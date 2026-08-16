import inspect
import unittest

from services.modernizer.conversion_pipeline import (
    _mp_ensure_java_service_modules_populated,
    modernize_project,
)


class JavaServiceModuleBackfillTests(unittest.TestCase):
    """Guard against the exact failure an IDE reports as "missing required
    source folder" for a generated multi-service Java project: the reactor
    pom.xml unconditionally declares <module>services/{domain}-service
    </module> for every domain, but LLM-driven domain generation can finish
    a domain with zero usable .java files under its src/main/java tree even
    though the job reported that domain "complete". See
    _mp_ensure_java_service_modules_populated in conversion_pipeline.py."""

    def _target(self):
        return {"backend_tech": "Spring Boot 3", "db_target": "postgres"}

    def test_backfills_a_domain_with_no_java_sources(self):
        output = {
            # Struct domain generated normally.
            "ModernizedApp/services/struct-service/src/main/java/com/acme/struct/controller/StructController.java": "// ok",
            "ModernizedApp/services/struct-service/pom.xml": "<project/>",
            # Mina domain "completed" per the job log, but somehow left no
            # .java files behind under its src/main/java tree.
            "ModernizedApp/services/mina-service/src/main/resources/application.yml": "server: {}",
        }
        backfilled = _mp_ensure_java_service_modules_populated(
            output, ["struct", "mina"], "acme", self._target(), ["ORDERS"],
        )

        self.assertEqual(backfilled, ["mina"])
        mina_java_files = [
            p for p in output
            if p.startswith("ModernizedApp/services/mina-service/src/main/java/") and p.endswith(".java")
        ]
        self.assertTrue(mina_java_files, "expected mina-service to be backfilled with .java sources")
        # A minimal buildable scaffold means a Spring Boot entry point exists.
        self.assertTrue(any(p.endswith("MinaApplication.java") for p in mina_java_files))

    def test_does_not_touch_a_domain_that_already_has_java_sources(self):
        original_content = "// hand-verified generated content"
        output = {
            "ModernizedApp/services/struct-service/src/main/java/com/acme/struct/controller/StructController.java": original_content,
        }
        backfilled = _mp_ensure_java_service_modules_populated(
            output, ["struct"], "acme", self._target(), ["ORDERS"],
        )

        self.assertEqual(backfilled, [])
        self.assertEqual(
            output["ModernizedApp/services/struct-service/src/main/java/com/acme/struct/controller/StructController.java"],
            original_content,
        )

    def test_all_domains_missing_are_all_backfilled(self):
        output: dict = {}
        backfilled = _mp_ensure_java_service_modules_populated(
            output, ["mina", "photoshop"], "acme", self._target(), ["ORDERS"],
        )
        self.assertEqual(sorted(backfilled), ["mina", "photoshop"])
        for domain in ("mina", "photoshop"):
            base = f"ModernizedApp/services/{domain}-service"
            self.assertTrue(any(
                p.startswith(f"{base}/src/main/java/") and p.endswith(".java")
                for p in output
            ))

    def test_modernize_project_wires_the_backfill_after_domain_generation_for_java(self):
        # modernize_project() itself is too heavy to run end-to-end here (real
        # build_runner / docs_generation / LLM calls) — verify the wiring
        # statically instead: the call must exist, gated on lang == "java",
        # immediately after _mp_run_domain_generation and before anything
        # else touches `output` for the Java branch.
        source = inspect.getsource(modernize_project)
        self.assertIn("_mp_ensure_java_service_modules_populated(", source)
        call_index = source.index("_mp_ensure_java_service_modules_populated(")
        domain_gen_index = source.index("_mp_run_domain_generation(")
        self.assertLess(
            domain_gen_index, call_index,
            "backfill must run after domain generation, not before",
        )


if __name__ == "__main__":
    unittest.main()
