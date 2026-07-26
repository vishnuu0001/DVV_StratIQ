# Supply Chain Disruption Manager

An autonomous, end-to-end Supply Chain Disruption Management platform built on the **Sense → Understand → Act** architecture.

```
╔══════════════════════════════════════════════════════════════════╗
║          SUPPLY CHAIN DISRUPTION MANAGER                        ║
║  ┌────────────┐  ┌────────────────┐  ┌────────────────────┐    ║
║  │   SENSE    │  │  UNDERSTAND    │  │       ACT          │    ║
║  │  Signal    │→ │  Knowledge     │→ │  Agentic System    │    ║
║  │  Inspector │  │  Graph (Neo4j) │  │  (Orchestrator +   │    ║
║  │            │  │                │  │   7 Specialists)   │    ║
║  └────────────┘  └────────────────┘  └────────────────────┘    ║
╚══════════════════════════════════════════════════════════════════╝
```

## What it does

1. **Ingests** disruption signals from ERP, WMS, TMS, supplier portals, MES/MQTT
2. **Normalizes** them into a canonical event envelope (validated, deduplicated, enriched, severity-scored)
3. **Publishes** to Redis Streams partitioned by domain (`disruption.*`)
4. **Traverses** the Supply Chain Knowledge Graph to compute downstream blast radius
5. **Dispatches** specialist agents (Buyer, Logistics, Warehouse, Quality, Inventory, Planning, Shop-floor)
6. **Creates** a full incident record with plan, specialist outputs, and audit trail
7. **Escalates** irreversible decisions to humans for approval
8. **Visualizes** everything in a dark-mode, executive-grade operational UI

---

## Quick Start

### Windows localhost/IIS path

Docker is optional. For a Windows-local run, install Python 3.11+, Node.js 20+,
Neo4j, PostgreSQL, Redis, and IIS URL Rewrite. Then run:

```powershell
Copy-Item .env.localhost .env -Force
.\scripts\Install-Local.ps1
& ".\Start+Services.ps1"
```

Open http://localhost:5173 for the Vite-hosted UI.
After code changes, run `& ".\Start+Services.ps1" -RestartApps` to recycle the local app processes.

Seed and trigger the demo:

```powershell
.\scripts\Seed-Local.ps1
```

Build the static UI for IIS:

```powershell
.\scripts\Build-IIS.ps1
.\scripts\Start-Local.ps1 -SkipUi
```

See [LOCAL_IIS_RUNBOOK.md](LOCAL_IIS_RUNBOOK.md) for the full Windows/IIS setup.

### Docker path

If Docker Desktop is available, the original Compose workflow still works:

```bash
cp .env.example .env
make up
```

Services:
| Service | URL |
|---------|-----|
| Web UI | http://localhost:5173 |
| KG Service | http://localhost:8001 |
| Agent Service | http://localhost:8002 |
| Signal Inspector | http://localhost:8003 |
| Neo4j Browser | http://localhost:7474 |

Seed data:

```bash
make seed
```

This seeds:
- 200+ KG nodes (5 suppliers, 25 materials, 20 POs, 18 shipments, 80 stock lots, 12 production orders, ...)
- 6 canonical disruption events (one per scenario type)

Run full demo:

```bash
make demo
```

This runs `up` → `seed` → triggers a supplier delay scenario → creates a full incident.

Open http://localhost:5173 to watch it happen in the UI.

Check health:

