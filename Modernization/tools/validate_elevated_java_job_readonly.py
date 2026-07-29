"""Read-only revalidation of an elevated persisted Java generation job."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from services.build_runner import run_build
from services.modernizer.build_artifacts import _reconcile_java_generation_output


def main(job_id: str) -> None:
    source = Path(r"C:\Windows\Temp\modernization_jobs") / f"{job_id}.json"
    job = json.loads(source.read_text(encoding="utf-8"))
    original = dict(job.get("output") or {})
    candidate = dict(original)
    project_paths = list(candidate)
    project_name = project_paths[0].split("/", 1)[0] if project_paths else "GeneratedProject"
    _reconcile_java_generation_output(candidate, project_name)
    with tempfile.TemporaryDirectory(prefix="java_service_revalidation_") as directory:
        result = run_build(candidate, "java", Path(directory))
    report = {
        "job_id": job_id,
        "passed": result.passed,
        "checker": result.checker,
        "remaining_errors": result.errors_by_file,
        "original_file_count": len(original),
        "candidate_file_count": len(candidate),
        "removed_paths": sorted(set(original) - set(candidate)),
        "added_paths": sorted(set(candidate) - set(original)),
    }
    report_path = ROOT / "data" / "logs" / "read-only-java-revalidation.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1])
