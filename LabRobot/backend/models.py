# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: LabRobot — backend (models.py)
# Date: 2026-03-12
# ---------------------------------------------------------------------------
import datetime
import json
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, JSON, Text
from sqlalchemy.orm import relationship
from database import Base


# ─── Legacy Chemical Lab Models ──────────────────────────────────────────────
class Scientist(Base):
    __tablename__ = "scientists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    code = Column(String, unique=True, nullable=False)

    racks = relationship("Rack", back_populates="scientist")
    placements = relationship("Placement", back_populates="scientist")


class Rack(Base):
    __tablename__ = "racks"

    id = Column(Integer, primary_key=True, index=True)
    barcode = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    scientist_id = Column(Integer, ForeignKey("scientists.id"), nullable=False)

    scientist = relationship("Scientist", back_populates="racks")
    placements = relationship("Placement", back_populates="rack")


class ChemicalCatalog(Base):
    __tablename__ = "chemical_catalog"

    id = Column(Integer, primary_key=True, index=True)
    barcode = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    placements = relationship("Placement", back_populates="chemical")


class Placement(Base):
    __tablename__ = "placements"

    id = Column(Integer, primary_key=True, index=True)
    chemical_id = Column(Integer, ForeignKey("chemical_catalog.id"), nullable=False)
    rack_id = Column(Integer, ForeignKey("racks.id"), nullable=False)
    scientist_id = Column(Integer, ForeignKey("scientists.id"), nullable=False)
    compartment = Column(Integer, nullable=False, default=1)
    status = Column(String, default="Placed", nullable=False)
    placed_at = Column(DateTime, default=datetime.datetime.utcnow)
    fetched_at = Column(DateTime, nullable=True)

    chemical = relationship("ChemicalCatalog", back_populates="placements")
    rack = relationship("Rack", back_populates="placements")
    scientist = relationship("Scientist", back_populates="placements")


# ─── Production Robot Models ─────────────────────────────────────────────────

class RobotType(Base):
    """Robot type definitions: Welding, Assembly, AMR, Inspection, etc."""
    __tablename__ = "robot_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # e.g., "Welding", "AMR", "Vision Inspection"
    category = Column(String, nullable=False)  # e.g., "production", "intralogistics", "quality"
    description = Column(Text, nullable=True)
    max_speed = Column(Float, default=1.0)  # m/s
    payload_capacity = Column(Float, default=50.0)  # kg
    reach = Column(Float, nullable=True)  # mm for articulated robots
    dof = Column(Integer, nullable=True)  # degrees of freedom
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    robots = relationship("Robot", back_populates="robot_type")
    operations = relationship("RobotOperation", back_populates="robot_type")


class Robot(Base):
    """Individual robot instances on the production floor."""
    __tablename__ = "robots"

    id = Column(Integer, primary_key=True, index=True)
    robot_id = Column(String, unique=True, nullable=False)  # e.g., "ROB-001"
    robot_type_id = Column(Integer, ForeignKey("robot_types.id"), nullable=False)
    status = Column(String, default="idle")  # idle, moving, working, charging, error
    position = Column(JSON, default=lambda: {"x": 0, "y": 0, "z": 0})  # 3D position
    orientation = Column(JSON, default=lambda: {"roll": 0, "pitch": 0, "yaw": 0})
    current_load = Column(Float, default=0.0)  # kg
    battery_level = Column(Float, default=100.0)  # percentage
    current_task_id = Column(Integer, ForeignKey("robot_operations.id"), nullable=True)
    location_zone = Column(String, nullable=True)  # e.g., "Assembly Line 1", "Warehouse A"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    robot_type = relationship("RobotType", back_populates="robots")
    operations = relationship("RobotOperation", back_populates="robot", foreign_keys="RobotOperation.robot_id")
    telemetry = relationship("RobotTelemetry", back_populates="robot")


