# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: LabRobot — backend (main.py)
# Date: 2026-06-13
# ---------------------------------------------------------------------------
import asyncio
import datetime
import json
import os
import urllib.error
import urllib.request
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from sqlalchemy import text

from auth import (
    LABROBOT_APP, auth_required, decode_access_token, decode_token_for_refresh,
    extract_bearer_token, validate_portal_session,
)

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

from database import engine, get_db, Base, SessionLocal
from models import (
    Scientist, Rack, ChemicalCatalog, Placement,
    RobotType, Robot, RobotOperation, ProductionStation,
    SimulationConfig, RobotCommand, RackInventory, ConveyorInventory
)
from schemas import (
    ScientistSchema,
    ChemicalCatalogSchema,
    PlacementCreate,
    PlacementSchema,
    RobotTypeSchema, RobotTypeCreate,
    RobotSchema, RobotCreate, RobotUpdate,
    RobotOperationSchema, RobotOperationCreate,
    ProductionStationSchema, ProductionStationCreate,
    SimulationConfigSchema, SimulationConfigCreate,
    RobotCommandSchema, RobotCommandCreate,
    MqttAcknowledgementSchema, InventorySchema,
)
from robot_service import RobotService, SimulationService, PathPlanningService, CommandQueueService
from simulation_engine import ScenarioFactory, SimulationScenario
from mqtt_bridge import BackendMqttBridge

Base.metadata.create_all(bind=engine)
mqtt_bridge = BackendMqttBridge()


# Function: _dispatch_next_for_robot
def _dispatch_next_for_robot(robot_id: str) -> dict | None:
    db = SessionLocal()
    try:
        next_command = CommandQueueService.dispatch_if_idle(db, robot_id)
        if not next_command:
            return None

        command_payload = {
            "command": next_command.command_type,
            "commandId": next_command.command_id,
            "robotId": next_command.robot_id,
            "rackId": next_command.rack_id,
            "itemId": next_command.item_id,
            "conveyorId": next_command.conveyor_id,
            **(next_command.payload or {}),
        }
        mqtt_bridge.publish_command(command_payload)
        return command_payload
    finally:
        db.close()


# Function: ensure_placement_compartment_schema
def ensure_placement_compartment_schema(db: Session) -> None:
    cols = {
        row[1]
        for row in db.execute(text("PRAGMA table_info(placements)")).fetchall()
    }
    if "compartment" not in cols:
        db.execute(text("ALTER TABLE placements ADD COLUMN compartment INTEGER"))
        db.commit()

    db.execute(
        text(
            "UPDATE placements "
            "SET compartment = 1 "
            "WHERE compartment IS NULL OR compartment < 1 OR compartment > 3"
        )
    )
    db.commit()


# Function: _trim_excess_racks
def _trim_excess_racks(db: Session, racks: list, target: int) -> None:
    """Remove excess racks (keep the first `target`), orphaning their placements first."""
    for rack in racks[target:]:
        db.query(Placement).filter(Placement.rack_id == rack.id).delete()
        db.delete(rack)
    db.commit()


# Function: _add_missing_racks
def _add_missing_racks(db: Session, scientist: Scientist, racks: list, idx: int, target: int) -> None:
    existing_cols = {r.name.replace("Rack ", "") for r in racks}
    for col in ["1", "2", "3"]:
        if len(racks) >= target:
            break
        if col in existing_cols:
            continue
        db.add(Rack(
            barcode=f"RACK-S{idx}-{col}",
            name=f"Rack {col}",
            scientist_id=scientist.id,
        ))
        existing_cols.add(col)
    db.commit()


# Function: ensure_rack_count
def ensure_rack_count(db: Session, target: int = 3) -> None:
    """Ensure every scientist has exactly `target` racks, trimming or adding as needed."""
    scientists = db.query(Scientist).all()
    for idx, scientist in enumerate(scientists, start=1):
        racks = (
            db.query(Rack)
            .filter(Rack.scientist_id == scientist.id)
            .order_by(Rack.id)
            .all()
        )
        if len(racks) > target:
            _trim_excess_racks(db, racks, target)
        elif len(racks) < target:
            _add_missing_racks(db, scientist, racks, idx, target)


