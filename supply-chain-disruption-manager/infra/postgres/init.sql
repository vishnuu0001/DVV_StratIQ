-- Signal Inspector + Agent Service share the same Postgres instance.
-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Signal Inspector schema is applied via Alembic in signal-inspector service.
-- Agent Service schema is applied via Alembic in agent-service.
-- This file just ensures the DB is ready with extensions.
