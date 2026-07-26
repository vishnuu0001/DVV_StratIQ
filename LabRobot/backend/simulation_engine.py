# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Real-time Physics-based Robot Simulation Engine.
# Date: 2026-03-02
# ---------------------------------------------------------------------------
"""
Real-time Physics-based Robot Simulation Engine.
Handles simulation state updates, collision detection, and event generation.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import math
import json

from sqlalchemy.orm import Session
from models import Robot, RobotType, SimulationConfig


class RobotState(Enum):
    """Enumeration of robot operational states."""
    IDLE = "idle"
    MOVING = "moving"
    WORKING = "working"
    CHARGING = "charging"
    ERROR = "error"
    PAUSED = "paused"


@dataclass
class Vector3D:
    """3D vector for positions and velocities."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    # Function: __add__
    def __add__(self, other):
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    # Function: __sub__
    def __sub__(self, other):
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    # Function: __mul__
    def __mul__(self, scalar):
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)

    # Function: magnitude
    def magnitude(self) -> float:
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    # Function: normalize
    def normalize(self):
        mag = self.magnitude()
        if mag > 0:
            return Vector3D(self.x/mag, self.y/mag, self.z/mag)
        return self

    # Function: to_dict
    def to_dict(self) -> Dict:
        return {"x": self.x, "y": self.y, "z": self.z}

    # Function: from_dict
    @classmethod
    def from_dict(cls, d: Dict):
        return cls(d.get("x", 0), d.get("y", 0), d.get("z", 0))


@dataclass
class RobotPhysics:
    """Physics properties for a robot."""
    mass: float = 100.0  # kg
    max_velocity: float = 2.0  # m/s
    max_acceleration: float = 1.0  # m/s^2
    friction: float = 0.1
    collision_radius: float = 0.5  # meters


@dataclass
class SimulationRobot:
    """In-memory robot state for simulation."""
    robot_id: str
    position: Vector3D = field(default_factory=lambda: Vector3D())
    velocity: Vector3D = field(default_factory=lambda: Vector3D())
    acceleration: Vector3D = field(default_factory=lambda: Vector3D())
    orientation: Dict = field(default_factory=lambda: {"roll": 0.0, "pitch": 0.0, "yaw": 0.0})
    status: RobotState = RobotState.IDLE
    current_target: Optional[Vector3D] = None
    current_load: float = 0.0
    battery_level: float = 100.0
    battery_drain_rate: float = 0.05  # % per second when moving
    physics: RobotPhysics = field(default_factory=RobotPhysics)
    error_code: Optional[str] = None
    last_update_time: float = 0.0

    # Function: to_dict
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            "robot_id": self.robot_id,
            "position": self.position.to_dict(),
            "velocity": self.velocity.to_dict(),
            "acceleration": self.acceleration.to_dict(),
            "orientation": self.orientation,
            "status": self.status.value,
            "current_load": self.current_load,
            "battery_level": self.battery_level,
            "error_code": self.error_code,
        }


class PhysicsEngine:
    """Handles physics calculations for robot movements."""

    # Gravity constant (for VR/AR applications)
    GRAVITY = 9.81  # m/s^2

    # Function: update_position
    @staticmethod
    def update_position(robot: SimulationRobot, delta_time: float, obstacles: List[Dict] = None) -> bool:
        """
        Update robot position based on physics.
        Returns True if collision detected.
        """
        obstacles = obstacles or []

        # Update velocity based on acceleration (simplified Newton's laws)
        robot.velocity = robot.velocity + robot.acceleration * delta_time

        # Clamp velocity to max
        vel_mag = robot.velocity.magnitude()
        if vel_mag > robot.physics.max_velocity:
            robot.velocity = robot.velocity.normalize() * robot.physics.max_velocity

        # Apply friction
        if vel_mag > 0:
            friction_decel = robot.physics.friction
            robot.velocity = robot.velocity * (1 - friction_decel * delta_time)

        # New position
        new_pos = robot.position + robot.velocity * delta_time

        # Collision detection
        collision = False
        for obstacle in obstacles:
            if PhysicsEngine._check_sphere_collision(
                new_pos, robot.physics.collision_radius,
                obstacle.get("position", {x: 0, y: 0, z: 0}),
                obstacle.get("radius", 0.5)
            ):
                collision = True
                break

        if not collision:
            robot.position = new_pos
        else:
            robot.velocity = Vector3D()  # Stop movement
            robot.status = RobotState.ERROR
            robot.error_code = "COLLISION_DETECTED"

        # Battery drain
        if robot.status in [RobotState.MOVING, RobotState.WORKING]:
            battery_delta = robot.physics.battery_drain_rate * delta_time
            robot.battery_level = max(0, robot.battery_level - battery_delta)

            if robot.battery_level <= 0:
                robot.status = RobotState.CHARGING
                robot.velocity = Vector3D()

        return collision

    # Function: move_to_target
    @staticmethod
    def move_to_target(robot: SimulationRobot, target: Vector3D, delta_time: float):
        """Calculate movement towards target."""
        if not robot.current_target:
            robot.current_target = target

        direction = (target - robot.position).normalize()
        distance = (target - robot.position).magnitude()

        if distance < 0.1:
            # Reached target
            robot.current_target = None
            robot.velocity = Vector3D()
            robot.acceleration = Vector3D()
            robot.status = RobotState.IDLE
            return True

        # Accelerate towards target
        robot.acceleration = direction * robot.physics.max_acceleration
        robot.status = RobotState.MOVING
        return False

    # Function: _check_sphere_collision
    @staticmethod
    def _check_sphere_collision(pos1: Vector3D, rad1: float, pos2: Dict, rad2: float) -> bool:
        """Check if two spheres collide."""
        center2 = Vector3D.from_dict(pos2)
        distance = (pos1 - center2).magnitude()
        return distance < (rad1 + rad2)


