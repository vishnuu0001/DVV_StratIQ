# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Novastra-ITSM — tests (test_cmdb.py)
# Date: 2026-06-29
# ---------------------------------------------------------------------------
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
from fastapi import HTTPException
from pydantic import ValidationError

from backend.api.cmdb import CMDBQuery, IngestRequest, _fetch_table, ingest, nl_query
from backend.services import cmdb_store


class CMDBStoreTests(unittest.TestCase):
    # Function: setUp
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.original_path = cmdb_store.DB_PATH
        cmdb_store.DB_PATH = Path(self.tempdir.name) / "cmdb.sqlite3"

    # Function: tearDown
    def tearDown(self):
        cmdb_store.DB_PATH = self.original_path
        self.tempdir.cleanup()

    # Function: test_allowlist_rejects_unknown_field
    def test_allowlist_rejects_unknown_field(self):
        with self.assertRaises(ValidationError):
            CMDBQuery.model_validate({
                "entity": "ci",
                "filters": [{"field": "password", "operator": "equals", "value": "x"}],
            })

    # Function: test_query_operators_and_real_count
    def test_query_operators_and_real_count(self):
        cmdb_store.replace_entity("ci", [
            {"sys_id": "1", "name": "SERVER-01", "os": "Windows", "environment": "Production", "last_discovered": "2020-01-01T00:00:00+00:00"},
            {"sys_id": "2", "name": "SERVER-02", "os": "Linux", "environment": "Production", "last_discovered": "2099-01-01T00:00:00+00:00"},
        ])
        result = cmdb_store.query_records("ci", [
            {"field": "os", "operator": "contains", "value": "windows"},
            {"field": "environment", "operator": "equals", "value": "production"},
            {"field": "last_discovered", "operator": "older_than", "value": 90},
        ], 1, 50)
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["records"][0]["name"], "SERVER-01")

    # Function: test_related_ticket_search_and_pagination
    def test_related_ticket_search_and_pagination(self):
        cmdb_store.replace_entity("incident", [
            {"sys_id": "1", "number": "INC001", "short_description": "Outlook profile failure"},
            {"sys_id": "2", "number": "INC002", "short_description": "VPN issue"},
        ])
        result = cmdb_store.query_records("incident", [
            {"field": "short_description", "operator": "related_to", "value": "Outlook"},
        ], 1, 1)
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["pages"], 1)
        self.assertEqual(result["records"][0]["number"], "INC001")

    # Function: test_relationships_ignore_blank_cis
    def test_relationships_ignore_blank_cis(self):
        cmdb_store.replace_entity("relation", [
            {"sys_id": "1", "parent": "APP-01", "child": "DB-01", "type": "Depends on"},
            {"sys_id": "2", "parent": "", "child": "DB-02", "type": "Depends on"},
        ])
        result = cmdb_store.relationship_analysis()
        self.assertEqual(result["authoritative_relationship_count"], 1)

    # Function: test_license_uses_real_unit_cost
    def test_license_uses_real_unit_cost(self):
        cmdb_store.replace_entity("license", [
            {"sys_id": "1", "name": "M365", "rights": "100", "allocated": "40", "unit_cost": "120"},
        ])
        result = cmdb_store.license_analysis(1, 50)
        self.assertEqual(result["total_annual_saving_usd"], 7200)
        self.assertEqual(result["opportunities"][0]["reclaim_seats"], 60)

    # Function: test_validated_query_endpoint_executes_store
    def test_validated_query_endpoint_executes_store(self):
        cmdb_store.replace_entity("incident", [
            {"sys_id": "1", "number": "INC001", "short_description": "Outlook profile failure"},
        ])
        result = __import__("asyncio").run(nl_query({
            "query": "Outlook tickets",
            "structured_query": {"entity": "incident", "filters": [
                {"field": "short_description", "operator": "contains", "value": "Outlook"}
            ]},
            "page": 1,
            "page_size": 25,
        }, {"username": "tester"}))
        self.assertEqual(result["estimated_record_count"], 1)
        self.assertEqual(result["sample_results"][0]["number"], "INC001")

    # Function: test_ingestion_persists_all_requested_entities
    def test_ingestion_persists_all_requested_entities(self):
        request = IngestRequest(
            base_url="https://example.service-now.com",
            username="user",
            password="secret",
            tables=["ci", "relation", "incident", "change", "asset", "license"],
            verify_ssl=False,
        )

        # Function: fake_fetch
        async def fake_fetch(_client, _request, table, _fields):
            return [{"sys_id": f"{table}-1", "name": table}]

        with patch("backend.api.cmdb._fetch_table", new=AsyncMock(side_effect=fake_fetch)):
            result = __import__("asyncio").run(ingest(request, {"username": "tester"}))
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["total_records"], 6)
        self.assertEqual(set(result["counts"]), {"ci", "relation", "incident", "change", "asset", "license"})

    # Function: test_servicenow_401_is_not_reported_as_portal_session_401
    def test_servicenow_401_is_not_reported_as_portal_session_401(self):
        request = IngestRequest(
            base_url="https://example.service-now.com",
            username="user",
            password="invalid",
            tables=["ci"],
        )
        upstream_request = httpx.Request("GET", "https://example.service-now.com/api/now/table/cmdb_ci")
        client = AsyncMock()
        client.get.return_value = httpx.Response(401, request=upstream_request)

        with self.assertRaises(HTTPException) as raised:
            __import__("asyncio").run(_fetch_table(client, request, "cmdb_ci", "sys_id,name"))

        self.assertEqual(raised.exception.status_code, 502)
        self.assertIn("ServiceNow rejected", raised.exception.detail)

    # Function: test_ingest_returns_structured_failure_for_upstream_auth_error
    def test_ingest_returns_structured_failure_for_upstream_auth_error(self):
        request = IngestRequest(
            base_url="https://example.service-now.com",
            username="user",
            password="invalid",
            tables=["ci"],
        )
        failure = HTTPException(status_code=502, detail="ServiceNow rejected access to cmdb_ci")
        with patch("backend.api.cmdb._fetch_table", new=AsyncMock(side_effect=failure)):
            result = __import__("asyncio").run(ingest(request, {"username": "tester"}))

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["failed_table"], "cmdb_ci")
        self.assertIn("ci", result["errors"])


if __name__ == "__main__":
    unittest.main()