# Function: seed_data
def seed_data(db: Session) -> None:
    if db.query(Scientist).count() > 0:
        return

    scientists_data = [
        {"name": "Dr. Alice", "code": "S001"},
        {"name": "Dr. Bob", "code": "S002"},
        {"name": "Dr. Carol", "code": "S003"},
    ]
    for s_data in scientists_data:
        db.add(Scientist(**s_data))
    db.flush()

    scientists = db.query(Scientist).all()
    # 3 racks × 3 slots each = 9 slots per scientist
    for idx, scientist in enumerate(scientists, start=1):
        for col in ["1", "2", "3"]:
            db.add(
                Rack(
                    barcode=f"RACK-S{idx}-{col}",
                    name=f"Rack {col}",
                    scientist_id=scientist.id,
                )
            )

    chemicals_data = [
        {"barcode": "CHEM-001", "name": "Sodium Chloride", "description": "NaCl — Common salt"},
        {"barcode": "CHEM-002", "name": "Hydrochloric Acid", "description": "HCl — Strong acid"},
        {"barcode": "CHEM-003", "name": "Sulfuric Acid", "description": "H2SO4 — Strong acid"},
        {"barcode": "CHEM-004", "name": "Sodium Hydroxide", "description": "NaOH — Strong base"},
        {"barcode": "CHEM-005", "name": "Ethanol", "description": "C2H5OH — Alcohol"},
        {"barcode": "CHEM-006", "name": "Acetone", "description": "C3H6O — Solvent"},
        {"barcode": "CHEM-007", "name": "Hydrogen Peroxide", "description": "H2O2 — Oxidizing agent"},
        {"barcode": "CHEM-008", "name": "Ammonia Solution", "description": "NH3 — Weak base"},
        {"barcode": "CHEM-009", "name": "Benzene", "description": "C6H6 — Aromatic hydrocarbon"},
        {"barcode": "CHEM-010", "name": "Methanol", "description": "CH3OH — Alcohol"},
    ]
    for c_data in chemicals_data:
        db.add(ChemicalCatalog(**c_data))

    db.commit()


# Function: lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    db = next(get_db())
    try:
        ensure_placement_compartment_schema(db)
        seed_data(db)
        ensure_rack_count(db, target=3)
        mqtt_bridge.set_on_command_finished(_dispatch_next_for_robot)
        mqtt_bridge.start()
    finally:
        db.close()
    yield
    mqtt_bridge.stop()


