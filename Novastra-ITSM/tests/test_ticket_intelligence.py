from __future__ import annotations

import asyncio
import json
import unittest
from unittest.mock import patch

from fastapi import HTTPException

from backend.api.ticket_intelligence import classify_ticket, summarize_thread


class TicketIntelligenceClassificationTests(unittest.TestCase):
    def test_classification_returns_validated_ollama_result(self):
        response = {
            "category": "Hardware",
            "subcategory": "Laptop Replacement",
            "priority": "P4",
            "urgency": "low",
            "assignment_group": "End User Computing",
            "confidence": 0.92,
            "reasoning": "The user requests lifecycle replacement of an out-of-warranty laptop.",
        }
        with patch(
            "backend.api.ticket_intelligence._call_llm",
            return_value=json.dumps(response),
        ), patch("backend.api.ticket_intelligence.cfg.OLLAMA_MODEL", "qwen2.5-coder:7b"):
            result = asyncio.run(classify_ticket(
                {"title": "Request new laptop", "description": "Old device is out of warranty"},
                {"username": "tester"},
            ))

        self.assertTrue(result["llm_used"])
        self.assertEqual(result["provider"], "ollama")
        self.assertEqual(result["model"], "qwen2.5-coder:7b")
        self.assertEqual(result["category"], "Hardware")
        self.assertEqual(result["urgency"], "Low")

    def test_classification_never_returns_heuristic_on_ollama_failure(self):
        with patch(
            "backend.api.ticket_intelligence._call_llm",
            side_effect=RuntimeError("runtime unavailable"),
        ), patch("backend.api.ticket_intelligence.cfg.OLLAMA_MODEL", "qwen2.5-coder:7b"):
            with self.assertRaises(HTTPException) as raised:
                asyncio.run(classify_ticket(
                    {"title": "Request new laptop", "description": "Old device is out of warranty"},
                    {"username": "tester"},
                ))

        self.assertEqual(raised.exception.status_code, 503)
        self.assertIn("No heuristic classification was returned", raised.exception.detail)


class TicketIntelligenceSummaryTests(unittest.TestCase):
    def test_empty_thread_is_rejected_before_calling_ollama(self):
        with patch("backend.api.ticket_intelligence._call_llm") as llm:
            with self.assertRaises(HTTPException) as raised:
                asyncio.run(summarize_thread(
                    {"ticket_id": "INC0235904", "thread": [{"content": ""}]},
                    {"username": "tester"},
                ))
        self.assertEqual(raised.exception.status_code, 422)
        llm.assert_not_called()

    def test_grounded_summary_preserves_empty_actions(self):
        response = {
            "summary": "A replacement laptop is requested because the current laptop is out of warranty.",
            "key_actions": [],
            "next_steps": [],
        }
        with patch(
            "backend.api.ticket_intelligence._call_llm",
            return_value=json.dumps(response),
        ), patch("backend.api.ticket_intelligence.cfg.OLLAMA_MODEL", "qwen2.5-coder:7b"):
            result = asyncio.run(summarize_thread(
                {
                    "ticket_id": "INC0235904",
                    "thread": [{
                        "author": "Requester",
                        "content": "Request new laptop; the current laptop is out of warranty.",
                    }],
                },
                {"username": "tester"},
            ))
        self.assertEqual(result["key_actions"], [])
        self.assertEqual(result["next_steps"], [])
        self.assertTrue(result["llm_used"])

    def test_unrelated_summary_is_rejected(self):
        response = {
            "summary": "The account is locked after repeated password failures.",
            "key_actions": ["Confirmed account lock"],
            "next_steps": ["Reset password"],
        }
        with patch(
            "backend.api.ticket_intelligence._call_llm",
            return_value=json.dumps(response),
        ):
            with self.assertRaises(HTTPException) as raised:
                asyncio.run(summarize_thread(
                    {
                        "ticket_id": "INC0235904",
                        "thread": [{"content": "Request a replacement laptop because it is out of warranty."}],
                    },
                    {"username": "tester"},
                ))
        self.assertEqual(raised.exception.status_code, 503)

    def test_malformed_ollama_response_is_rejected(self):
        with patch(
            "backend.api.ticket_intelligence._call_llm",
            return_value='{"category":"Hardware"}',
        ):
            with self.assertRaises(HTTPException) as raised:
                asyncio.run(classify_ticket(
                    {"title": "Request new laptop", "description": "Old device is out of warranty"},
                    {"username": "tester"},
                ))

        self.assertEqual(raised.exception.status_code, 503)


if __name__ == "__main__":
    unittest.main()
