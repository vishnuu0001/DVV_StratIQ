.PHONY: help up down seed demo test lint build logs clean

COMPOSE=docker compose
ENV_FILE=.env

help:
	@echo ""
	@echo "Supply Chain Disruption Manager"
	@echo "================================"
	@echo "make up       — Start all services"
	@echo "make down     — Stop all services"
	@echo "make seed     — Seed KG + event data"
	@echo "make demo     — Full end-to-end demo"
	@echo "make test     — Run all tests"
	@echo "make lint     — Run linters"
	@echo "make build    — Build all images"
	@echo "make logs     — Tail all logs"
	@echo "make clean    — Remove volumes + containers"
	@echo ""

up:
	@cp -n .env.example .env 2>/dev/null || true
	$(COMPOSE) up -d
	@echo "Waiting for services..."
	@sleep 10
	@$(COMPOSE) ps

down:
	$(COMPOSE) down

build:
	$(COMPOSE) build --no-cache

seed:
	@echo "Seeding Knowledge Graph..."
	@curl -s -X POST http://localhost:8001/seed \
		-H "X-API-Key: $$(grep KG_API_KEY .env | cut -d= -f2)" \
		-H "Content-Type: application/json" | python -m json.tool
	@echo ""
	@echo "Seeding canonical events..."
	@for f in seed/events/*.json; do \
		echo "  Posting $$f..."; \
		curl -s -X POST http://localhost:8003/ingest/manual \
			-H "Content-Type: application/json" \
			-d @$$f > /dev/null; \
	done
	@echo "Seed complete."

demo: up
	@sleep 15
	@$(MAKE) seed
	@echo ""
	@echo "Triggering supplier delay scenario..."
	@curl -s -X POST http://localhost:8002/disruption \
		-H "X-API-Key: $$(grep AGENT_API_KEY .env | cut -d= -f2)" \
		-H "Content-Type: application/json" \
		-d @seed/scenarios/supplier_delay_trigger.json | python -m json.tool
	@echo ""
	@echo "Demo running. Open http://localhost:5173 to view the UI."

test:
	@echo "Running KG service tests..."
	$(COMPOSE) run --rm kg-service pytest tests/ -v --tb=short
	@echo "Running Signal Inspector tests..."
	$(COMPOSE) run --rm signal-inspector pytest tests/ -v --tb=short
	@echo "Running Agent Service tests..."
	$(COMPOSE) run --rm agent-service pytest tests/ -v --tb=short

test-local:
	cd services/kg-service && python -m pytest tests/ -v --tb=short
	cd services/signal-inspector && python -m pytest tests/ -v --tb=short
	cd services/agent-service && python -m pytest tests/ -v --tb=short

lint:
	@echo "Linting KG service..."
	cd services/kg-service && ruff check src/ && mypy --strict src/
	@echo "Linting Signal Inspector..."
	cd services/signal-inspector && ruff check src/ && mypy --strict src/
	@echo "Linting Agent Service..."
	cd services/agent-service && ruff check src/ && mypy --strict src/
	@echo "Linting Web UI..."
	cd apps/web-ui && npm run type-check

logs:
	$(COMPOSE) logs -f

logs-kg:
	$(COMPOSE) logs -f kg-service

logs-inspector:
	$(COMPOSE) logs -f signal-inspector

logs-agent:
	$(COMPOSE) logs -f agent-service

logs-ui:
	$(COMPOSE) logs -f web-ui

clean:
	$(COMPOSE) down -v --remove-orphans
	docker system prune -f

ps:
	$(COMPOSE) ps

restart-%:
	$(COMPOSE) restart $*

health:
	@echo "KG Service:"; curl -s http://localhost:8001/health | python -m json.tool
	@echo "Agent Service:"; curl -s http://localhost:8002/health | python -m json.tool
	@echo "Signal Inspector:"; curl -s http://localhost:8003/health | python -m json.tool
