# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Test configuration and fixtures using testcontainers for Neo4j.
# Date: 2026-02-22
# ---------------------------------------------------------------------------
"""Test configuration and fixtures using testcontainers for Neo4j."""
from __future__ import annotations

from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from testcontainers.neo4j import Neo4jContainer

# Override settings before importing app modules
import os

TEST_API_KEY = "test-api-key-12345"


# Function: neo4j_container
@pytest.fixture(scope="session")
def neo4j_container() -> Generator[Neo4jContainer, None, None]:
    """Start a Neo4j testcontainer for the entire test session."""
    with Neo4jContainer("neo4j:5.18-community") as container:
        yield container


# Function: neo4j_bolt_url
@pytest.fixture(scope="session")
def neo4j_bolt_url(neo4j_container: Neo4jContainer) -> str:
    return neo4j_container.get_connection_url()


# Function: set_env
@pytest.fixture(scope="session", autouse=True)
def set_env(neo4j_bolt_url: str) -> Generator[None, None, None]:
    """Set environment variables before importing the app."""
    os.environ["NEO4J_URI"] = neo4j_bolt_url
    os.environ["NEO4J_USER"] = "neo4j"
    os.environ["NEO4J_PASSWORD"] = "neo4j"
    os.environ["KG_API_KEY"] = TEST_API_KEY
    os.environ["KG_SEED_ENABLED"] = "true"
    os.environ["LOG_LEVEL"] = "WARNING"
    os.environ["ENVIRONMENT"] = "test"
    yield


# Function: app
@pytest_asyncio.fixture(scope="session")
async def app(set_env: None) -> AsyncGenerator[FastAPI, None]:
    """Build the FastAPI app with a live Neo4j testcontainer."""
    # Import after env vars are set so Settings picks them up
    import kg.config as cfg
    cfg._settings = None  # force re-read

    from kg.main import app as _app
    from kg.db import init_driver, close_driver

    await init_driver()
    yield _app
    await close_driver()


# Function: client
@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Async test client with auth header."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-API-Key": TEST_API_KEY},
    ) as c:
        yield c


# Function: unauthed_client
@pytest_asyncio.fixture
async def unauthed_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Async test client without auth header."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c
