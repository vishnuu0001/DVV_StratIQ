# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Robot service layer for managing robot operations, movements, and telemetry.
# Date: 2026-03-27
# ---------------------------------------------------------------------------
"""
Robot service layer for managing robot operations, movements, and telemetry.
Provides business logic for robot control and simulation.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
import math
import json

from models import (
    Robot, RobotType, RobotOperation, RobotMovement, RobotTelemetry,
    ProductionStation, ProductionTask, SimulationConfig, SimulationEvent,
    RobotCommand, MqttAcknowledgement, RackInventory, ConveyorInventory
)
from schemas import (
    RobotCreate, RobotUpdate, RobotOperationCreate, RobotSchema,
    RobotOperationSchema, RobotTelemetrySchema, RobotMovementSchema
)


class RobotService:
    """Service for managing robot operations and state."""

    # Function: create_robot
    @staticmethod
    def create_robot(db: Session, robot_create: RobotCreate) -> Robot:
        """Create a new robot instance."""
        # Verify robot type exists
        robot_type = db.query(RobotType).filter(
            RobotType.id == robot_create.robot_type_id
        ).first()
        if not robot_type:
            raise ValueError(f"Robot type {robot_create.robot_type_id} not found")

        db_robot = Robot(
            robot_id=robot_create.robot_id,
            robot_type_id=robot_create.robot_type_id,
            location_zone=robot_create.location_zone,
            position={"x": 0.0, "y": 0.0, "z": 0.0},
            orientation={"roll": 0.0, "pitch": 0.0, "yaw": 0.0},
        )
        db.add(db_robot)
        db.commit()
        db.refresh(db_robot)
        return db_robot

    # Function: get_robot
    @staticmethod
    def get_robot(db: Session, robot_id: int) -> Optional[Robot]:
        """Get a robot by ID."""
        return db.query(Robot).filter(Robot.id == robot_id).first()

    # Function: get_robot_by_robot_id
    @staticmethod
    def get_robot_by_robot_id(db: Session, robot_id: str) -> Optional[Robot]:
        """Get a robot by robot_id string."""
        return db.query(Robot).filter(Robot.robot_id == robot_id).first()

    # Function: list_robots
    @staticmethod
    def list_robots(db: Session, location_zone: Optional[str] = None, status: Optional[str] = None) -> List[Robot]:
        """List robots with optional filtering."""
        query = db.query(Robot)
        if location_zone:
            query = query.filter(Robot.location_zone == location_zone)
        if status:
            query = query.filter(Robot.status == status)
        return query.all()

    # Function: update_robot
    @staticmethod
    def update_robot(db: Session, robot_id: int, update_data: RobotUpdate) -> Optional[Robot]:
        """Update robot status and position."""
        robot = db.query(Robot).filter(Robot.id == robot_id).first()
        if not robot:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if value is not None:
                setattr(robot, key, value)

        robot.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(robot)
        return robot

    # Function: record_telemetry
    @staticmethod
    def record_telemetry(db: Session, robot_id: int, telemetry_data: Dict) -> RobotTelemetry:
        """Record robot telemetry data."""
        telemetry = RobotTelemetry(
            robot_id=robot_id,
            position=telemetry_data.get("position", {}),
            orientation=telemetry_data.get("orientation"),
            velocity=telemetry_data.get("velocity"),
            acceleration=telemetry_data.get("acceleration"),
            joint_angles=telemetry_data.get("joint_angles"),
            battery_level=telemetry_data.get("battery_level"),
            current_load=telemetry_data.get("current_load"),
            error_code=telemetry_data.get("error_code"),
            additional_metrics=telemetry_data.get("additional_metrics"),
        )
        db.add(telemetry)
        db.commit()
        db.refresh(telemetry)
        return telemetry

    # Function: get_robot_telemetry
    @staticmethod
    def get_robot_telemetry(db: Session, robot_id: int, limit: int = 100) -> List[RobotTelemetry]:
        """Get recent telemetry for a robot."""
        return db.query(RobotTelemetry).filter(
            RobotTelemetry.robot_id == robot_id
        ).order_by(RobotTelemetry.timestamp.desc()).limit(limit).all()

    # Function: create_operation
    @staticmethod
    def create_operation(db: Session, operation_create: RobotOperationCreate) -> RobotOperation:
        """Create a new robot operation/task."""
        # Generate operation_id
        last_op = db.query(RobotOperation).order_by(RobotOperation.id.desc()).first()
        op_num = (last_op.id if last_op else 0) + 1
        operation_id = f"OP-{op_num:06d}"

        db_operation = RobotOperation(
            operation_id=operation_id,
            robot_id=operation_create.robot_id,
            robot_type_id=operation_create.robot_type_id,
            operation_type=operation_create.operation_type,
            status="queued",
            start_position=operation_create.start_position,
            end_position=operation_create.end_position,
            estimated_duration=operation_create.estimated_duration,
            execution_metadata=operation_create.execution_metadata or {},
        )
        db.add(db_operation)
        db.commit()
        db.refresh(db_operation)
        return db_operation

    # Function: start_operation
    @staticmethod
    def start_operation(db: Session, operation_id: int) -> Optional[RobotOperation]:
        """Start executing a queued operation."""
        operation = db.query(RobotOperation).filter(RobotOperation.id == operation_id).first()
        if not operation or operation.status != "queued":
            return None

        operation.status = "executing"
        operation.start_time = datetime.utcnow()
        db.commit()
        db.refresh(operation)
        return operation

    # Function: complete_operation
    @staticmethod
    def complete_operation(db: Session, operation_id: int) -> Optional[RobotOperation]:
        """Mark an operation as completed."""
        operation = db.query(RobotOperation).filter(RobotOperation.id == operation_id).first()
        if not operation:
            return None

        operation.status = "completed"
        operation.end_time = datetime.utcnow()
        db.commit()
        db.refresh(operation)
        return operation

    # Function: fail_operation
    @staticmethod
    def fail_operation(db: Session, operation_id: int, error_msg: str = "") -> Optional[RobotOperation]:
        """Mark an operation as failed."""
        operation = db.query(RobotOperation).filter(RobotOperation.id == operation_id).first()
        if not operation:
            return None

        operation.status = "failed"
        operation.end_time = datetime.utcnow()
        if error_msg:
            operation.execution_metadata["error"] = error_msg
        db.commit()
        db.refresh(operation)
        return operation

    # Function: add_movement
    @staticmethod
    def add_movement(db: Session, operation_id: int, waypoint_index: int,
                     position: Dict, orientation: Optional[Dict] = None,
                     speed: Optional[float] = None) -> RobotMovement:
        """Add a movement waypoint to an operation."""
        movement = RobotMovement(
            operation_id=operation_id,
            waypoint_index=waypoint_index,
            position=position,
            orientation=orientation,
            speed=speed,
        )
        db.add(movement)
        db.commit()
        db.refresh(movement)
        return movement

    # Function: get_operation_movements
    @staticmethod
    def get_operation_movements(db: Session, operation_id: int) -> List[RobotMovement]:
        """Get all movements for an operation in order."""
        return db.query(RobotMovement).filter(
            RobotMovement.operation_id == operation_id
        ).order_by(RobotMovement.waypoint_index).all()


class SimulationService:
    """Service for managing robot simulation scenarios."""

    # Function: create_scenario
    @staticmethod
    def create_scenario(db: Session, config_id: str, scenario_type: str,
                       name: str, physics_enabled: bool = True) -> SimulationConfig:
        """Create a simulation scenario."""
        scenario = SimulationConfig(
            config_id=config_id,
            name=name,
            scenario_type=scenario_type,
            physics_enabled=physics_enabled,
            enabled=True,
        )
        db.add(scenario)
        db.commit()
        db.refresh(scenario)
        return scenario

    # Function: log_event
    @staticmethod
    def log_event(db: Session, config_id: int, event_type: str,
                  severity: str = "info", robot_id: Optional[str] = None,
                  description: Optional[str] = None, event_data: Optional[Dict] = None) -> SimulationEvent:
        """Log a simulation event."""
        # Generate event_id
        last_event = db.query(SimulationEvent).order_by(SimulationEvent.id.desc()).first()
        event_num = (last_event.id if last_event else 0) + 1
        event_id = f"EVT-{event_num:06d}"

        event = SimulationEvent(
            event_id=event_id,
            config_id=config_id,
            event_type=event_type,
            severity=severity,
            robot_id=robot_id,
            description=description,
            event_data=event_data or {},
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event


class CommandQueueService:
    """Service for robot command queueing, dispatch and acknowledgement processing."""

    TERMINAL_STATUSES = {"completed", "failed"}

    # Function: enqueue_command
    @staticmethod
    def enqueue_command(db: Session, command_data: Dict) -> RobotCommand:
        existing = db.query(RobotCommand).filter(
            RobotCommand.command_id == command_data["command_id"]
        ).first()
        if existing:
            return existing

        command = RobotCommand(
            command_id=command_data["command_id"],
            robot_id=command_data["robot_id"],
            command_type=command_data.get("command_type", "PICK_AND_PLACE"),
            rack_id=command_data.get("rack_id"),
            item_id=command_data.get("item_id"),
            conveyor_id=command_data.get("conveyor_id"),
            priority=command_data.get("priority", 1),
            payload=command_data.get("payload", {}),
            source=command_data.get("source", "api"),
            status="queued",
        )
        db.add(command)
        db.commit()
        db.refresh(command)
        return command

    # Function: list_robot_queue
    @staticmethod
    def list_robot_queue(db: Session, robot_id: str) -> List[RobotCommand]:
        return db.query(RobotCommand).filter(
            RobotCommand.robot_id == robot_id
        ).order_by(
            RobotCommand.status.asc(),
            RobotCommand.priority.desc(),
            RobotCommand.created_at.asc(),
        ).all()

    # Function: get_next_queued_command
    @staticmethod
    def get_next_queued_command(db: Session, robot_id: str) -> Optional[RobotCommand]:
        return db.query(RobotCommand).filter(
            RobotCommand.robot_id == robot_id,
            RobotCommand.status == "queued",
        ).order_by(
            RobotCommand.priority.desc(),
            RobotCommand.created_at.asc(),
        ).first()

    # Function: get_active_command
    @staticmethod
    def get_active_command(db: Session, robot_id: str) -> Optional[RobotCommand]:
        return db.query(RobotCommand).filter(
            RobotCommand.robot_id == robot_id,
            RobotCommand.status.in_(["dispatched", "executing"]),
        ).order_by(RobotCommand.created_at.asc()).first()

    # Function: dispatch_if_idle
    @staticmethod
    def dispatch_if_idle(db: Session, robot_id: str) -> Optional[RobotCommand]:
        active = CommandQueueService.get_active_command(db, robot_id)
        if active:
            return None

        next_cmd = CommandQueueService.get_next_queued_command(db, robot_id)
        if not next_cmd:
            return None

        next_cmd.status = "dispatched"
        next_cmd.dispatched_at = datetime.utcnow()
        db.commit()
        db.refresh(next_cmd)
        return next_cmd

    # Function: persist_ack
    @staticmethod
    def persist_ack(db: Session, topic: str, payload: Dict) -> MqttAcknowledgement:
        ack = MqttAcknowledgement(
            topic=topic,
            command_id=payload.get("commandId") or payload.get("command_id"),
            robot_id=payload.get("robotId") or payload.get("robot_id"),
            status=payload.get("status"),
            rack_id=payload.get("rackId") or payload.get("rack_id"),
            conveyor_id=payload.get("conveyorId") or payload.get("conveyor_id"),
            item_id=payload.get("itemId") or payload.get("item_id"),
            payload=payload,
        )
        db.add(ack)
        db.commit()
        db.refresh(ack)
        return ack

    # Function: apply_ack_to_command
    @staticmethod
    def apply_ack_to_command(db: Session, ack_payload: Dict) -> Optional[RobotCommand]:
        command_id = ack_payload.get("commandId") or ack_payload.get("command_id")
        if not command_id:
            return None

        command = db.query(RobotCommand).filter(
            RobotCommand.command_id == command_id
        ).first()
        if not command:
            return None

        status = (ack_payload.get("status") or "").lower()
        if status in {"accepted", "received", "arrived_rack", "scan_started", "scan_complete", "picked", "arrived_conveyor", "placed_on_conveyor"}:
            command.status = "executing"
        elif status in {"completed"}:
            command.status = "completed"
            command.completed_at = datetime.utcnow()
            CommandQueueService._apply_inventory_transfer(
                db,
                rack_id=command.rack_id,
                conveyor_id=command.conveyor_id,
                item_id=command.item_id,
            )
        elif status in {"failed", "rejected"}:
            command.status = "failed"
            command.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(command)
        return command

    # Function: _apply_inventory_transfer
    @staticmethod
    def _apply_inventory_transfer(db: Session, rack_id: Optional[str], conveyor_id: Optional[str], item_id: Optional[str]) -> None:
        if not rack_id or not conveyor_id or not item_id:
            return

        rack = db.query(RackInventory).filter(
            RackInventory.rack_id == rack_id,
            RackInventory.item_id == item_id,
        ).first()
        if not rack:
            rack = RackInventory(rack_id=rack_id, item_id=item_id, quantity=0)
            db.add(rack)
            db.flush()

        if rack.quantity > 0:
            rack.quantity -= 1

        conveyor = db.query(ConveyorInventory).filter(
            ConveyorInventory.conveyor_id == conveyor_id,
            ConveyorInventory.item_id == item_id,
        ).first()
        if not conveyor:
            conveyor = ConveyorInventory(conveyor_id=conveyor_id, item_id=item_id, quantity=0)
            db.add(conveyor)
            db.flush()

        conveyor.quantity += 1
        db.commit()

    # Function: list_acknowledgements
    @staticmethod
    def list_acknowledgements(db: Session, limit: int = 200) -> List[MqttAcknowledgement]:
        return db.query(MqttAcknowledgement).order_by(
            MqttAcknowledgement.received_at.desc()
        ).limit(limit).all()

    # Function: list_rack_inventory
    @staticmethod
    def list_rack_inventory(db: Session) -> List[RackInventory]:
        return db.query(RackInventory).order_by(RackInventory.rack_id.asc()).all()

    # Function: list_conveyor_inventory
    @staticmethod
    def list_conveyor_inventory(db: Session) -> List[ConveyorInventory]:
        return db.query(ConveyorInventory).order_by(ConveyorInventory.conveyor_id.asc()).all()


class PathPlanningService:
    """Service for robot path planning and collision detection."""

    # Function: calculate_path
    @staticmethod
    def calculate_path(start: Dict, end: Dict, obstacles: List[Dict] = None) -> List[Dict]:
        """
        Calculate a path between two points, avoiding obstacles.
        Returns list of waypoints.
        """
        obstacles = obstacles or []
        waypoints = [start]

        # Simple linear interpolation for now
        # In production, use RRT or A* for complex environments
        distance = PathPlanningService.distance_3d(start, end)
        if distance < 0.01:
            return waypoints

        steps = max(2, int(distance * 10))
        for i in range(1, steps):
            t = i / steps
            waypoint = {
                "x": start["x"] + (end["x"] - start["x"]) * t,
                "y": start["y"] + (end["y"] - start["y"]) * t,
                "z": start["z"] + (end["z"] - start["z"]) * t,
            }
            waypoints.append(waypoint)

        waypoints.append(end)
        return waypoints

    # Function: distance_3d
    @staticmethod
    def distance_3d(p1: Dict, p2: Dict) -> float:
        """Calculate 3D Euclidean distance."""
        dx = p2.get("x", 0) - p1.get("x", 0)
        dy = p2.get("y", 0) - p1.get("y", 0)
        dz = p2.get("z", 0) - p1.get("z", 0)
        return math.sqrt(dx**2 + dy**2 + dz**2)

    # Function: check_collision
    @staticmethod
    def check_collision(pos1: Dict, pos2: Dict, obstacle: Dict, radius: float = 0.5) -> bool:
        """Check if line segment between pos1 and pos2 collides with obstacle."""
        # Simple sphere collision check
        obs_pos = obstacle.get("position", {})
        obs_radius = obstacle.get("radius", 0.5)

        # Distance from obstacle center to line segment
        dist = PathPlanningService._point_to_segment_distance(
            obs_pos, pos1, pos2
        )
        return dist < (radius + obs_radius)

    # Function: _point_to_segment_distance
    @staticmethod
    def _point_to_segment_distance(point: Dict, seg_start: Dict, seg_end: Dict) -> float:
        """Calculate distance from point to line segment."""
        x, y, z = point.get("x", 0), point.get("y", 0), point.get("z", 0)
        x1, y1, z1 = seg_start.get("x", 0), seg_start.get("y", 0), seg_start.get("z", 0)
        x2, y2, z2 = seg_end.get("x", 0), seg_end.get("y", 0), seg_end.get("z", 0)

        dx = x2 - x1
        dy = y2 - y1
        dz = z2 - z1
        length_sq = dx**2 + dy**2 + dz**2

        if length_sq == 0:
            return math.sqrt((x - x1)**2 + (y - y1)**2 + (z - z1)**2)

        t = max(0, min(1, ((x - x1)*dx + (y - y1)*dy + (z - z1)*dz) / length_sq))
        proj_x = x1 + t * dx
        proj_y = y1 + t * dy
        proj_z = z1 + t * dz

        return math.sqrt((x - proj_x)**2 + (y - proj_y)**2 + (z - proj_z)**2)
