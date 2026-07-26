# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Novastra-ITSM — tests (test_ticket_picker_search.py)
# Date: 2026-02-14
# ---------------------------------------------------------------------------
from __future__ import annotations

import unittest
from unittest.mock import patch

from backend.api import tickets


class TicketPickerSearchTests(unittest.IsolatedAsyncioTestCase):
    # Function: test_uses_operational_store_with_true_total
    async def test_uses_operational_store_with_true_total(self):
        calls = []

        # Function: fake_get_all_incidents
        def fake_get_all_incidents(*, limit, offset, search=None, **_kwargs):
            calls.append((limit, offset, search))
            return ([{"number": "INC0099999", "short_description": "Database timeout"}], 5003)

        with patch.object(tickets, "get_all_incidents", fake_get_all_incidents):
            result = await tickets.search_tickets(
                q="database", limit=100, offset=100, current_user={"username": "admin"},
            )

        self.assertEqual(calls, [(100, 100, "database")])
        self.assertEqual(result["source"], "operational_store")
        self.assertEqual(result["total"], 5003)
        self.assertTrue(result["has_more"])
        self.assertEqual(result["tickets"][0]["number"], "INC0099999")

    # Function: test_falls_back_to_samples_when_store_unavailable
    async def test_falls_back_to_samples_when_store_unavailable(self):
        # Function: unavailable
        def unavailable(**_kwargs):
            raise RuntimeError("database not configured")

        with patch.object(tickets, "get_all_incidents", unavailable):
            result = await tickets.search_tickets(
                q="VPN", limit=5, offset=0, current_user={"username": "admin"},
            )

        self.assertEqual(result["source"], "sample_fallback")
        self.assertGreaterEqual(result["total"], 1)
        self.assertEqual(result["tickets"][0]["number"], "INC0012345")


if __name__ == "__main__":
    unittest.main()