class RobotOperation(Base):
    """Tasks/operations performed by robots."""
    __tablename__ = "robot_operations"

    id = Column(Integer, primary_key=True, index=True)
    operation_id = Column(String, unique=True, nullable=False)  # e.g., "OP-001"
    robot_id = Column(Integer, ForeignKey("robots.id"), nullable=False)
    robot_type_id = Column(Integer, ForeignKey("robot_types.id"), nullable=False)
    operation_type = Column(String, nullable=False)  # e.g., "weld", "assemble", "transport", "inspect"
    status = Column(String, default="queued")  # queued, executing, paused, completed, failed
    start_position = Column(JSON, nullable=True)
    end_position = Column(JSON, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    estimated_duration = Column(Float, nullable=True)  # seconds
    execution_metadata = Column(JSON, default=dict)  # Additional operation-specific data
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    robot = relationship("Robot", back_populates="operations", foreign_keys=[robot_id])
    robot_type = relationship("RobotType", back_populates="operations")
    movements = relationship("RobotMovement", back_populates="operation")


class RobotMovement(Base):
    """Tracks robot movement waypoints during operations."""
    __tablename__ = "robot_movements"

    id = Column(Integer, primary_key=True, index=True)
    operation_id = Column(Integer, ForeignKey("robot_operations.id"), nullable=False)
    waypoint_index = Column(Integer, nullable=False)
    position = Column(JSON, nullable=False)  # {"x": float, "y": float, "z": float}
    orientation = Column(JSON, nullable=True)
    speed = Column(Float, nullable=True)  # m/s
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    operation = relationship("RobotOperation", back_populates="movements")


class RobotTelemetry(Base):
    """Real-time telemetry data from robots."""
    __tablename__ = "robot_telemetry"

    id = Column(Integer, primary_key=True, index=True)
    robot_id = Column(Integer, ForeignKey("robots.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    position = Column(JSON, nullable=False)
    orientation = Column(JSON, nullable=True)
    velocity = Column(JSON, nullable=True)  # {"vx": float, "vy": float, "vz": float}
    acceleration = Column(JSON, nullable=True)
    joint_angles = Column(JSON, nullable=True)  # For articulated robots
    battery_level = Column(Float, nullable=True)
    current_load = Column(Float, nullable=True)
    error_code = Column(String, nullable=True)
    additional_metrics = Column(JSON, nullable=True)

    robot = relationship("Robot", back_populates="telemetry")


class ProductionStation(Base):
    """Physical workstations/zones in the production floor."""
    __tablename__ = "production_stations"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(String, unique=True, nullable=False)  # e.g., "STATION-001"
    name = Column(String, nullable=False)
    station_type = Column(String, nullable=False)  # e.g., "welding", "assembly", "inspection", "warehouse"
    position = Column(JSON, default=lambda: {"x": 0, "y": 0, "z": 0})
    dimensions = Column(JSON, default=lambda: {"length": 2.0, "width": 2.0, "height": 2.0})
    status = Column(String, default="operational")  # operational, maintenance, offline
    assigned_robots = Column(JSON, default=list)  # List of robot IDs
    queue_count = Column(Integer, default=0)
    throughput = Column(Float, default=0.0)  # items per hour
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    tasks = relationship("ProductionTask", back_populates="station")


class ProductionTask(Base):
    """Production line tasks/jobs."""
    __tablename__ = "production_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, nullable=False)  # e.g., "TASK-001"
    station_id = Column(Integer, ForeignKey("production_stations.id"), nullable=False)
    task_type = Column(String, nullable=False)  # e.g., "weld", "assemble"
    status = Column(String, default="pending")  # pending, assigned, executing, completed, failed
    assigned_robot_id = Column(Integer, ForeignKey("robots.id"), nullable=True)
    priority = Column(Integer, default=1)
    estimated_duration = Column(Float, nullable=True)
    actual_duration = Column(Float, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    station = relationship("ProductionStation", back_populates="tasks")


class SimulationConfig(Base):
    """Configuration for real-time simulation scenarios."""
    __tablename__ = "simulation_configs"

    id = Column(Integer, primary_key=True, index=True)
    config_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    scenario_type = Column(String, nullable=False)  # e.g., "production", "intralogistics", "quality"
    enabled = Column(Integer, default=1)
    physics_enabled = Column(Integer, default=1)
    time_scale = Column(Float, default=1.0)  # 1.0 = real-time
    config_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    events = relationship("SimulationEvent", back_populates="config")


class SimulationEvent(Base):
    """Events that occur during simulation (collisions, completions, errors)."""
    __tablename__ = "simulation_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, nullable=False)
    config_id = Column(Integer, ForeignKey("simulation_configs.id"), nullable=False)
    event_type = Column(String, nullable=False)  # e.g., "collision", "task_completed", "robot_error"
    severity = Column(String, default="info")  # info, warning, error, critical
    robot_id = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    event_data = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    config = relationship("SimulationConfig", back_populates="events")


class RobotCommand(Base):
    """Queued robot commands received from external systems (MQTT/API)."""
    __tablename__ = "robot_commands"

    id = Column(Integer, primary_key=True, index=True)
    command_id = Column(String, unique=True, nullable=False, index=True)
    robot_id = Column(String, nullable=False, index=True)
    command_type = Column(String, nullable=False, default="PICK_AND_PLACE")
    rack_id = Column(String, nullable=True)
    item_id = Column(String, nullable=True)
    conveyor_id = Column(String, nullable=True)
    priority = Column(Integer, default=1)
    status = Column(String, default="queued", index=True)  # queued, dispatched, executing, completed, failed
    source = Column(String, default="api")  # api, mqtt, bridge
    payload = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    dispatched_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)


class MqttAcknowledgement(Base):
    """Raw MQTT acknowledgements persisted for audit and replay."""
    __tablename__ = "mqtt_acknowledgements"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, nullable=False, index=True)
    command_id = Column(String, nullable=True, index=True)
    robot_id = Column(String, nullable=True, index=True)
    status = Column(String, nullable=True, index=True)
    rack_id = Column(String, nullable=True)
    conveyor_id = Column(String, nullable=True)
    item_id = Column(String, nullable=True)
    payload = Column(JSON, default=dict)
    received_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)


class RackInventory(Base):
    """Inventory count by rack/item for robotics pick workflows."""
    __tablename__ = "rack_inventory"

    id = Column(Integer, primary_key=True, index=True)
    rack_id = Column(String, nullable=False, index=True)
    item_id = Column(String, nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class ConveyorInventory(Base):
    """Inventory count by conveyor/item for placed goods tracking."""
    __tablename__ = "conveyor_inventory"

    id = Column(Integer, primary_key=True, index=True)
    conveyor_id = Column(String, nullable=False, index=True)
    item_id = Column(String, nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