```bash
make health
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Docker Compose                               │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                        Web UI (React 18 + Vite)              │   │
│  │         http://localhost:5173                                  │   │
│  └────────────┬──────────────────┬──────────────────────────────┘   │
│               │                  │                                    │
│  ┌────────────▼───┐  ┌──────────▼──────────┐  ┌──────────────────┐ │
│  │  KG Service    │  │  Signal Inspector    │  │  Agent Service   │ │
│  │  FastAPI:8001  │  │  FastAPI:8003        │  │  FastAPI:8002    │ │
│  │  Neo4j client  │  │  Adapters+Normalizer │  │  Orchestrator    │ │
│  └────────────────┘  └──────────┬───────────┘  └──────────▲───────┘ │
│         │                       │                          │          │
│  ┌──────▼──────┐       ┌────────▼──────────────────────────┘         │
│  │  Neo4j 5   │       │         Redis 7 Streams                     │ │
│  │  bolt:7687 │       │  disruption.* | events.invalid | incident.* │ │
│  └────────────┘       └──────────────────────────────────────────────┘ │
│                                         │                               │
│                              ┌──────────▼───────┐                       │
│                              │   Postgres 16    │                       │
│                              │  canonical_events │                       │
│                              │  incidents        │                       │
│                              └──────────────────┘                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Services

| Service | Port | Owns |
|---------|------|------|
| `kg-service` | 8001 | Neo4j schema, entity CRUD, traversal, owners, seed loader |
| `signal-inspector` | 8003 | Adapters, normalizer pipeline, Redis publish, event audit (Postgres), SSE |
| `agent-service` | 8002 | Incident state machine, orchestrator, 7 specialists, human approval API |
| `web-ui` | 5173 | React operational control tower |

### Infrastructure

| Service | Port | Purpose |
|---------|------|---------|
| Neo4j | 7474 (HTTP), 7687 (Bolt) | Knowledge Graph |
| Postgres 16 | 5432 | Event audit + incident records |
| Redis 7 | 6379 | Event bus (Streams) |

---

## API Reference

### KG Service (port 8001)

All KG endpoints require `X-API-Key` header.

```bash
# Health
curl http://localhost:8001/health

# Get entity
curl -H "X-API-Key: kg-dev-key-change-in-prod" \
     http://localhost:8001/entity/Supplier/SUP-001

# Traverse blast radius
curl -H "X-API-Key: kg-dev-key-change-in-prod" \
     "http://localhost:8001/traverse?root_id=SUP-001&edge_kinds=flow,meta&direction=outbound&max_depth=6"

# Get owners
curl -H "X-API-Key: kg-dev-key-change-in-prod" \
     "http://localhost:8001/owners?node_id=PO-10001&include_transitive=true"

# Search
curl -H "X-API-Key: kg-dev-key-change-in-prod" \
     -d '{"query": "steel", "kind": "Material"}' \
     http://localhost:8001/search

# Seed
curl -X POST -H "X-API-Key: kg-dev-key-change-in-prod" \
     http://localhost:8001/seed
```

### Signal Inspector (port 8003)

```bash
# Health
curl http://localhost:8003/health

# Ingest manual event
curl -X POST http://localhost:8003/ingest/manual \
     -H "Content-Type: application/json" \
     -d @seed/events/supplier_delay.json

# List events
curl "http://localhost:8003/events?severity=high&limit=20"

# Live SSE stream
curl -N http://localhost:8003/events/stream

# Replay event
curl -X POST http://localhost:8003/event/{event_id}/replay

# List adapters
curl http://localhost:8003/adapters

# Schema browser
curl http://localhost:8003/schemas
curl http://localhost:8003/schemas/supplier.po.delayed
```

### Agent Service (port 8002)

All Agent endpoints require `X-API-Key` header.

```bash
# Health
curl -H "X-API-Key: agent-dev-key-change-in-prod" \
     http://localhost:8002/health

# Trigger disruption
curl -X POST http://localhost:8002/disruption \
     -H "X-API-Key: agent-dev-key-change-in-prod" \
     -H "Content-Type: application/json" \
     -d @seed/scenarios/supplier_delay_trigger.json

# List incidents
curl -H "X-API-Key: agent-dev-key-change-in-prod" \
     "http://localhost:8002/incidents?state=AWAITING_APPROVAL"

# Get incident detail
curl -H "X-API-Key: agent-dev-key-change-in-prod" \
     http://localhost:8002/incident/{id}

# Get incident timeline
curl -H "X-API-Key: agent-dev-key-change-in-prod" \
     http://localhost:8002/incident/{id}/timeline