app = FastAPI(title="Lab Chemical Management System", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_PUBLIC_PATHS = {"/", "/api/health", "/api/auth/refresh", "/docs", "/openapi.json", "/redoc"}
_READ_ONLY_SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


# Function: enforce_auth
@app.middleware("http")
async def enforce_auth(request: Request, call_next):
    path = request.url.path
    if request.method == "OPTIONS" or not auth_required() or not path.startswith("/api") or path in _PUBLIC_PATHS:
        return await call_next(request)
    token = extract_bearer_token(request.headers.get("Authorization", ""))
    if not token:
        return JSONResponse({"error": "Authentication required"}, status_code=401)
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        return JSONResponse({"error": str(exc)}, status_code=401)

    try:
        portal_session = await asyncio.to_thread(validate_portal_session, token)
    except PermissionError as exc:
        return JSONResponse({"error": str(exc), "code": "LAB_ACCESS_DENIED"}, status_code=403)
    except (ValueError, TypeError) as exc:
        return JSONResponse({"error": str(exc)}, status_code=401)

    portal_user = portal_session.get("user") or {}
    payload["username"] = portal_user.get("username", payload.get("username"))
    payload["role"] = portal_user.get("role", payload.get("role"))
    payload["apps"] = portal_user.get("apps") or []
    payload["read_only"] = bool(portal_user.get("read_only"))
    if payload.get("role") != "admin" and LABROBOT_APP not in (payload.get("apps") or []):
        return JSONResponse(
            {"error": "Access denied for Lab Robot", "code": "LAB_ACCESS_DENIED"},
            status_code=403,
        )
    if payload.get("read_only") and request.method not in _READ_ONLY_SAFE_METHODS:
        return JSONResponse(
            {
                "error": "Read-only access: operations are disabled for this account",
                "code": "READ_ONLY_ACCOUNT",
            },
            status_code=403,
        )
    request.state.auth = payload
    request.state.portal_user = portal_user
    return await call_next(request)


# Function: refresh_access_token
@app.post("/api/auth/refresh")
async def refresh_access_token(request: Request):
    """Exchanges a token that's expired (or about to) for a fresh one.

    Exempted from enforce_auth (see _PUBLIC_PATHS) because the whole point
    is to accept a token the strict path would already reject on `exp` —
    the signature check inside decode_token_for_refresh is what proves the
    caller actually held a legitimately-issued session, not just any
    client. Mirrors Modernization/api/server.py's twin endpoint.
    """
    token = extract_bearer_token(request.headers.get("Authorization", ""))
    if not token:
        try:
            body = await request.json()
        except (ValueError, TypeError):
            body = {}
        token = (body or {}).get("token")
    if not token:
        return JSONResponse({"error": "Authentication required"}, status_code=401)
    try:
        payload = decode_token_for_refresh(token)
    except ValueError as exc:
        return JSONResponse({"error": str(exc)}, status_code=401)
    try:
        portal_session = await asyncio.to_thread(validate_portal_session, token)
    except (PermissionError, ValueError, TypeError) as exc:
        return JSONResponse({"error": str(exc)}, status_code=401)

    portal_user = portal_session.get("user") or {}
    if portal_user.get("role") != "admin" and LABROBOT_APP not in (portal_user.get("apps") or []):
        return JSONResponse(
            {"error": "Access denied for Lab Robot", "code": "LAB_ACCESS_DENIED"},
            status_code=403,
        )

    # The central portal owns expiry. Return the same token rather than
    # extending a desktop session beyond its authoritative portal session.
    return {"token": token, "exp": int(payload.get("exp", 0))}


@app.get("/api/auth/session")
async def current_auth_session(request: Request):
    return {
        "user": request.state.portal_user,
        "expires_at": request.state.auth.get("exp"),
    }


# ── Scientists ────────────────────────────────────────────────────────────────

# Function: get_scientists
@app.get("/api/scientists", response_model=list[ScientistSchema])
def get_scientists(db: Session = Depends(get_db)):
    return db.query(Scientist).all()


# ── Chemical Catalog ──────────────────────────────────────────────────────────

# Function: get_all_chemicals
@app.get("/api/chemicals", response_model=list[ChemicalCatalogSchema])
def get_all_chemicals(db: Session = Depends(get_db)):
    return db.query(ChemicalCatalog).all()


# Function: search_chemical
@app.get("/api/chemicals/search", response_model=ChemicalCatalogSchema)
def search_chemical(barcode: str, db: Session = Depends(get_db)):
    chemical = (
        db.query(ChemicalCatalog)
        .filter(ChemicalCatalog.barcode == barcode)
        .first()
    )
    if not chemical:
        raise HTTPException(status_code=404, detail="Chemical not found for this barcode")
    return chemical


# ── Placements ────────────────────────────────────────────────────────────────

# Function: place_chemical
@app.post("/api/placements", status_code=201)
def place_chemical(payload: PlacementCreate, db: Session = Depends(get_db)):
    chemical = (
        db.query(ChemicalCatalog)
        .filter(ChemicalCatalog.barcode == payload.chemical_barcode)
        .first()
    )
    if not chemical:
        raise HTTPException(status_code=404, detail="Chemical not found for this barcode")

    # Validate the requested rack belongs to this scientist
    requested_rack = db.query(Rack).filter(Rack.id == payload.rack_id).first()
    if not requested_rack or requested_rack.scientist_id != payload.scientist_id:
        raise HTTPException(status_code=400, detail="Selected rack does not belong to this scientist")

    occupied_compartments = {
        p.compartment
        for p in db.query(Placement)
        .filter(
            Placement.rack_id == requested_rack.id,
            Placement.status == "Placed",
        )
        .all()
    }

    if payload.compartment in occupied_compartments:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Rack {requested_rack.barcode} compartment C{payload.compartment} is occupied. "
                "Please select an empty compartment."
            ),
        )

    placement = Placement(
        chemical_id=chemical.id,
        rack_id=requested_rack.id,
        scientist_id=payload.scientist_id,
        compartment=payload.compartment,
        status="Placed",
        placed_at=datetime.datetime.utcnow(),
    )
    db.add(placement)
    db.commit()
    db.refresh(placement)

    result = PlacementSchema.model_validate(placement).model_dump(mode="json")
    result["message"] = None
    return result


