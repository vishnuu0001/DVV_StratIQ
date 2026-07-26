# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: TraceForge — api/alembic (env.py)
# Date: 2026-04-20
# ---------------------------------------------------------------------------
from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from traceforge.config import DATABASE_URL
from traceforge.db.models import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Alembic drives migrations synchronously — swap the app's asyncpg URL for
# psycopg2 here only; the running app still uses the async engine in db/session.py.
SYNC_DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")


# Function: run_migrations_offline
def run_migrations_offline() -> None:
    context.configure(
        url=SYNC_DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# Function: run_migrations_online
def run_migrations_online() -> None:
    connectable = engine_from_config(
        {"sqlalchemy.url": SYNC_DATABASE_URL},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
