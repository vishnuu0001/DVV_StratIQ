# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Seed data factory — generates and loads a correlated supply chain dataset.
# Date: 2026-06-01
# ---------------------------------------------------------------------------
"""Seed data factory — generates and loads a correlated supply chain dataset.

All operations use MERGE so the load is fully idempotent.
"""
from __future__ import annotations

import json
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

import structlog
from neo4j import AsyncSession

from kg.repositories.entity_repo import _serialise_for_neo4j

log = structlog.get_logger(__name__)

_NOW = datetime(2025, 1, 15, 8, 0, 0, tzinfo=timezone.utc)
_DT = _NOW.isoformat()


# ---------------------------------------------------------------------------
# Helper builders
# ---------------------------------------------------------------------------

# Function: _base
def _base(entity_id: str, kind: str, domain: str) -> dict[str, Any]:
    return {
        "id": entity_id,
        "kind": kind,
        "domain": domain,
        "created_at": _DT,
        "updated_at": _DT,
        "status": "ACTIVE",
        "metadata": {},
    }


# Function: _supplier
def _supplier(n: int) -> dict[str, Any]:
    countries = ["CN", "DE", "US", "IN", "MX"]
    e = _base(f"SUP-00{n}", "Supplier", "procurement")
    e.update({
        "name": f"Supplier {n} Ltd",
        "country": countries[n - 1],
        "tier": [1, 1, 2, 2, 3][n - 1],
        "lead_time_days": [14, 21, 30, 45, 60][n - 1],
        "reliability_score": [0.97, 0.93, 0.88, 0.82, 0.75][n - 1],
        "contract_id": f"CTR-100{n}",
    })
    return e


# Function: _carrier
def _carrier(n: int) -> dict[str, Any]:
    modes = ["AIR", "SEA", "ROAD", "RAIL", "MULTIMODAL", "SEA", "AIR", "ROAD"]
    e = _base(f"CAR-00{n}", "Carrier", "logistics")
    e.update({
        "name": f"Carrier {n} Express",
        "mode": modes[n - 1],
        "service_level": ["PREMIUM", "STANDARD", "ECONOMY", "EXPRESS", "STANDARD", "ECONOMY", "PREMIUM", "STANDARD"][n - 1],
        "tracking_api": f"https://track.carrier{n}.com/api",
        "on_time_performance": round(0.95 - (n - 1) * 0.03, 2),
    })
    return e


# Function: _shopfloor
def _shopfloor(n: int) -> dict[str, Any]:
    e = _base(f"PLANT-00{n}", "ShopFloor", "production")
    e.update({
        "plant_address": f"{n * 100} Industrial Way, Plant City {n}",
        "shift_pattern": "3x8" if n == 1 else "2x12",
    })
    return e


# Function: _workcenter
def _workcenter(n: int, plant_n: int) -> dict[str, Any]:
    e = _base(f"WC-00{n}", "WorkCenter", "production")
    e.update({
        "shopfloor_id": f"PLANT-00{plant_n}",
        "line": f"LINE-{chr(64 + n)}",
        "capacity_per_hr": str(Decimal(str(100 + n * 25))),
        "current_order_id": None,
    })
    return e


# Function: _person
def _person(pid: str, name: str, role: str, email: str, region: str) -> dict[str, Any]:
    e = _base(pid, "Person", "people")
    e.update({"name": name, "role": role, "email": email, "phone": "+1-555-000-0001", "region": region})
    return e


# Function: _material
def _material(mid: str, desc: str, category: str, criticality: str, safety_stock: str, shelf_life: int | None = None) -> dict[str, Any]:
    e = _base(mid, "Material", "procurement")
    e.update({
        "description": desc,
        "category": category,
        "criticality": criticality,
        "safety_stock": safety_stock,
        "shelf_life_days": shelf_life,
    })
    return e


# Function: _po
def _po(n: int, sup_id: str, buyer_id: str, status: str, value: str, delivery: str) -> dict[str, Any]:
    e = _base(f"PO-{10000 + n}", "PurchaseOrder", "procurement")
    e.update({
        "supplier_id": sup_id,
        "buyer_id": buyer_id,
        "status": status,
        "currency": "USD",
        "total_value": value,
        "expected_delivery": delivery,
    })
    return e