# Approve incident
curl -X POST http://localhost:8002/incident/{id}/approve \
     -H "X-API-Key: agent-dev-key-change-in-prod" \
     -H "Content-Type: application/json" \
     -d '{"reason": "Plan accepted", "decided_by": "SCM-001"}'

# Reject incident
curl -X POST http://localhost:8002/incident/{id}/reject \
     -H "X-API-Key: agent-dev-key-change-in-prod" \
     -H "Content-Type: application/json" \
     -d '{"reason": "Need cheaper alternative sourcing option", "decided_by": "SCM-001"}'

# Live SSE stream
curl -N -H "X-API-Key: agent-dev-key-change-in-prod" \
     http://localhost:8002/incidents/stream
```

---

## Disruption Scenarios

Trigger from the UI left rail or via API/curl.

### 1. Supplier Delay
```bash
curl -X POST http://localhost:8002/disruption \
     -H "X-API-Key: agent-dev-key-change-in-prod" \
     -H "Content-Type: application/json" \
     -d @seed/scenarios/supplier_delay_trigger.json
```
- Root: SUP-001 (Apex Steel)
- Severity: high
- Agents: Buyer, Logistics, Inventory, Planning
- Human approval: required

### 2. ETA Slip
```bash
curl -X POST http://localhost:8003/ingest/manual \
     -H "Content-Type: application/json" \
     -d @seed/events/eta_slip.json
```
- Root: SHP-30007
- Severity: med/high
- Agents: Logistics, Warehouse, Planning

### 3. QC Rejection
```bash
curl -X POST http://localhost:8003/ingest/manual \
     -H "Content-Type: application/json" \
     -d @seed/events/qc_reject.json
```
- Root: QC-60003
- Severity: high (defect rate 16%)
- Agents: Quality, Buyer, Inventory, Planning

### 4. Customs Hold
```bash
curl -X POST http://localhost:8003/ingest/manual \
     -H "Content-Type: application/json" \
     -d @seed/events/customs_hold.json
```
- Root: CUS-40001
- Severity: med
- Agents: Logistics, Buyer

### 5. Short Pick
```bash
curl -X POST http://localhost:8003/ingest/manual \
     -H "Content-Type: application/json" \
     -d @seed/events/short_pick.json
```
- Root: ISS-90005
- Severity: high
- Agents: Warehouse, Planning, Shop-floor

### 6. Demand Spike
```bash
curl -X POST http://localhost:8003/ingest/manual \
     -H "Content-Type: application/json" \
     -d @seed/events/demand_spike.json
```
- Root: MAT-FG-002
- Severity: high (65% spike, below safety stock)
- Agents: Planning, Buyer, Logistics, Inventory

---

## UI Views

| Route | View |
|-------|------|
| `/` | Executive Overview |
| `/stream` | Live Signal Stream |
| `/graph` | Knowledge Graph |
| `/incidents` | Incident Command Center |
| `/agents` | Agent Workbench |
| `/adapters` | Adapter Operations |
| `/schemas` | Schema Browser |
| `/replay` | Replay & DLQ |

---

## Testing

```bash
# All tests (requires running services)
make test

# E2E tests only
pytest tests/e2e/ -v --timeout=120