# Function: reset_all_placements
@app.delete("/api/placements/all", status_code=200)
def reset_all_placements(db: Session = Depends(get_db)):
    """Delete every placement record — for dev/testing use."""
    count = db.query(Placement).delete(synchronize_session=False)
    db.commit()
    return {"deleted": count}


# Function: get_placements
@app.get("/api/placements", response_model=list[PlacementSchema])
def get_placements(scientist_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Placement)
    if scientist_id is not None:
        query = query.filter(Placement.scientist_id == scientist_id)
    return query.order_by(Placement.rack_id.asc(), Placement.compartment.asc(), Placement.placed_at.desc()).all()


# Function: fetch_chemical
@app.put("/api/placements/{placement_id}/fetch", response_model=PlacementSchema)
def fetch_chemical(placement_id: int, db: Session = Depends(get_db)):
    placement = db.query(Placement).filter(Placement.id == placement_id).first()
    if not placement:
        raise HTTPException(status_code=404, detail="Placement record not found")
    if placement.status == "Fetched":
        raise HTTPException(status_code=409, detail="Chemical has already been fetched")

    placement.status = "Fetched"
    placement.fetched_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(placement)
    return placement


# ── 3D Rack Visualizer ────────────────────────────────────────────────────────

# Function: visualize_racks
@app.get("/api/visualize/racks", response_class=Response)
def visualize_racks(scientist_id: int | None = None, db: Session = Depends(get_db)):
    from visualizer import generate_rack_image

    scientists = db.query(Scientist).all()
    if scientist_id is not None:
        scientists = [s for s in scientists if s.id == scientist_id]

    placements_query = db.query(Placement)
    if scientist_id is not None:
        placements_query = placements_query.filter(
            Placement.scientist_id == scientist_id
        )
    placements = placements_query.all()

    scientists_data = [
        {
            "id": s.id,
            "name": s.name,
            "code": s.code,
            "racks": [
                {"id": r.id, "barcode": r.barcode, "name": r.name}
                for r in s.racks
            ],
        }
        for s in scientists
    ]

    placements_data = [
        {
            "id": p.id,
            "rack_id": p.rack_id,
            "chemical_id": p.chemical_id,
            "compartment": p.compartment,
            "status": p.status,
            "chemical": {
                "barcode": p.chemical.barcode,
                "name": p.chemical.name,
            },
        }
        for p in placements
    ]

    png_bytes = generate_rack_image(scientists_data, placements_data)
    return Response(content=png_bytes, media_type="image/png")


# ── Production Robot Management ────────────────────────────────────────────────