# Function: _pol
def _pol(po_id: str, line: int, mat_id: str, qty: str, uom: str, price: str, need_by: str) -> dict[str, Any]:
    e = _base(f"POL-{po_id}-{line}", "PurchaseOrderLine", "procurement")
    e.update({
        "po_id": po_id,
        "material_id": mat_id,
        "qty_ordered": qty,
        "uom": uom,
        "unit_price": price,
        "need_by_date": need_by,
    })
    return e


# Function: _bom
def _bom(n: int, parent_mat: str, version: str, components: list[dict]) -> dict[str, Any]:
    e = _base(f"BOM-00{n}", "BOM", "production")
    e.update({
        "parent_material_id": parent_mat,
        "version": version,
        "components": components,  # list; _serialise_for_neo4j will json.dumps it
    })
    return e


# Function: _asn
def _asn(n: int, po_id: str, carrier_id: str, incoterm: str, days_offset: int = 0) -> dict[str, Any]:
    ship = datetime(2025, 1, 10 + days_offset, tzinfo=timezone.utc).isoformat()
    eta = datetime(2025, 2, 1 + days_offset, tzinfo=timezone.utc).isoformat()
    e = _base(f"ASN-{20000 + n}", "ASN", "logistics")
    e.update({
        "po_id": po_id,
        "carrier_id": carrier_id,
        "ship_date": ship,
        "eta": eta,
        "incoterm": incoterm,
        "handling_units": [f"HU-{n:04d}-{i}" for i in range(1, 4)],  # list; _serialise_for_neo4j handles it
    })
    return e


# Function: _shipment
def _shipment(n: int, asn_id: str, status: str, location: str | None) -> dict[str, Any]:
    e = _base(f"SHP-{30000 + n}", "Shipment", "logistics")
    e.update({
        "asn_id": asn_id,
        "status": status,
        "current_location": location,
        "last_event_at": _DT,
    })
    return e


# Function: _container
def _container(n: int, shp_id: str, ctype: str, weight: str) -> dict[str, Any]:
    e = _base(f"CNT-{n:03d}", "Container", "logistics")
    e.update({
        "shipment_id": shp_id,
        "type": ctype,
        "seal_no": f"SEAL-{n:06d}",
        "gross_weight_kg": weight,
    })
    return e


# Function: _customs
def _customs(n: int, shp_id: str, port: str, status: str, duties: str | None) -> dict[str, Any]:
    e = _base(f"CUS-{40000 + n}", "Customs", "logistics")
    e.update({
        "shipment_id": shp_id,
        "port": port,
        "status": status,
        "duties_amount": duties,
        "cleared_at": _DT if status == "CLEARED" else None,
    })
    return e


# Function: _dock
def _dock(n: int, warehouse_id: str) -> dict[str, Any]:
    e = _base(f"DOCK-{n:03d}", "Dock", "warehouse")
    e.update({
        "warehouse_id": warehouse_id,
        "appointment_window_start": datetime(2025, 1, 15, 6, 0, tzinfo=timezone.utc).isoformat(),
        "appointment_window_end": datetime(2025, 1, 15, 14, 0, tzinfo=timezone.utc).isoformat(),
        "current_load": n % 3,
    })
    return e


# Function: _grn
def _grn(n: int, po_id: str, asn_id: str) -> dict[str, Any]:
    e = _base(f"GRN-{50000 + n}", "GRN", "warehouse")
    e.update({
        "po_id": po_id,
        "asn_id": asn_id,
        "received_qty": str(Decimal("100.00")),
        "short_qty": str(Decimal("2.00")),
        "damaged_qty": str(Decimal("0.50")),
        "received_at": _DT,
    })
    return e


# Function: _qi
def _qi(n: int, grn_id: str, disposition: str) -> dict[str, Any]:
    e = _base(f"QC-{60000 + n}", "QualityInspection", "warehouse")
    e.update({
        "grn_id": grn_id,
        "sample_size": 10 + n,
        "defect_rate": round(0.02 * (n % 5), 4),
        "disposition": disposition,
        "closed_at": _DT if disposition != "PENDING" else None,
    })
    return e


# Function: _bin
def _bin(n: int, warehouse_id: str) -> dict[str, Any]:
    zone = chr(65 + (n % 26))
    e = _base(f"BIN-{zone}-{n:03d}", "Bin", "warehouse")
    e.update({
        "warehouse_id": warehouse_id,
        "zone": zone,
        "capacity": str(Decimal("500.00")),
        "current_qty": str(Decimal(str(n * 10 % 400))),
    })
    return e


