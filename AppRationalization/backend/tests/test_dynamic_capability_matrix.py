import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.services import ollama_service
from app.services.ollama_service import OllamaService
from app.services.technical_assessment_service import _dynamic_matrix_headers, _sanitize_market_payload
from app.services.technical_assessment_service import _is_technical_evaluation_topic


class DynamicCapabilityMatrixTests(unittest.TestCase):
    def test_technical_evaluation_import_topic_filter(self):
        self.assertTrue(_is_technical_evaluation_topic("Harmonize Alarm Management Solutions"))
        self.assertTrue(_is_technical_evaluation_topic("  harmonize alarm management solutions  "))
        self.assertFalse(_is_technical_evaluation_topic("Harmonize ERP Solutions"))

    def test_alarm_discovery_uses_industrial_market_query(self):
        queries = ollama_service._market_topic_queries("Harmonize Alarm Management Solutions")

        self.assertTrue(any("EEMUA 191" in query for query in queries))
        self.assertFalse(any("home automation" in query.casefold() for query in queries))

    def test_uploaded_context_supplies_conservative_product_defaults(self):
        values = ollama_service._portfolio_evidence_defaults(
            {
                "context": {
                    "Application type": "Commercial of the shelf with major modifications",
                    "Rationale": "Supports plant alarm monitoring and operational alerts.",
                }
            },
            ["Alarm Monitoring", "Energy Management", "COTS / Available in Market / Custom Products"],
        )

        self.assertEqual("Yes", values["Alarm Monitoring"])
        self.assertNotIn("Energy Management", values)
        self.assertEqual("Hybrid", values["COTS / Available in Market / Custom Products"])

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

    @patch("app.services.ollama_service.requests.get")
    def test_global_search_extracts_searxng_result_text(self, get):
        response = Mock()
        response.headers = {"content-type": "text/html; charset=utf-8"}
        response.text = (
            '<article class="result result-default category-general">'
            '<h3><a><span class="highlight">Ollama</span></a></h3>'
            '<p class="content">Run local language models and search grounded evidence.</p>'
            '</article>'
        )
        response.raise_for_status.return_value = None
        get.return_value = response

        with patch.object(ollama_service, "MARKET_SEARCH_URL", "http://localhost:8080/search"):
            with patch.object(ollama_service, "MARKET_SEARCH_ENGINES", "bing,mwmbl"):
                evidence = ollama_service._global_market_search("Ollama capabilities")

        self.assertEqual(1, len(evidence))
        self.assertIn("search grounded evidence", evidence[0])
        self.assertEqual("bing,mwmbl", get.call_args.kwargs["params"]["engines"])

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
        # General + industrial-standard topic searches, broad product searches,
        # then capability-specific validation for each product.
        self.assertEqual(6, search.call_count)
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
