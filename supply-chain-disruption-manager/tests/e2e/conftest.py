# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: E2E test configuration. Requires all services running.
# Date: 2026-01-23
# ---------------------------------------------------------------------------
"""E2E test configuration. Requires all services running."""
import pytest


# Function: pytest_configure
def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "e2e: marks tests as E2E requiring all services")


# Function: pytest_collection_modifyitems
def pytest_collection_modifyitems(items: list) -> None:
    for item in items:
        item.add_marker(pytest.mark.e2e)
