import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.services import ollama_service
from app.services.ollama_service import OllamaService
from app.services.technical_assessment_service import (
    _dynamic_matrix_headers,
    _resolve_categorize_size,
    _sanitize_market_payload,
    enrich_technical_evaluation_categorize_topic,
)
from app.services.technical_assessment_service import _is_technical_evaluation_topic


class DynamicCapabilityMatrixTests(unittest.TestCase):
    def test_size_prefers_wave_input_id_then_calculates(self):
        row = SimpleNamespace(
            product="Example Alarm App",
            size=None,
            to_dict=lambda: {
                "row_payload": {
                    "Number": "APM001",
                    "Application type": "Commercial of the shelf",
                    "Architecture type": "No Platform Application",
                    "Install type": "On Premise",
                }
            },
        )

        self.assertEqual(("M", "wave_inputs"), _resolve_categorize_size(row, {"apm001": "M"}))
        self.assertEqual(("XS", "calculated"), _resolve_categorize_size(row, {}))

        row.to_dict = lambda: {"row_payload": {"_validated_size_override": "L"}}
        self.assertEqual(("L", "validated"), _resolve_categorize_size(row, {"apm001": "M"}))

    def test_technical_evaluation_import_topic_filter(self):
        self.assertTrue(_is_technical_evaluation_topic("Harmonize Maintenance Management Systems"))
        self.assertTrue(_is_technical_evaluation_topic("  harmonize maintenance management systems  "))
        self.assertFalse(_is_technical_evaluation_topic("Harmonize Alarm Management Solutions"))
        self.assertFalse(_is_technical_evaluation_topic("Harmonize ERP Solutions"))

    def test_maintenance_discovery_uses_cmms_and_asset_management_queries(self):
        queries = ollama_service._market_topic_queries("Harmonize Maintenance Management Systems")

        self.assertTrue(any("CMMS" in query for query in queries))
        self.assertTrue(any("EAM" in query for query in queries))
        self.assertTrue(any("work order" in query for query in queries))
        self.assertTrue(any("condition monitoring" in query for query in queries))
        self.assertTrue(all(len(query.split()) <= 7 for query in queries))
        self.assertFalse(any("EEMUA 191" in query for query in queries))

    def test_enrichment_rejects_non_approved_topic_before_database_access(self):
        with self.assertRaisesRegex(ValueError, "restricted to the approved topic"):
            enrich_technical_evaluation_categorize_topic(
                "Harmonize Alarm Management Solutions"
            )

    def test_alarm_discovery_uses_industrial_market_query(self):
        queries = ollama_service._market_topic_queries("Harmonize Alarm Management Solutions")

        self.assertTrue(any("EEMUA 191" in query for query in queries))
        self.assertFalse(any("home automation" in query.casefold() for query in queries))

    def test_uploaded_context_supplies_conservative_product_defaults(self):
        values = ollama_service._portfolio_evidence_defaults(
            {
                "context": {
                    "Application type": "Commercial of the shelf with major modifications",
                    "Rationale": "Supports plant alarm monitoring, filtering, and operational alerts.",
                }
            },
            ["Alarm Filtering", "Energy Management", "COTS / Available in Market / Custom Products"],
        )

        self.assertEqual("Yes", values["Alarm Filtering"])
        self.assertNotIn("Energy Management", values)
        self.assertEqual("Hybrid", values["COTS / Available in Market / Custom Products"])

    def test_uploaded_context_contributes_explicit_capabilities(self):
        capabilities = ollama_service._portfolio_grounded_capabilities(
            "Harmonize Alarm Management Solutions",
            [{"context": {"Rationale": "Supports alarm monitoring and alarm-event analysis."}}],
        )

        self.assertEqual(["Alarm Monitoring", "Alarm Event Analysis"], capabilities)

    def test_maintenance_context_contributes_maintenance_capabilities(self):
        capabilities = ollama_service._portfolio_grounded_capabilities(
            "Harmonize Maintenance Management Systems",
            [{"context": {"Rationale": (
                "Supports work order processing, preventive maintenance, asset hierarchy, "
                "spare parts, condition monitoring, and reliability analytics."
            )}}],
        )

        self.assertEqual(
            [
                "Work Order Management",
                "Preventive Maintenance",
                "Asset Registry and Hierarchy",
                "Spare Parts and Inventory Management",
                "Condition Monitoring",
                "Reliability and Failure Analysis",
            ],
            capabilities,
        )

    def test_topic_evidence_extracts_all_explicit_maintenance_capabilities(self):
        capabilities = ollama_service._evidence_grounded_capabilities(
            "Harmonize Maintenance Management Systems",
            [
                "CMMS products provide work orders, preventive maintenance, spare parts inventory, "
                "condition monitoring, and maintenance reporting KPIs."
            ],
        )

        self.assertEqual(
            [
                "Work Order Management",
                "Preventive Maintenance",
                "Spare Parts and Inventory Management",
                "Condition Monitoring",
                "Maintenance Reporting and KPIs",
            ],
            capabilities,
        )

    def test_maintenance_topic_has_stable_core_comparison_schema(self):
        capabilities = ollama_service._topic_core_capabilities(
            "Harmonize Maintenance Management Systems"
        )

        self.assertIn("Work Order Management", capabilities)
        self.assertIn("Asset Lifecycle Management", capabilities)
        self.assertIn("Inspection and Calibration Management", capabilities)
        self.assertIn("Integration and Interoperability", capabilities)
        self.assertEqual(len(capabilities), len(set(capabilities)))

    def test_product_evidence_must_identify_the_product(self):
        evidence = [
            "Generic CMMS software — preventive maintenance and work orders",
            "BASANT Ultimo — commercial maintenance product with work order management",
            "Unrelated Ultimo game result",
        ]

        verified = ollama_service._verified_product_evidence("BASANT Ultimo", evidence)

        self.assertEqual(1, len(verified))
        self.assertIn("BASANT Ultimo", verified[0])

    def test_product_search_uses_safe_internal_and_vendor_aliases(self):
        self.assertEqual(
            ["BASANT Ultimo", "Ultimo"],
            ollama_service._product_search_aliases("BASANT Ultimo"),
        )
        self.assertIn(
            "GE APM",
            ollama_service._product_search_aliases(
                "General Electric Asset Performance Management"
            ),
        )
        self.assertIn(
            "bMobile",
            ollama_service._product_search_aliases("Beamex bMobile"),
        )
        queries = ollama_service._market_product_queries(
            "Harmonize Maintenance Management Systems", "BASANT Ultimo"
        )
        self.assertEqual(2, len(queries))
        self.assertTrue(all('"' not in query for query in queries))

    def test_maintenance_capabilities_are_canonicalized_and_off_topic_columns_removed(self):
        capabilities = ollama_service._canonicalize_capabilities(
            "Harmonize Maintenance Management Systems",
            [
                "Preventive Maintenance Scheduling",
                "Preventive Maintenance",
                "Planning and Resource Scheduling",
                "Maintenance Planning and Scheduling",
                "Energy Management",
            ],
        )

        self.assertEqual(
            ["Preventive Maintenance", "Maintenance Planning and Scheduling"],
            capabilities,
        )

    def test_portfolio_type_uses_authoritative_application_type(self):
        header = "COTS / Available in Market / Custom Products"

        self.assertEqual(
            "Custom",
            ollama_service._portfolio_evidence_defaults(
                {"context": {"Application type": "Self Developed"}}, [header]
            )[header],
        )
        self.assertEqual(
            "Hybrid",
            ollama_service._portfolio_evidence_defaults(
                {"context": {"Application type": "Commercial off-the-shelf with minor modifications"}},
                [header],
            )[header],
        )

    def test_synthetic_generic_rationale_does_not_mark_capabilities_yes(self):
        values = ollama_service._portfolio_evidence_defaults(
            {
                "context": {
                    "Application type": "Self Developed",
                    "Rationale": (
                        "Synthetic best-fit: aligns with maintenance planning, inspections, "
                        "asset work management, and CMMS processes."
                    ),
                    "Business Capability": "Provide Maintenance Management",
                }
            },
            [
                "Work Order Management",
                "Predictive Maintenance",
                "Condition Monitoring",
                "COTS / Available in Market / Custom Products",
            ],
        )

        self.assertNotIn("Work Order Management", values)
        self.assertNotIn("Predictive Maintenance", values)
        self.assertNotIn("Condition Monitoring", values)
        self.assertEqual("Custom", values["COTS / Available in Market / Custom Products"])

    @patch("app.services.ollama_service._available_model", return_value="test-model")
    @patch("app.services.ollama_service._generate")
    def test_model_guesses_are_downgraded_without_matching_product_evidence(self, generate, _model):
        generate.return_value = json.dumps([
            {
                "id": "1",
                "values": {
                    "Work Order Management": "Yes",
                    "Predictive Maintenance": "No",
                    "COTS / Available in Market / Custom Products": "COTS",
                },
            }
        ])

        values = OllamaService.generate_market_product_enrichment(
            "Harmonize Maintenance Management Systems",
            [{"id": 1, "product": "Internal Tool", "context": {}, "market_evidence": []}],
            [
                "Work Order Management",
                "Predictive Maintenance",
                "COTS / Available in Market / Custom Products",
            ],
        )["1"]

        self.assertEqual("Unknown", values["Work Order Management"])
        self.assertEqual("Unknown", values["Predictive Maintenance"])
        self.assertEqual("Unknown", values["COTS / Available in Market / Custom Products"])

    @patch("app.services.ollama_service._available_model", return_value="test-model")
    @patch("app.services.ollama_service._generate")
    def test_explicit_product_evidence_overrides_model_omission(self, generate, _model):
        generate.return_value = json.dumps([
            {"id": "1", "values": {"Work Order Management": "Unknown"}}
        ])

        values = OllamaService.generate_market_product_enrichment(
            "Harmonize Maintenance Management Systems",
            [{
                "id": 1,
                "product": "Limble CMMS",
                "context": {},
                "market_evidence": [
                    "Limble CMMS maintenance software streamlines managing work orders."
                ],
            }],
            ["Work Order Management"],
        )["1"]

        self.assertEqual("Yes", values["Work Order Management"])

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

    @patch("app.services.ollama_service.requests.get")
    def test_global_search_combines_searxng_json_title_and_content(self, get):
        response = Mock()
        response.headers = {"content-type": "application/json"}
        response.json.return_value = {
            "results": [{
                "title": "BASANT Ultimo maintenance software",
                "content": "Commercial product for work orders and preventive maintenance.",
            }]
        }
        response.raise_for_status.return_value = None
        get.return_value = response

        with patch.object(ollama_service, "MARKET_SEARCH_URL", "http://localhost:8080/search"):
            evidence = ollama_service._global_market_search(
                "BASANT Ultimo maintenance software capabilities"
            )

        self.assertEqual(1, len(evidence))
        self.assertIn("BASANT Ultimo", evidence[0])
        self.assertIn("work orders", evidence[0])

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
        # General + industrial-standard topic searches, then one independently
        # verified product query per product for this non-maintenance topic.
        self.assertEqual(4, search.call_count)
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