# Function: _stocklot
def _stocklot(n: int, mat_id: str, bin_id: str) -> dict[str, Any]:
    e = _base(f"LOT-{70000 + n}", "StockLot", "warehouse")
    e.update({
        "material_id": mat_id,
        "bin_id": bin_id,
        "qty_on_hand": str(Decimal("50.00")),
        "qty_allocated": str(Decimal("10.00")),
        "expiry_date": "2026-01-01" if n % 3 == 0 else None,
        "lot_number": f"LN-{n:06d}",
    })
    return e


# Function: _prd
def _prd(n: int, fg_id: str, bom_id: str, status: str) -> dict[str, Any]:
    e = _base(f"PRD-{80000 + n}", "ProductionOrder", "production")
    e.update({
        "finished_good_id": fg_id,
        "qty": str(Decimal("200.00")),
        "start_date": "2025-01-20",
        "due_date": "2025-02-15",
        "status": status,
    })
    return e


# Function: _mat_issue
def _mat_issue(n: int, prd_id: str, mat_id: str, bin_id: str, wc_id: str) -> dict[str, Any]:
    e = _base(f"ISS-{90000 + n}", "MaterialIssue", "production")
    e.update({
        "production_order_id": prd_id,
        "material_id": mat_id,
        "qty_issued": str(Decimal("25.00")),
        "source_bin_id": bin_id,
        "dest_workcenter_id": wc_id,
        "issued_at": _DT,
    })
    return e


# Function: _signal_bus
def _signal_bus() -> dict[str, Any]:
    e = _base("BUS-001", "SignalBus", "system")
    e.update({"bus_type": "redis_streams", "redis_url": "redis://redis:6379/0"})
    return e


# Function: _orchestrator
def _orchestrator() -> dict[str, Any]:
    e = _base("ORC-001", "Orchestrator", "system")
    e.update({"version": "1.0.0", "model": "claude-sonnet-4-6"})
    return e


# ---------------------------------------------------------------------------
# Dataset builders (pure — build a list of entity dicts, no I/O)
# ---------------------------------------------------------------------------

# Function: _build_materials
def _build_materials() -> list[dict[str, Any]]:
    materials: list[dict[str, Any]] = []
    criticalities = ["A", "A", "B", "A", "B", "C", "A", "B", "C", "B"]

    raw_descs = [
        "Steel Coil Grade A", "Aluminium Ingot 99.7%", "Polypropylene Resin",
        "Copper Wire 2mm", "Rubber Sheet 3mm", "Silicone Compound",
        "Carbon Fibre Strand", "Glass Fibre Mat", "Epoxy Resin Type B", "Nylon 66 Pellets",
    ]
    for i, desc in enumerate(raw_descs, 1):
        materials.append(_material(f"MAT-RAW-{i:03d}", desc, "RAW", criticalities[i - 1], "50.00"))

    sfg_descs = [
        "Stamped Steel Bracket", "Machined Aluminium Housing", "Injection Moulded Cover",
        "Wound Copper Coil", "Vulcanised Rubber Seal", "Cast Silicone Gasket",
        "CFRP Panel 600x400", "Fibreglass Shell", "Cured Epoxy Laminate", "Nylon Gear Assembly",
    ]
    for i, desc in enumerate(sfg_descs, 1):
        materials.append(_material(f"MAT-SFG-{i:03d}", desc, "SFG", criticalities[i - 1], "100.00"))

    fg_descs = [
        "Electric Motor Module M1", "Gearbox Assembly G2",
        "Control Unit CU3", "Sensor Pack SP4", "Actuator Assembly AA5",
    ]
    fg_criticalities = ["A", "A", "B", "B", "C"]
    for i, desc in enumerate(fg_descs, 1):
        materials.append(_material(f"MAT-FG-{i:03d}", desc, "FG", fg_criticalities[i - 1], "200.00"))

    return materials


