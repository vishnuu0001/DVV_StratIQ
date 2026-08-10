import json
from types import SimpleNamespace

from traceforge.routers.testcases import _test_case_content_hash


def test_review_metadata_changes_test_case_content_hash():
    test_case = SimpleNamespace(
        title="Approved outcome",
        test_type="POSITIVE",
        test_level="UI_E2E",
        preconditions=[],
        steps=[{"step_no": 1, "action": "Submit", "expected_result": "Accepted"}],
        priority="P1",
        gherkin=json.dumps({"automation_status": "AUTOMATION_BLOCKED"}),
        upstream_req_hash="a" * 64,
    )
    original_hash = _test_case_content_hash(test_case)

    test_case.gherkin = json.dumps({
        "automation_status": "AUTOMATION_BLOCKED",
        "review_decisions": [{"resolved_by": "test-lead", "resolution": "Role confirmed"}],
    })

    assert _test_case_content_hash(test_case) != original_hash