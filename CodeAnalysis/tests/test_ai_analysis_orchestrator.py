import concurrent.futures
import sys
import types

# The collector is infrastructure-only and does not instantiate an Ollama
# client. Keep this unit test runnable with the repository's lightweight test
# interpreter, where the optional runtime Ollama SDK is not installed.
sys.modules.setdefault("ollama", types.SimpleNamespace(Client=object))

from services.ai_analysis import (
    _ANALYSES,
    _build_fast_analyses,
    _collect_dispatched_results,
    _enrich_prediction_sections,
    _generate_prediction_narratives,
)


def test_collect_dispatched_results_preserves_success_and_failure_outputs():
    successful = concurrent.futures.Future()
    successful.set_result({"summary": "Generated output"})
    failed = concurrent.futures.Future()
    failed.set_exception(RuntimeError("model section failed"))
    report = {"analyses": {}}
    progress = []

    _collect_dispatched_results(
        {successful: "tech_debt", failed: "cloud_blockers"},
        {"tech_debt": "Tech Debt", "cloud_blockers": "Cloud Blockers"},
        progress.append,
        report,
    )

    assert report["analyses"]["tech_debt"]["summary"] == "Generated output"
    assert report["analyses"]["cloud_blockers"]["error"] == "model section failed"
    assert set(progress) == {"Tech Debt", "Cloud Blockers"}


def _scanner_result():
    return {
        "repo_name": "sample-app",
        "total_sloc": 1200,
        "languages_detected": ["Java"],
        "health": {"health": 62, "risk_label": "FAIR", "summary": ["Long methods: 4"]},
        "debt": {"debt_months": 2, "risk_label": "MEDIUM"},
        "cloud": {"total": 25, "blockers": ["No containerization artifacts"]},
        "architecture": {
            "layer_counts": {"Coordination": 2},
            "nodes": [{"name": "src/OrderService.java"}, {"name": "src/OrderAction.java"}],
        },
        "language_reports": [{"bad_practices": ["Long methods: 4"]}],
        "ml_predictions": {
            "defect_predictions": [{
                "file": "C:/upload/extracted/sample-app/src/OrderService.java",
                "risk_level": "high",
                "probability": 0.82,
                "factors": ["High complexity"],
            }],
            "migration_score": {"legacy_signals": {"struts": True}},
            "tech_fingerprint": {"struts": 0.9},
            "summary": "Legacy migration is recommended.",
        },
    }


def test_prediction_narratives_use_one_bounded_ollama_call():
    class Client:
        calls = 0

        def generate_json(self, *args, **kwargs):
            self.calls += 1
            assert kwargs["max_tokens"] == 420
            assert kwargs["timeout"] == 180
            assert kwargs["max_attempts"] == 1
            return {"tech_debt": {"summary": "Prioritize complexity.", "top_actions": ["Refactor"]}}

    client = Client()
    result = _generate_prediction_narratives(_scanner_result(), {"tech_debt"}, "qwen3.5:9b", client)

    assert client.calls == 1
    assert result["tech_debt"]["summary"] == "Prioritize complexity."


def test_fast_analyses_populate_every_prediction_section():
    keys = {key for key, *_ in _ANALYSES}
    analyses = _build_fast_analyses(_scanner_result(), {}, keys, "qwen3.5:9b")

    assert set(analyses) == keys
    assert analyses["tech_debt"]["hotspots"][0]["file"].endswith("src/OrderService.java")
    assert analyses["cloud_blockers"]["blockers"]
    assert analyses["microservices"]["microservices"]
    assert analyses["business_rules"]["business_rules"]
    assert analyses["transformation"]["transformation_paths"]
    assert analyses["code_level"]["per_function_issues"]


def test_deterministic_enrichment_adds_deep_prediction_fields():
    keys = {key for key, *_ in _ANALYSES}
    analyses = _build_fast_analyses(_scanner_result(), {}, keys, "qwen2.5-coder:3b")
    enriched = _enrich_prediction_sections(
        analyses, _scanner_result(), repo_path="", model="qwen2.5-coder:3b",
    )

    transformation = enriched["transformation"]
    assert transformation["modernisation_phases"][0]["title"]
    assert transformation["modernisation_phases"][0]["success_criteria"]
    assert transformation["transformation_paths"][0]["rationale"]
    assert transformation["transformation_paths"][0]["affected_file_patterns"]
    assert transformation["transformation_paths"][0]["business_benefits"]
    assert enriched["cloud_blockers"]["twelve_factor_compliance"]
    assert enriched["legacy_modernization"]["technology_replacements"]
