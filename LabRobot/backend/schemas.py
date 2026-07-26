# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: LabRobot — backend (schemas.py)
# Date: 2025-12-04
# ---------------------------------------------------------------------------
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


# ─── Legacy Chemical Lab Schemas ────────────────────────────────────────────
class RackSchema(BaseModel):
    id: int
    barcode: str
    name: str
    scientist_id: int

    model_config = {"from_attributes": True}


class ScientistSchema(BaseModel):
    id: int
    name: str
    code: str
    racks: List[RackSchema] = []

    model_config = {"from_attributes": True}


class ChemicalCatalogSchema(BaseModel):
    id: int
    barcode: str
    name: str
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class PlacementCreate(BaseModel):
    chemical_barcode: str
    rack_id: int
    scientist_id: int
    compartment: int = Field(ge=1, le=3)


class PlacementSchema(BaseModel):
    id: int
    chemical_id: int
    rack_id: int
    scientist_id: int
    compartment: int
    status: str
    placed_at: datetime
    fetched_at: Optional[datetime] = None
    chemical: ChemicalCatalogSchema
    rack: RackSchema
    message: Optional[str] = None

    model_config = {"from_attributes": True}


# ─── Production Robot Schemas ───────────────────────────────────────────────

class RobotTypeSchema(BaseModel):
    id: int
    name: str
    category: str
    description: Optional[str] = None
    max_speed: float
    payload_capacity: float
    reach: Optional[float] = None
    dof: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RobotTypeCreate(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    max_speed: float = 1.0
    payload_capacity: float = 50.0
    reach: Optional[float] = None
    dof: Optional[int] = None


class RobotTelemetrySchema(BaseModel):
    id: int
    robot_id: int
    timestamp: datetime
    position: Dict[str, float]
    orientation: Optional[Dict[str, float]] = None
    velocity: Optional[Dict[str, float]] = None
    acceleration: Optional[Dict[str, float]] = None
    joint_angles: Optional[Dict[str, float]] = None
    battery_level: Optional[float] = None
    current_load: Optional[float] = None
    error_code: Optional[str] = None
    additional_metrics: Optional[Dict[str, Any]] = None

    model_config = {"from_attributes": True}


class RobotSchema(BaseModel):
    id: int
    robot_id: str
    robot_type_id: int
    status: str
    position: Dict[str, float]
    orientation: Dict[str, float]
    current_load: float
    battery_level: float
    current_task_id: Optional[int] = None
    location_zone: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RobotCreate(BaseModel):
    robot_id: str
    robot_type_id: int
    location_zone: Optional[str] = None


class RobotUpdate(BaseModel):
    status: Optional[str] = None
    position: Optional[Dict[str, float]] = None
    orientation: Optional[Dict[str, float]] = None
    current_load: Optional[float] = None
    battery_level: Optional[float] = None
    location_zone: Optional[str] = None


class RobotMovementSchema(BaseModel):
    id: int
    operation_id: int
    waypoint_index: int
    position: Dict[str, float]
    orientation: Optional[Dict[str, float]] = None
    speed: Optional[float] = None
    timestamp: datetime

    model_config = {"from_attributes": True}


class RobotOperationSchema(BaseModel):
    id: int
    operation_id: str
    robot_id: int
    robot_type_id: int
    operation_type: str
    status: str
    start_position: Optional[Dict[str, float]] = None
    end_position: Optional[Dict[str, float]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    estimated_duration: Optional[float] = None
    execution_metadata: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class RobotOperationCreate(BaseModel):
    robot_id: int
    robot_type_id: int
    operation_type: str
    start_position: Dict[str, float]
    end_position: Dict[str, float]
    estimated_duration: Optional[float] = None
    execution_metadata: Optional[Dict[str, Any]] = None


class ProductionStationSchema(BaseModel):
    id: int
    station_id: str
    name: str
    station_type: str
    position: Dict[str, float]
    dimensions: Dict[str, float]
    status: str
    assigned_robots: List[str]
    queue_count: int
    throughput: float
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductionStationCreate(BaseModel):
    station_id: str
    name: str
    station_type: str
    position: Optional[Dict[str, float]] = None
    dimensions: Optional[Dict[str, float]] = None


class ProductionTaskSchema(BaseModel):
    id: int
    task_id: str
    station_id: int
    task_type: str
    status: str
    assigned_robot_id: Optional[int] = None
    priority: int
    estimated_duration: Optional[float] = None
    actual_duration: Optional[float] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductionTaskCreate(BaseModel):
    task_id: str
    station_id: int
    task_type: str
    priority: int = 1
    estimated_duration: Optional[float] = None


class SimulationConfigSchema(BaseModel):
    id: int
    config_id: str
    name: str
    scenario_type: str
    enabled: bool
    physics_enabled: bool
    time_scale: float
    config_data: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class SimulationConfigCreate(BaseModel):
    config_id: str
    name: str
    scenario_type: str
    enabled: bool = True
    physics_enabled: bool = True
    time_scale: float = 1.0
    config_data: Optional[Dict[str, Any]] = None


class SimulationEventSchema(BaseModel):
    id: int
    event_id: str
    config_id: int
    event_type: str
    severity: str
    robot_id: Optional[str] = None
    description: Optional[str] = None
    event_data: Dict[str, Any]
    timestamp: datetime

    model_config = {"from_attributes": True}


class RobotCommandCreate(BaseModel):
    command_id: str
    robot_id: str
    command_type: str = "PICK_AND_PLACE"
    rack_id: Optional[str] = None
    item_id: Optional[str] = None
    conveyor_id: Optional[str] = None
    priority: int = 1
    payload: Optional[Dict[str, Any]] = None
    source: str = "api"


class RobotCommandSchema(BaseModel):
    id: int
    command_id: str
    robot_id: str
    command_type: str
    rack_id: Optional[str] = None
    item_id: Optional[str] = None
    conveyor_id: Optional[str] = None
    priority: int
    status: str
    source: str
    payload: Dict[str, Any]
    created_at: datetime
    dispatched_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class MqttAcknowledgementSchema(BaseModel):
    id: int
    topic: str
    command_id: Optional[str] = None
    robot_id: Optional[str] = None
    status: Optional[str] = None
    rack_id: Optional[str] = None
    conveyor_id: Optional[str] = None
    item_id: Optional[str] = None
    payload: Dict[str, Any]
    received_at: datetime

    model_config = {"from_attributes": True}


class InventorySchema(BaseModel):
    location_type: str
    location_id: str
    item_id: str
    quantity: int
    updated_at: datetime