class SimulationScenario:
    """Manages a complete simulation scenario with multiple robots."""

    # Function: __init__
    def __init__(self, config_id: str, scenario_type: str, time_scale: float = 1.0):
        self.config_id = config_id
        self.scenario_type = scenario_type
        self.time_scale = time_scale  # 1.0 = real-time, 2.0 = 2x speed
        self.robots: Dict[str, SimulationRobot] = {}
        self.obstacles: List[Dict] = []
        self.events: List[Dict] = []
        self.simulation_time: float = 0.0
        self.is_running: bool = False
        self.physics_enabled: bool = True

    # Function: add_robot
    def add_robot(self, robot: SimulationRobot):
        """Add a robot to the simulation."""
        self.robots[robot.robot_id] = robot

    # Function: add_obstacle
    def add_obstacle(self, obstacle_id: str, position: Dict, radius: float = 0.5):
        """Add a static obstacle to the scenario."""
        self.obstacles.append({
            "id": obstacle_id,
            "position": position,
            "radius": radius,
        })

    # Function: update
    def update(self, delta_time: float):
        """Update simulation state."""
        if not self.is_running:
            return

        # Apply time scale
        scaled_delta = delta_time * self.time_scale

        for robot in self.robots.values():
            if self.physics_enabled and robot.status != RobotState.IDLE:
                collision = PhysicsEngine.update_position(robot, scaled_delta, self.obstacles)

                if collision:
                    self._log_event(
                        event_type="collision",
                        severity="error",
                        robot_id=robot.robot_id,
                        description=f"Robot {robot.robot_id} collided with obstacle"
                    )

            # Update battery if charging
            if robot.status == RobotState.CHARGING:
                robot.battery_level = min(100.0, robot.battery_level + 0.3 * scaled_delta)
                if robot.battery_level >= 100.0:
                    robot.status = RobotState.IDLE
                    robot.battery_level = 100.0

        self.simulation_time += scaled_delta

    # Function: move_robot_to
    def move_robot_to(self, robot_id: str, target: Dict) -> bool:
        """Command robot to move to target."""
        robot = self.robots.get(robot_id)
        if not robot or robot.battery_level <= 0:
            return False

        target_vec = Vector3D.from_dict(target)
        robot.current_target = target_vec
        robot.status = RobotState.MOVING
        return True

    # Function: perform_operation
    def perform_operation(self, robot_id: str, operation_type: str, duration: float) -> bool:
        """Command robot to perform an operation."""
        robot = self.robots.get(robot_id)
        if not robot or robot.battery_level <= 0:
            return False

        robot.status = RobotState.WORKING
        return True

    # Function: _log_event
    def _log_event(self, event_type: str, severity: str = "info",
                   robot_id: Optional[str] = None, description: Optional[str] = None):
        """Log a simulation event."""
        event = {
            "type": event_type,
            "severity": severity,
            "robot_id": robot_id,
            "description": description,
            "timestamp": self.simulation_time,
        }
        self.events.append(event)

    # Function: get_state_snapshot
    def get_state_snapshot(self) -> Dict:
        """Get current state of all robots."""
        return {
            "config_id": self.config_id,
            "scenario_type": self.scenario_type,
            "simulation_time": self.simulation_time,
            "robots": {rid: r.to_dict() for rid, r in self.robots.items()},
            "obstacles": self.obstacles,
            "events": self.events[-10:],  # Last 10 events
        }


# ─── Scenario Templates ──────────────────────────────────────────────────────

class ScenarioFactory:
    """Factory for creating predefined simulation scenarios."""

    # Function: create_production_scenario
    @staticmethod
    def create_production_scenario() -> SimulationScenario:
        """Create a production/assembly line scenario."""
        scenario = SimulationScenario("PROD-001", "production")

        # Add workstations as obstacles
        stations = [
            {"id": "STATION-1", "position": {"x": 0, "y": 0, "z": 0}, "radius": 1.0},
            {"id": "STATION-2", "position": {"x": 5, "y": 0, "z": 0}, "radius": 1.0},
            {"id": "STATION-3", "position": {"x": 10, "y": 0, "z": 0}, "radius": 1.0},
        ]

        for station in stations:
            scenario.add_obstacle(station["id"], station["position"], station["radius"])

        return scenario

    # Function: create_warehouse_scenario
    @staticmethod
    def create_warehouse_scenario() -> SimulationScenario:
        """Create a warehouse/intralogistics scenario."""
        scenario = SimulationScenario("WH-001", "intralogistics")

        # Add storage racks as obstacles
        for row in range(3):
            for col in range(3):
                scenario.add_obstacle(
                    f"RACK-{row}-{col}",
                    {"x": col * 3, "y": row * 3, "z": 0},
                    0.8
                )

        return scenario

    # Function: create_inspection_scenario
    @staticmethod
    def create_inspection_scenario() -> SimulationScenario:
        """Create a quality inspection scenario."""
        scenario = SimulationScenario("QI-001", "quality_inspection")

        # Add inspection stations
        scenario.add_obstacle(
            "INSPECTION-BOOTH",
            {"x": 5, "y": 5, "z": 1},
            1.5
        )

        return scenario