# Function: create_robot_type
@app.post("/api/robot-types", response_model=RobotTypeSchema, status_code=201)
def create_robot_type(robot_type_data: RobotTypeCreate, db: Session = Depends(get_db)):
    """Create a new robot type definition."""
    existing = db.query(RobotType).filter(RobotType.name == robot_type_data.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Robot type already exists")

    robot_type = RobotType(**robot_type_data.model_dump())
    db.add(robot_type)
    db.commit()
    db.refresh(robot_type)
    return robot_type


# Function: get_robot_types
@app.get("/api/robot-types", response_model=list[RobotTypeSchema])
def get_robot_types(db: Session = Depends(get_db)):
    """Get all robot type definitions."""
    return db.query(RobotType).all()


# Function: create_robot
@app.post("/api/robots", response_model=RobotSchema, status_code=201)
def create_robot(robot_data: RobotCreate, db: Session = Depends(get_db)):
    """Create a new robot instance."""
    try:
        robot = RobotService.create_robot(db, robot_data)
        return robot
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Function: list_robots
@app.get("/api/robots", response_model=list[RobotSchema])
def list_robots(location_zone: str = None, status: str = None, db: Session = Depends(get_db)):
    """List all robots with optional filtering."""
    return RobotService.list_robots(db, location_zone=location_zone, status=status)


# Function: get_robot
@app.get("/api/robots/{robot_id}", response_model=RobotSchema)
def get_robot(robot_id: int, db: Session = Depends(get_db)):
    """Get a specific robot by ID."""
    robot = RobotService.get_robot(db, robot_id)
    if not robot:
        raise HTTPException(status_code=404, detail="Robot not found")
    return robot


# Function: update_robot
@app.put("/api/robots/{robot_id}", response_model=RobotSchema)
def update_robot(robot_id: int, update_data: RobotUpdate, db: Session = Depends(get_db)):
    """Update robot status and properties."""
    robot = RobotService.update_robot(db, robot_id, update_data)
    if not robot:
        raise HTTPException(status_code=404, detail="Robot not found")
    return robot


# Function: create_operation
@app.post("/api/robots/{robot_id}/operations", response_model=RobotOperationSchema, status_code=201)
def create_operation(robot_id: int, op_data: RobotOperationCreate, db: Session = Depends(get_db)):
    """Create a new operation for a robot."""
    robot = RobotService.get_robot(db, robot_id)
    if not robot:
        raise HTTPException(status_code=404, detail="Robot not found")

    operation = RobotService.create_operation(db, op_data)
    return operation


# Function: get_robot_telemetry
@app.get("/api/robots/{robot_id}/telemetry")
def get_robot_telemetry(robot_id: int, limit: int = 100, db: Session = Depends(get_db)):
    """Get recent telemetry data for a robot."""
    robot = RobotService.get_robot(db, robot_id)
    if not robot:
        raise HTTPException(status_code=404, detail="Robot not found")

    telemetry = RobotService.get_robot_telemetry(db, robot_id, limit=limit)
    return [
        {
            "timestamp": t.timestamp.isoformat(),
            "position": t.position,
            "orientation": t.orientation,
            "velocity": t.velocity,
            "battery_level": t.battery_level,
            "current_load": t.current_load,
            "error_code": t.error_code,
        }
        for t in telemetry
    ]


# ── Production Stations ────────────────────────────────────────────────────────

# Function: create_station
@app.post("/api/stations", response_model=ProductionStationSchema, status_code=201)
def create_station(station_data: ProductionStationCreate, db: Session = Depends(get_db)):
    """Create a new production station."""
    existing = db.query(ProductionStation).filter(
        ProductionStation.station_id == station_data.station_id
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Station already exists")

    station = ProductionStation(
        station_id=station_data.station_id,
        name=station_data.name,
        station_type=station_data.station_type,
        position=station_data.position or {"x": 0, "y": 0, "z": 0},
        dimensions=station_data.dimensions or {"length": 2.0, "width": 2.0, "height": 2.0},
    )
    db.add(station)
    db.commit()
    db.refresh(station)
    return station


# Function: list_stations
@app.get("/api/stations", response_model=list[ProductionStationSchema])
def list_stations(db: Session = Depends(get_db)):
    """List all production stations."""
    return db.query(ProductionStation).all()


# ── Simulation Scenarios ────────────────────────────────────────────────────────

# Function: create_simulation
@app.post("/api/simulations/scenarios", response_model=SimulationConfigSchema, status_code=201)
def create_simulation(config_data: SimulationConfigCreate, db: Session = Depends(get_db)):
    """Create a new simulation scenario."""
    existing = db.query(SimulationConfig).filter(
        SimulationConfig.config_id == config_data.config_id
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Simulation config already exists")

    scenario = SimulationService.create_scenario(
        db,
        config_data.config_id,
        config_data.scenario_type,
        config_data.name,
        config_data.physics_enabled,
    )
    return scenario


# Function: list_simulations
@app.get("/api/simulations/scenarios", response_model=list[SimulationConfigSchema])
def list_simulations(db: Session = Depends(get_db)):
    """List all simulation configurations."""
    return db.query(SimulationConfig).filter(SimulationConfig.enabled == True).all()


# Function: get_scenario_templates
@app.get("/api/simulations/templates")
def get_scenario_templates():
    """Get available simulation scenario templates."""
    return {
        "templates": [
            {
                "id": "production",
                "name": "Production & Assembly",
                "description": "Assembly line with welding, machining, inspection robots",
                "use_cases": ["Machine Tending", "Welding", "Assembly", "Inspection"]
            },
            {
                "id": "warehouse",
                "name": "Warehouse & Intralogistics",
                "description": "AMR-based warehouse with ASRS and fleet management",
                "use_cases": ["AMR Transport", "ASRS", "Inventory Management", "Fleet Control"]
            },
            {
                "id": "quality",
                "name": "Quality & Inspection",
                "description": "Vision-based QA and advanced inspection robots",
                "use_cases": ["Visual Inspection", "Quality Assurance", "Defect Detection"]
            },
            {
                "id": "mixed",
                "name": "Full Factory",
                "description": "Complete factory floor with all robot types",
                "use_cases": ["Production", "Intralogistics", "Quality", "Safety"]
            }
        ]
    }


# ── MQTT Bridge, Queue, and Inventory APIs ───────────────────────────────────

# Function: enqueue_robot_command
@app.post("/api/robot-commands", response_model=RobotCommandSchema, status_code=201)
def enqueue_robot_command(command_data: RobotCommandCreate, db: Session = Depends(get_db)):
    """Enqueue robot command; if robot is idle, dispatch immediately via MQTT."""
    command = CommandQueueService.enqueue_command(db, command_data.model_dump())

    # Multi-command queueing: commands are accepted even when robot is busy.
    if command.status == "queued":
        _dispatch_next_for_robot(command.robot_id)

    # Reload latest status after dispatch attempt.
    latest = db.query(RobotCommand).filter(RobotCommand.id == command.id).first()
    return latest or command


# Function: list_robot_commands
@app.get("/api/robot-commands", response_model=list[RobotCommandSchema])
def list_robot_commands(robot_id: str | None = None, status: str | None = None, db: Session = Depends(get_db)):
    query = db.query(RobotCommand)
    if robot_id:
        query = query.filter(RobotCommand.robot_id == robot_id)
    if status:
        query = query.filter(RobotCommand.status == status)
    return query.order_by(RobotCommand.created_at.desc()).all()


# Function: get_robot_queue
@app.get("/api/robots/{robot_id}/queue", response_model=list[RobotCommandSchema])
def get_robot_queue(robot_id: str, db: Session = Depends(get_db)):
    return CommandQueueService.list_robot_queue(db, robot_id)


# Function: get_mqtt_acks
@app.get("/api/mqtt/acks", response_model=list[MqttAcknowledgementSchema])
def get_mqtt_acks(limit: int = 200, db: Session = Depends(get_db)):
    return CommandQueueService.list_acknowledgements(db, limit=limit)


# Function: ingest_ack
@app.post("/api/mqtt/acks", response_model=MqttAcknowledgementSchema, status_code=201)
def ingest_ack(payload: dict, db: Session = Depends(get_db)):
    """Manual/webhook fallback to ingest acknowledgements without broker subscription."""
    ack = CommandQueueService.persist_ack(db, "api/manual", payload)
    command = CommandQueueService.apply_ack_to_command(db, payload)
    if command and command.status in {"completed", "failed"}:
        _dispatch_next_for_robot(command.robot_id)
    return ack


# Function: get_rack_inventory
@app.get("/api/inventory/racks", response_model=list[InventorySchema])
def get_rack_inventory(db: Session = Depends(get_db)):
    rows = CommandQueueService.list_rack_inventory(db)
    return [
        {
            "location_type": "rack",
            "location_id": row.rack_id,
            "item_id": row.item_id,
            "quantity": row.quantity,
            "updated_at": row.updated_at,
        }
        for row in rows
    ]


# Function: get_conveyor_inventory
@app.get("/api/inventory/conveyors", response_model=list[InventorySchema])
def get_conveyor_inventory(db: Session = Depends(get_db)):
    rows = CommandQueueService.list_conveyor_inventory(db)
    return [
        {
            "location_type": "conveyor",
            "location_id": row.conveyor_id,
            "item_id": row.item_id,
            "quantity": row.quantity,
            "updated_at": row.updated_at,
        }
        for row in rows
    ]


# Function: initialize_scenario
@app.post("/api/simulations/{scenario_id}/initialize")
def initialize_scenario(scenario_id: str, db: Session = Depends(get_db)):
    """Initialize a simulation with robots from database."""
    config = db.query(SimulationConfig).filter(
        SimulationConfig.config_id == scenario_id
    ).first()
    if not config:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Create scenario from template
    scenario = None
    if scenario_id.startswith("PROD"):
        scenario = ScenarioFactory.create_production_scenario()
    elif scenario_id.startswith("WH"):
        scenario = ScenarioFactory.create_warehouse_scenario()
    elif scenario_id.startswith("QI"):
        scenario = ScenarioFactory.create_inspection_scenario()

    if not scenario:
        raise HTTPException(status_code=400, detail="Unknown scenario type")

    return {
        "scenario_id": scenario.config_id,
        "status": "initialized",
        "robots": list(scenario.robots.keys()),
        "obstacles": scenario.obstacles,
    }


# ── AI Lab — Google VEO sample generation / chat ────────────────────────────
# The one call site in the AI Lab catalog demo (frontend/src/components/
# AILabCatalog.jsx) that talks to a real model instead of simulating one.
# The key never reaches the browser: the frontend calls these endpoints
# (which sit behind the same enforce_auth() middleware as every other /api
# route above), and only this process holds GOOGLE_AI_API_KEY.
_GEMINI_MODEL = "gemini-flash-latest"
_GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{_GEMINI_MODEL}:generateContent"
_VEO_SYSTEM_INSTRUCTION = (
    "You are standing in for Google VEO, a video generation tool, inside a sandbox "
    "trial demo in an AI Lab catalog. VEO itself is a separate video model this demo "
    "doesn't call — you are a real conversational stand-in so the trial feels live "
    "instead of scripted. Chat naturally with the user about the video they want; "
    "whenever they ask you to generate or describe something, respond with a vivid, "
    "concrete description of what that video would show. Never say you're a text "
    "model or that no video file was actually produced — stay in character as the "
    "tool's sample-generation step throughout."
)


# Function: _call_gemini
def _call_gemini(contents: list[dict], system_instruction: str | None = None) -> str:
    """POSTs a `contents` turn list to Gemini's generateContent and returns
    the reply text. Shared by the single-shot sample endpoint and the chat
    endpoint below — same key, same model, same error handling either way."""
    api_key = os.getenv("GOOGLE_AI_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(status_code=503, detail="GOOGLE_AI_API_KEY is not configured on the backend")

    request_body: dict = {"contents": contents}
    if system_instruction:
        request_body["systemInstruction"] = {"parts": [{"text": system_instruction}]}
    request = urllib.request.Request(
        _GEMINI_URL,
        data=json.dumps(request_body).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json", "X-goog-api-key": api_key},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise HTTPException(status_code=502, detail=f"Gemini request failed: {detail}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise HTTPException(status_code=502, detail=f"Gemini request failed: {exc}") from exc

    try:
        return result["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise HTTPException(status_code=502, detail="Gemini returned an unexpected response shape") from exc


# Function: generate_veo_sample
@app.post("/api/ai-lab/veo/sample")
def generate_veo_sample(payload: dict):
    """Stand-in for a real Google VEO video-generation call: VEO itself is a
    separate (billed, quota-gated) video model, so this uses the trial
    Gemini text key to produce a real, non-canned description of what the
    sample video would contain, keyed off the use-case note the requester
    entered in the Request Access step."""
    use_case = (payload or {}).get("use_case", "").strip() or "a short brand marketing clip"
    prompt = (
        "You are the sample-output step of a video generation tool's sandbox trial. "
        f'A user requested a sample video for this use case: "{use_case}". '
        "In 2-3 vivid sentences, describe what the generated sample video would show. "
        "Describe the video only — do not mention that you are a text model or that no video file exists."
    )
    text_out = _call_gemini([{"parts": [{"text": prompt}]}])
    return {"sample_description": text_out, "model": _GEMINI_MODEL}


# Function: veo_chat
@app.post("/api/ai-lab/veo/chat")
def veo_chat(payload: dict):
    """Multi-turn chat for the Google VEO trial — the same real Gemini call
    as generate_veo_sample, but as an actual back-and-forth conversation
    (a la the Google AI Studio chat playground) instead of one canned
    generation. Takes the full running transcript each turn since this
    endpoint is stateless; the frontend keeps history client-side."""
    messages = (payload or {}).get("messages") or []
    contents = []
    for message in messages:
        text = str((message or {}).get("text", "")).strip()
        if not text:
            continue
        role = "model" if message.get("role") == "model" else "user"
        contents.append({"role": role, "parts": [{"text": text}]})
    if not contents:
        raise HTTPException(status_code=400, detail="messages must contain at least one non-empty turn")
    reply = _call_gemini(contents, system_instruction=_VEO_SYSTEM_INSTRUCTION)
    return {"reply": reply, "model": _GEMINI_MODEL}


# ── Health Check ───────────────────────────────────────────────────────────────

# Function: health_check
@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Lab Robot Management System"}