# Service-specific unit tests
cd services/kg-service && pytest tests/ -v
cd services/signal-inspector && pytest tests/ -v
cd services/agent-service && pytest tests/ -v
```

---

## Configuration

Environment variables in `.env`:

| Variable | Default | Purpose |
|----------|---------|---------|
| `KG_API_KEY` | `kg-dev-key-change-in-prod` | Auth for KG service |
| `AGENT_API_KEY` | `agent-dev-key-change-in-prod` | Auth for Agent service |
| `INSPECTOR_ERP_HMAC_SECRET` | `erp-hmac-secret-change-in-prod` | HMAC for ERP webhook |
| `MOCK_AGENTS` | `true` | Use deterministic mock agents (no LLM key needed) |
| `ANTHROPIC_API_KEY` | _(none)_ | Set to use real Claude models |
| `ORCHESTRATOR_MODEL` | `claude-opus-4-8` | LLM model for orchestrator |
| `SPECIALIST_MODEL` | `claude-sonnet-4-6` | LLM model for specialists |
| `NEO4J_PASSWORD` | `disruption123` | Neo4j password |
| `POSTGRES_PASSWORD` | `sc_secret` | Postgres password |

### Using Real LLM Agents

By default, `MOCK_AGENTS=true` so the system works without an Anthropic API key. To enable real Claude models:

```bash
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
echo "MOCK_AGENTS=false" >> .env
docker compose restart agent-service
```

---

## Linting

```bash
make lint
```

Runs `ruff check` + `mypy --strict` on all Python services, and `tsc --noEmit` on the UI.

---

## Troubleshooting

**Neo4j takes too long to start:**
Wait 30–60 seconds after `make up`. Neo4j needs warm-up time. Run `make health` to check.

**Seed fails with connection error:**
Services may not be fully up. Wait 30s and retry: `make seed`.

**Events not appearing in UI stream:**
Check Redis is running (`docker compose ps redis`). Check SSE connection in browser DevTools Network tab.

**Agent service not consuming events:**
Check Redis consumer group: `docker compose exec redis redis-cli XINFO GROUPS disruption.supplier`

**KG traversal returns empty:**
Ensure seed was run. Check `GET /health` returns `node_count > 0`.

**UI blank / API errors:**
Check browser console for CORS errors. Ensure all three backend ports (8001, 8002, 8003) are accessible.

---

## Known Limitations (v1)

1. **No auth on Web UI** — single-user dev mode. Add OAuth/OIDC for multi-user.
2. **Redis Streams, not Kafka** — appropriate for local dev; replace with Kafka for production scale.
3. **Mock agents by default** — specialist tool outputs are realistic mocks. Wire real ERP/WMS/TMS adapters for production.
4. **No temporal KG** — current state only; no graph versioning or bitemporal queries.
5. **Single Neo4j node** — Community edition, no clustering or HA.
6. **No RBAC** — API key auth only; no per-user role enforcement.
7. **LLM costs unbounded** — add per-incident cost tracking and budget caps for production.

---

## Next Production Hardening Steps

1. **Replace Redis Streams with Kafka** for partition-resilient, replay-capable event bus
2. **Add Keycloak/Auth0** for UI SSO and per-role API permissions
3. **Neo4j Enterprise** with causal clustering for HA graph reads
4. **Implement real SoR adapters** — replace ERP/WMS/TMS mocks with real system API calls
5. **Add LLM prompt versioning** — version orchestrator/specialist prompts, eval on each change
6. **Instrument with OpenTelemetry** — traces per incident, dashboards in Grafana
7. **Implement bitemporal KG** — track both valid-time and transaction-time for audit
8. **Add cost guardrails** — per-incident LLM spend limit, circuit breaker
9. **Add suppression rules** — prevent duplicate incidents from noisy adapters
10. **Kubernetes Helm chart** — production deployment with horizontal scaling for agent workers

---

## Project Structure

```
supply-chain-disruption-manager/
├── docker-compose.yml
├── Makefile
├── README.md
├── .env.example
├── services/
│   ├── kg-service/          # FastAPI + Neo4j (port 8001)
│   ├── signal-inspector/    # FastAPI + Redis + Postgres (port 8003)
│   └── agent-service/       # FastAPI + Postgres + Redis (port 8002)
├── apps/
│   └── web-ui/              # React 18 + Vite + Tailwind (port 5173)
├── seed/
│   ├── kg/                  # KG reference data (suppliers, materials, people)
│   ├── events/              # Canonical event fixtures per scenario
│   └── scenarios/           # Scenario definitions + trigger payloads
├── infra/
│   └── postgres/            # DB init scripts
└── tests/
    └── e2e/                 # End-to-end test suite
```