# Function: _build_purchase_orders
def _build_purchase_orders(suppliers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    statuses = ["OPEN", "ACK", "SHIPPED", "RECEIVED", "CLOSED", "OPEN", "ACK", "SHIPPED", "RECEIVED", "CLOSED",
                "OPEN", "ACK", "SHIPPED", "RECEIVED", "CLOSED", "DRAFT", "OPEN", "CANCELLED", "OPEN", "ACK"]
    pos_data = []
    for i in range(1, 21):
        sup_id = suppliers[(i - 1) % 5]["id"]
        val = str(Decimal(str(10000 + i * 1500)))
        po = _po(i, sup_id, "USR-BUYER-001", statuses[i - 1], val, "2025-03-15")
        pos_data.append(po)
    return pos_data


# Function: _build_po_lines
def _build_po_lines(pos_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    uoms = ["EA", "KG", "L", "M", "BOX"]
    pol_list: list[dict[str, Any]] = []
    for i, po in enumerate(pos_data, 1):
        for line in range(1, 4):
            mat_idx = ((i - 1) * 3 + line - 1) % 10
            mat_id = f"MAT-RAW-{mat_idx + 1:03d}"
            pol = _pol(po["id"], line, mat_id, str(Decimal(str(50 + line * 10))), uoms[line % 5], str(Decimal(str(100 + i * 5))), "2025-03-10")
            pol_list.append(pol)
    return pol_list


# Function: _build_asns
def _build_asns(pos_data: list[dict[str, Any]], carriers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    incoterms = ["FOB", "CIF", "DAP", "DDP", "EXW", "FCA"]
    asns = []
    for i in range(1, 19):
        po = pos_data[i % len(pos_data)]
        carrier = carriers[i % len(carriers)]
        asn = _asn(i, po["id"], carrier["id"], incoterms[i % len(incoterms)], days_offset=(i % 10))
        asns.append(asn)
    return asns


# Function: _build_shipments
def _build_shipments(asns: list[dict[str, Any]]) -> list[dict[str, Any]]:
    shp_statuses = ["IN_TRANSIT", "DELIVERED", "ARRIVED", "BOOKED", "EXCEPTION"]
    locations = ["Shanghai Port", "Los Angeles Port", "Rotterdam", "Singapore", None]
    shipments = []
    for i in range(1, 19):
        asn = asns[i - 1]
        shp = _shipment(i, asn["id"], shp_statuses[i % len(shp_statuses)], locations[i % len(locations)])
        shipments.append(shp)
    return shipments


# Function: _build_containers
def _build_containers(shipments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ctypes = ["CONT_20FT", "CONT_40FT", "PALLET", "CARTON"]
    containers = []
    for i in range(1, 25):
        shp = shipments[i % len(shipments)]
        cnt = _container(i, shp["id"], ctypes[i % len(ctypes)], str(Decimal(str(1000 + i * 50))))
        containers.append(cnt)
    return containers


# Function: _build_customs_entries
def _build_customs_entries(shipments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ports = ["Los Angeles", "Rotterdam", "Singapore", "Hamburg", "Long Beach"]
    cus_statuses = ["CLEARED", "PENDING", "HELD", "CLEARED", "CLEARED"]
    customs_entries = []
    for i in range(1, 6):
        shp = shipments[i - 1]
        duties = str(Decimal(str(500 + i * 100))) if cus_statuses[i - 1] != "PENDING" else None
        cus = _customs(i, shp["id"], ports[i - 1], cus_statuses[i - 1], duties)
        customs_entries.append(cus)
    return customs_entries


# Function: _build_grns
def _build_grns(pos_data: list[dict[str, Any]], asns: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grns = []
    for i in range(1, 16):
        po = pos_data[i % len(pos_data)]
        asn = asns[i % len(asns)]
        grn = _grn(i, po["id"], asn["id"])
        grns.append(grn)
    return grns


# Function: _build_quality_inspections
def _build_quality_inspections(grns: list[dict[str, Any]]) -> list[dict[str, Any]]:
    gi_dispositions = ["ACCEPT", "ACCEPT", "REJECT", "PENDING", "REWORK"]
    qis = []
    for i in range(1, 16):
        grn = grns[i - 1]
        qi = _qi(i, grn["id"], gi_dispositions[i % len(gi_dispositions)])
        qis.append(qi)
    return qis


# Function: _build_stock_lots
def _build_stock_lots(materials: list[dict[str, Any]], bins: list[dict[str, Any]]) -> list[dict[str, Any]]:
    stock_lots = []
    for i in range(1, 81):
        mat = materials[i % len(materials)]
        bin_node = bins[i % len(bins)]
        sl = _stocklot(i, mat["id"], bin_node["id"])
        stock_lots.append(sl)
    return stock_lots


# Function: _build_production_orders
def _build_production_orders(fg_ids: list[str], boms: list[dict[str, Any]]) -> list[dict[str, Any]]:
    prd_statuses = ["PLANNED", "RELEASED", "RUNNING", "COMPLETED", "CANCELLED", "PLANNED"]
    prod_orders = []
    for i in range(1, 13):
        fg_id = fg_ids[i % len(fg_ids)]
        bom_id = boms[i % len(boms)]["id"]
        prd = _prd(i, fg_id, bom_id, prd_statuses[i % len(prd_statuses)])
        prod_orders.append(prd)
    return prod_orders


# Function: _build_material_issues
def _build_material_issues(
    prod_orders: list[dict[str, Any]],
    materials: list[dict[str, Any]],
    bins: list[dict[str, Any]],
    workcenters: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    mat_issues = []
    for i in range(1, 41):
        prd = prod_orders[i % len(prod_orders)]
        mat = materials[i % len(materials)]
        bin_node = bins[i % len(bins)]
        wc = workcenters[i % len(workcenters)]
        iss = _mat_issue(i, prd["id"], mat["id"], bin_node["id"], wc["id"])
        mat_issues.append(iss)
    return mat_issues


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

class SeedFactory:
    # Function: __init__
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._node_count = 0
        self._edge_count = 0

    # Function: _merge_node
    async def _merge_node(self, entity: dict[str, Any]) -> None:
        kind = entity["kind"]
        props = _serialise_for_neo4j(entity)
        cypher = f"""
        MERGE (n:Entity {{id: $id}})
        SET n:{kind}
        SET n += $props
        """
        await self._session.run(cypher, id=entity["id"], props=props)
        self._node_count += 1

    # Function: _merge_edge
    async def _merge_edge(self, from_id: str, to_id: str, kind: str, verb: str, props: dict | None = None) -> None:
        rel_type = kind.upper()
        edge_props = {
            "kind": kind,
            "verb": verb,
            "properties": "{}",
            "created_at": _DT,
            "updated_at": _DT,
        }
        if props:
            edge_props["properties"] = json.dumps(props)
        cypher = f"""
        MATCH (a:Entity {{id: $from_id}})
        MATCH (b:Entity {{id: $to_id}})
        MERGE (a)-[r:{rel_type} {{verb: $verb}}]->(b)
        SET r += $props
        """
        await self._session.run(cypher, from_id=from_id, to_id=to_id, verb=verb, props=edge_props)
        self._edge_count += 1

    # Function: _merge_nodes
    async def _merge_nodes(self, items: list[dict[str, Any]]) -> None:
        for item in items:
            await self._merge_node(item)

    # Function: _merge_edges
    async def _merge_edges(self, edges: list[tuple[str, str, str, str]]) -> None:
        for from_id, to_id, kind, verb in edges:
            await self._merge_edge(from_id, to_id, kind, verb)

    # Function: _merge_bom_specifies_edges
    async def _merge_bom_specifies_edges(self, boms: list[dict[str, Any]]) -> None:
        for bom in boms:
            raw_components = bom.get("components", "[]")
            components = json.loads(raw_components) if isinstance(raw_components, str) else raw_components
            for comp in components:
                await self._merge_edge(bom["id"], comp["material_id"], "meta", "specifies")

    # Function: _seed_nodes
    async def _seed_nodes(self) -> dict[str, list[dict[str, Any]]]:
        suppliers = [_supplier(i) for i in range(1, 6)]
        await self._merge_nodes(suppliers)

        carriers = [_carrier(i) for i in range(1, 9)]
        await self._merge_nodes(carriers)

        shopfloors = [_shopfloor(i) for i in range(1, 3)]
        await self._merge_nodes(shopfloors)

        wc_plant_map = {1: 1, 2: 1, 3: 2, 4: 2}
        workcenters = [_workcenter(i, wc_plant_map[i]) for i in range(1, 5)]
        await self._merge_nodes(workcenters)

        people_data = [
            ("USR-BUYER-001", "Alice Chen", "Buyer", "alice@sc.example", "APAC"),
            ("USR-LC-001", "Bob Martinez", "LogisticsCoordinator", "bob@sc.example", "AMER"),
            ("USR-WM-001", "Carol Williams", "WarehouseManager", "carol@sc.example", "EMEA"),
            ("USR-QC-001", "David Kim", "QCInspector", "david@sc.example", "APAC"),
            ("USR-PLN-001", "Eve Thompson", "Planner", "eve@sc.example", "AMER"),
            ("USR-SFS-001", "Frank Lee", "ShopFloorSupervisor", "frank@sc.example", "EMEA"),
            ("USR-SCM-001", "Grace Patel", "SupplyChainManager", "grace@sc.example", "GLOBAL"),
        ]
        people = [_person(*p) for p in people_data]
        await self._merge_nodes(people)

        materials = _build_materials()
        await self._merge_nodes(materials)

        pos_data = _build_purchase_orders(suppliers)
        await self._merge_nodes(pos_data)

        pol_list = _build_po_lines(pos_data)
        await self._merge_nodes(pol_list)

        bom_components_data = [
            [{"material_id": "MAT-RAW-001", "qty_per": "2.5", "uom": "KG"},
             {"material_id": "MAT-RAW-004", "qty_per": "1.0", "uom": "M"},
             {"material_id": "MAT-SFG-001", "qty_per": "4.0", "uom": "EA"}],
            [{"material_id": "MAT-RAW-002", "qty_per": "3.0", "uom": "KG"},
             {"material_id": "MAT-RAW-003", "qty_per": "0.5", "uom": "KG"},
             {"material_id": "MAT-SFG-002", "qty_per": "2.0", "uom": "EA"}],
            [{"material_id": "MAT-RAW-005", "qty_per": "1.5", "uom": "KG"},
             {"material_id": "MAT-SFG-005", "qty_per": "3.0", "uom": "EA"}],
            [{"material_id": "MAT-RAW-007", "qty_per": "0.8", "uom": "KG"},
             {"material_id": "MAT-SFG-007", "qty_per": "2.0", "uom": "EA"},
             {"material_id": "MAT-RAW-009", "qty_per": "1.2", "uom": "L"}],
        ]
        fg_ids = ["MAT-FG-001", "MAT-FG-002", "MAT-FG-003", "MAT-FG-004"]
        boms = [_bom(i, fg_ids[i - 1], f"v{i}.0", bom_components_data[i - 1]) for i in range(1, 5)]
        await self._merge_nodes(boms)

        asns = _build_asns(pos_data, carriers)
        await self._merge_nodes(asns)

        shipments = _build_shipments(asns)
        await self._merge_nodes(shipments)

        containers = _build_containers(shipments)
        await self._merge_nodes(containers)

        customs_entries = _build_customs_entries(shipments)
        await self._merge_nodes(customs_entries)

        docks = [_dock(i, "WH-001") for i in range(1, 4)]
        await self._merge_nodes(docks)

        grns = _build_grns(pos_data, asns)
        await self._merge_nodes(grns)

        qis = _build_quality_inspections(grns)
        await self._merge_nodes(qis)

        bins = [_bin(i, "WH-001") for i in range(1, 31)]
        await self._merge_nodes(bins)

        stock_lots = _build_stock_lots(materials, bins)
        await self._merge_nodes(stock_lots)

        prod_orders = _build_production_orders(fg_ids, boms)
        await self._merge_nodes(prod_orders)

        mat_issues = _build_material_issues(prod_orders, materials, bins, workcenters)
        await self._merge_nodes(mat_issues)

        signal_bus = _signal_bus()
        orchestrator = _orchestrator()
        await self._merge_node(signal_bus)
        await self._merge_node(orchestrator)

        return {
            "shopfloors": shopfloors, "workcenters": workcenters, "pos_data": pos_data,
            "pol_list": pol_list, "boms": boms, "asns": asns, "shipments": shipments,
            "containers": containers, "customs_entries": customs_entries, "docks": docks,
            "grns": grns, "qis": qis, "bins": bins, "stock_lots": stock_lots,
            "prod_orders": prod_orders, "mat_issues": mat_issues,
        }

    # Function: _seed_edges
    async def _seed_edges(self, ds: dict[str, list[dict[str, Any]]]) -> None:
        shopfloors = ds["shopfloors"]
        workcenters = ds["workcenters"]
        pos_data = ds["pos_data"]
        pol_list = ds["pol_list"]
        boms = ds["boms"]
        asns = ds["asns"]
        shipments = ds["shipments"]
        containers = ds["containers"]
        customs_entries = ds["customs_entries"]
        docks = ds["docks"]
        grns = ds["grns"]
        qis = ds["qis"]
        bins = ds["bins"]
        stock_lots = ds["stock_lots"]
        prod_orders = ds["prod_orders"]
        mat_issues = ds["mat_issues"]

        await self._merge_edges([(po["supplier_id"], po["id"], "flow", "fulfills") for po in pos_data])
        await self._merge_edges([(pol["po_id"], pol["id"], "flow", "contains") for pol in pol_list])
        await self._merge_edges([(asn["po_id"], asn["id"], "flow", "triggers") for asn in asns])
        await self._merge_edges([(asn["id"], asn["carrier_id"], "flow", "carried_by") for asn in asns])
        await self._merge_edges([(shp["asn_id"], shp["id"], "flow", "ships_via") for shp in shipments])
        await self._merge_edges([
            (shp["id"], docks[i % len(docks)]["id"], "flow", "arrives_at")
            for i, shp in enumerate(shipments)
        ])
        await self._merge_edges([(cnt["shipment_id"], cnt["id"], "meta", "includes") for cnt in containers])
        await self._merge_edges([(ce["shipment_id"], ce["id"], "flow", "cleared_by") for ce in customs_entries])
        await self._merge_edges([(grn["id"], grn["po_id"], "flow", "receives_against") for grn in grns])
        await self._merge_edges([(grn["id"], grn["asn_id"], "flow", "receives_against") for grn in grns])
        await self._merge_edges([(qi["grn_id"], qi["id"], "flow", "triggers") for qi in qis])
        await self._merge_edges([
            (qi["id"], bins[i % len(bins)]["id"], "flow", "putaway_to")
            for i, qi in enumerate(qis)
        ])
        await self._merge_edges([(sl["bin_id"], sl["id"], "meta", "holds") for sl in stock_lots])
        await self._merge_edges([(sl["id"], sl["material_id"], "meta", "instance_of") for sl in stock_lots])
        await self._merge_edges([
            (prd["id"], boms[i % len(boms)]["id"], "meta", "uses")
            for i, prd in enumerate(prod_orders)
        ])
        await self._merge_edges([(mi["production_order_id"], mi["id"], "flow", "requests") for mi in mat_issues])
        await self._merge_edges([
            (mi["id"], stock_lots[i % len(stock_lots)]["id"], "flow", "consumes")
            for i, mi in enumerate(mat_issues)
        ])
        await self._merge_edges([(mi["id"], mi["dest_workcenter_id"], "flow", "feeds") for mi in mat_issues])
        await self._merge_edges([(wc["id"], wc["shopfloor_id"], "meta", "belongs_to") for wc in workcenters])
        await self._merge_bom_specifies_edges(boms)

        await self._merge_edges([("USR-BUYER-001", po["id"], "owns", "creates") for po in pos_data])
        await self._merge_edges([("USR-LC-001", shp["id"], "owns", "tracks") for shp in shipments])
        await self._merge_edges([("USR-WM-001", grn["id"], "owns", "oversees") for grn in grns])
        await self._merge_edges([("USR-QC-001", qi["id"], "owns", "performs") for qi in qis])
        await self._merge_edges([("USR-PLN-001", prd["id"], "owns", "releases") for prd in prod_orders])
        await self._merge_edges([("USR-SFS-001", wc["id"], "owns", "runs") for wc in workcenters])
        await self._merge_edges([("USR-SCM-001", sf["id"], "owns", "pnl_for") for sf in shopfloors])

        await self._merge_edge("BUS-001", "ORC-001", "meta", "managed_by")

    # Function: load
    async def load(self) -> dict[str, int]:
        log.info("seed_start")

        datasets = await self._seed_nodes()

        log.info("seed_nodes_done", count=self._node_count)

        await self._seed_edges(datasets)

        log.info("seed_edges_done", count=self._edge_count)
        log.info("seed_complete", nodes=self._node_count, edges=self._edge_count)

        return {"nodes": self._node_count, "edges": self._edge_count}
