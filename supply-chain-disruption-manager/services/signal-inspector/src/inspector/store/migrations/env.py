# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Alembic environment configuration for async SQLAlchemy.
# Date: 2026-06-27
# ---------------------------------------------------------------------------
"""Alembic environment configuration for async SQLAlchemy."""

from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Import models to register them with Base.metadata
from inspector.store.models import Base  # noqa: F401

config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


# Function: get_url
def get_url() -> str:
    """Return the database URL from environment or alembic.ini."""
    return os.environ.get(
        "POSTGRES_URL",
        config.get_main_option("sqlalchemy.url", ""),
    )


# Function: run_migrations_offline
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode without a DB connection."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# Function: do_run_migrations
def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


# Function: run_async_migrations
async def run_async_migrations() -> None:
    """Run migrations in 'online' async mode."""
    cfg = config.get_section(config.config_ini_section, {})
    cfg["sqlalchemy.url"] = get_url()

    connectable = async_engine_from_config(
        cfg,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


# Function: run_migrations_online
def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
