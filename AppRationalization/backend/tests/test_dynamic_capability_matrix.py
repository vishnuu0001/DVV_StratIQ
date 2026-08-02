import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.services import ollama_service
from app.services.ollama_service import OllamaService
from app.services.technical_assessment_service import _dynamic_matrix_headers, _sanitize_market_payload


class DynamicCapabilityMatrixTests(unittest.TestCase):
    @patch("app.services.ollama_service.requests.get")
    def test_global_search_extracts_public_result_text(self, get):
        response = Mock()
        response.headers = {"content-type": "text/html"}
        response.text = (
            '<a class="result__a">Alarm management standard</a>'
            '<div class="result__snippet">Alarm management includes dynamic flood suppression.</div>'
        )
        response.raise_for_status.return_value = None
        get.return_value = response

        with patch.object(ollama_service, "MARKET_SEARCH_URL", "https://search.example.test"):
            evidence = ollama_service._global_market_search("alarm management capabilities")

        self.assertEqual(2, len(evidence))
        self.assertIn("dynamic flood suppression", evidence[1])

    @patch.object(OllamaService, "generate_market_product_enrichment")
    @patch("app.services.ollama_service._generate")
    @patch("app.services.ollama_service._global_market_search")
    @patch("app.services.ollama_service._available_model", return_value="test-model")
    def test_discovers_columns_then_validates_every_product(
        self, _model, search, generate, enrich,
    ):
        search.side_effect = lambda query: [f"Evidence for {query}"]
        generate.return_value = json.dumps({
            "capabilities": ["ISA-18.2 Compliance", "Dynamic Alarm Flood Handling"]
        })
        enrich.return_value = {
            "1": {"ISA-18.2 Compliance": "Yes"},
            "2": {"ISA-18.2 Compliance": "No"},
        }
        products = [
            {"id": 1, "product": "Product A", "size": "S"},
            {"id": 2, "product": "Product B", "size": "M"},
        ]

        matrix = OllamaService.discover_market_capability_matrix("Alarm Management", products)

        self.assertEqual(
            ["ISA-18.2 Compliance", "Dynamic Alarm Flood Handling"],
            matrix["capabilities"],
        )
        self.assertEqual(5, search.call_count)  # topic, broad product search, then capability-specific validation
        validated_products = enrich.call_args.args[1]
        self.assertEqual({"1", "2"}, {str(item["id"]) for item in validated_products})
        self.assertTrue(all(item["market_evidence"] for item in validated_products))

    def test_dashboard_schema_comes_from_enrichment_not_uploaded_columns(self):
        rows = [
            SimpleNamespace(to_dict=lambda: {
                "enrichment_payload": {
                    "_matrix_schema_version": 2,
                    "ISA-18.2 Compliance": "Yes",
                    "Dynamic Alarm Flood Handling": "No",
                    "COTS / Available in Market / Custom Products": "COTS",
                }
            })
        ]

        capabilities, product_types = _dynamic_matrix_headers(rows)

        self.assertEqual(["ISA-18.2 Compliance", "Dynamic Alarm Flood Handling"], capabilities)
        self.assertEqual(["COTS / Available in Market / Custom Products"], product_types)
        self.assertEqual(
            {"ISA-18.2 Compliance": "Yes"},
            _sanitize_market_payload({"ISA-18.2 Compliance": "supported"}, ["ISA-18.2 Compliance"]),
        )
        self.assertEqual(
            {"ISA-18.2 Compliance": "No"},
            _sanitize_market_payload(
                {"ISA-18.2 Compliance": "does not provide compliance support"},
                ["ISA-18.2 Compliance"],
            ),
        )


if __name__ == "__main__":
    unittest.main()
