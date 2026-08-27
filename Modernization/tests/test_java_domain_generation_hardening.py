import unittest
from unittest.mock import patch

from services.modernizer.validation_orchestration import (
    _clean_generated_content, _generate_validated, _normalize_jakarta_namespace,
)
from services.validators import ValidationResult


class CleanGeneratedContentTests(unittest.TestCase):
    """Reproduces the real observed failure: CustomerController.java failed
    compilation on all 3 attempts with "illegal character: '`'" on line 1 —
    the old fullmatch-only fence check left the whole response, backticks
    included, completely unstripped whenever the model added any text
    outside a single perfectly-formed fenced block, which a repair round
    fed compiler diagnostics can never fix (the diagnostics describe a
    syntax error, not "you still included markdown fences")."""

    def test_strips_a_perfectly_formed_single_fence_unchanged(self):
        content = _clean_generated_content("```java\nclass Foo {}\n```")
        self.assertEqual(content, "class Foo {}\n")

    def test_strips_a_fence_with_leading_prose(self):
        content = _clean_generated_content(
            "Here is the complete file:\n\n```java\nclass Foo {}\n```"
        )
        self.assertEqual(content, "class Foo {}\n")

    def test_strips_a_fence_with_trailing_prose(self):
        content = _clean_generated_content(
            "```java\nclass Foo {}\n```\n\nThis Controller handles CRUD operations."
        )
        self.assertEqual(content, "class Foo {}\n")

    def test_strips_a_fence_with_prose_on_both_sides(self):
        content = _clean_generated_content(
            "Sure, here you go:\n```java\nclass Foo {}\n```\nLet me know if you need changes."
        )
        self.assertEqual(content, "class Foo {}\n")

    def test_keeps_content_from_a_fence_with_no_closing_marker(self):
        # A closing fence cut off by max_tokens truncation, or never emitted.
        content = _clean_generated_content("```java\nclass Foo {\n    void bar() {}")
        self.assertEqual(content, "class Foo {\n    void bar() {}\n")

    def test_leaves_unfenced_content_unchanged(self):
        content = _clean_generated_content("class Foo {}")
        self.assertEqual(content, "class Foo {}\n")

    def test_empty_input_returns_empty(self):
        self.assertEqual(_clean_generated_content(""), "")
        self.assertEqual(_clean_generated_content(None), "")


class NormalizeJakartaNamespaceTests(unittest.TestCase):
    """Reproduces the real observed failure: a Spring Boot 3 Controller
    failed all 3 repair attempts on nothing but `import javax.validation.Valid`
    — every other reported compiler error was fixed along the way, but the
    model kept reverting this one, well-known, unambiguous rename. Jakarta EE
    9 renamed these packages 1:1 with no semantic change, so it is applied
    deterministically rather than left to model compliance."""

    def test_rewrites_known_migrated_packages(self):
        content = (
            "import javax.validation.Valid;\n"
            "import javax.persistence.Entity;\n"
            "import javax.servlet.http.HttpServletRequest;\n"
            "import javax.ws.rs.GET;\n"
            "import javax.annotation.PostConstruct;\n"
            "import javax.transaction.Transactional;\n"
            "import static javax.validation.Validation.buildDefaultValidatorFactory;\n"
        )
        normalized = _normalize_jakarta_namespace(content)
        self.assertIn("import jakarta.validation.Valid;", normalized)
        self.assertIn("import jakarta.persistence.Entity;", normalized)
        self.assertIn("import jakarta.servlet.http.HttpServletRequest;", normalized)
        self.assertIn("import jakarta.ws.rs.GET;", normalized)
        self.assertIn("import jakarta.annotation.PostConstruct;", normalized)
        self.assertIn("import jakarta.transaction.Transactional;", normalized)
        self.assertIn("import static jakarta.validation.Validation.buildDefaultValidatorFactory;", normalized)
        self.assertNotIn("javax.", normalized)

    def test_does_not_touch_core_jdk_javax_packages(self):
        """javax.sql, javax.crypto, javax.xml.parsers, javax.swing, etc. are
        core JDK APIs that never moved to Jakarta EE — a blanket javax. ->
        jakarta. swap would silently break these."""
        content = (
            "import javax.sql.DataSource;\n"
            "import javax.crypto.Cipher;\n"
            "import javax.xml.parsers.DocumentBuilder;\n"
            "import javax.management.MBeanServer;\n"
        )
        self.assertEqual(_normalize_jakarta_namespace(content), content)


class JavaDomainGenerationConvergenceTests(unittest.TestCase):
    """The domain-service generator (services/modernizer/domain_generators/java.py
    -> _generate_validated) drives Java microservice files like Controller,
    Entity+DTO, and Service through up to 3 generate-validate-repair attempts
    per file. Before this fix, a repair attempt that reproduced the exact same
    validator diagnostics as the attempt before it (i.e. made zero measurable
    progress) still burned the full max_attempts budget every time — the
    pattern observed stalling Photoshop/Notification domain generation, where
    every single component went through attempt 2/3 and attempt 3/3 regardless
    of whether anything was actually being fixed."""

    def _failing_result(self, diagnostics):
        return ValidationResult("generated.java", "java", "compiler", False, list(diagnostics))

    def test_java_stops_early_when_repair_makes_no_progress(self):
        # Every generate() call returns different content, but validate_file
        # always reports the exact same diagnostics — the model is not
        # actually fixing anything.
        gen_calls = {"n": 0}

        def fake_generate(*args, **kwargs):
            gen_calls["n"] += 1
            return f"// attempt {gen_calls['n']}\nclass Foo {{}}"

        with patch("services.llm.generate", side_effect=fake_generate), \
             patch(
                 "services.validators.validate_file",
                 return_value=self._failing_result(["missing @RestController"]),
             ):
            content, result, attempts = _generate_validated(
                "generate a controller", model="qwen3.5:9b", system="sys",
                max_tokens=512, num_ctx=2048, rel_path="Foo.java", language="java",
                max_attempts=3,
            )

        # Attempt 1 (initial) + attempt 2 (repair, diagnostics unchanged) ->
        # stop. Attempt 3 must never fire because it would just repeat the
        # exact same no-progress cycle.
        self.assertEqual(gen_calls["n"], 2)
        self.assertEqual(attempts, 2)
        self.assertFalse(result.passed)

    def test_java_keeps_retrying_when_diagnostics_actually_change(self):
        # Diagnostics change on every attempt (genuine progress signal, or at
        # least new information) -> the loop must still run the full
        # max_attempts budget rather than stopping early.
        gen_calls = {"n": 0}
        results = [
            self._failing_result(["error A"]),
            self._failing_result(["error B"]),
            self._failing_result(["error C"]),
        ]

        def fake_generate(*args, **kwargs):
            gen_calls["n"] += 1
            return f"// attempt {gen_calls['n']}\nclass Foo {{}}"

        def fake_validate(*args, **kwargs):
            return results[min(gen_calls["n"] - 1, len(results) - 1)]

        with patch("services.llm.generate", side_effect=fake_generate), \
             patch("services.validators.validate_file", side_effect=fake_validate):
            _content, result, attempts = _generate_validated(
                "generate a controller", model="qwen3.5:9b", system="sys",
                max_tokens=512, num_ctx=2048, rel_path="Foo.java", language="java",
                max_attempts=3,
            )

        self.assertEqual(gen_calls["n"], 3)
        self.assertEqual(attempts, 3)
        self.assertFalse(result.passed)

    def test_non_java_languages_are_unaffected_by_the_convergence_check(self):
        # Same no-progress diagnostics pattern as the first test, but for a
        # non-Java language: must NOT early-exit, preserving prior behavior
        # for csharp/python/typescript/go generation exactly as before.
        gen_calls = {"n": 0}

        def fake_generate(*args, **kwargs):
            gen_calls["n"] += 1
            return f"// attempt {gen_calls['n']}\nclass Foo {{}}"

        with patch("services.llm.generate", side_effect=fake_generate), \
             patch(
                 "services.validators.validate_file",
                 return_value=self._failing_result(["missing namespace"]),
             ):
            _content, result, attempts = _generate_validated(
                "generate a controller", model="qwen3.5:9b", system="sys",
                max_tokens=512, num_ctx=2048, rel_path="Foo.cs", language="csharp",
                max_attempts=3,
            )

        self.assertEqual(gen_calls["n"], 3)
        self.assertEqual(attempts, 3)
        self.assertFalse(result.passed)


class JavaDomainGeneratorTimeBudgetTests(unittest.TestCase):
    """domain_generators/java.py's _llm_domain_java previously called
    _generate_validated with no generation_max_seconds bound at all for its
    per-domain LLM calls (Controller and Entity+DTO) — unlike the
    whole-project repair path, which already bounds every generate() call.
    A single slow/stuck Ollama call in this path could therefore run
    unbounded (up to _TRANSIENT_RETRY_ATTEMPTS x the 360s HTTP timeout) with
    no forward-progress guarantee.

    The budget here must be _JAVA_FILE_GENERATION_MAX_SECONDS, not
    _REPAIR_CALL_MAX_SECONDS: for language="java", _generate_validated treats
    generation_max_seconds as one AGGREGATE budget covering the initial draft
    plus every repair attempt (see its java_deadline logic) — exactly what
    _JAVA_FILE_GENERATION_MAX_SECONDS is sized and documented for.
    _REPAIR_CALL_MAX_SECONDS is a *per-call* budget for other languages'
    single-file repair/closure calls, deliberately smaller than a full
    first-draft generation; wiring it in here left no margin for a real
    Controller/Entity draft (observed: 300-600s alone on real hardware),
    so the very first attempt — before any repair round started — already
    exceeded the whole aggregate budget on every domain, every time."""

    def test_all_java_domain_calls_pass_the_java_aggregate_time_budget(self):
        from services.modernizer._shared import _JAVA_FILE_GENERATION_MAX_SECONDS
        from services.modernizer.domain_generators.java import _llm_domain_java

        captured_kwargs = []

        def fake_generate_validated(prompt, **kwargs):
            captured_kwargs.append(kwargs)
            return "// generated\nclass Foo {}", ValidationResult(
                kwargs.get("rel_path", "Foo.java"), "java", "compiler", True, [],
            ), 1

        files = {}
        with patch(
            "services.modernizer.validation_orchestration._generate_validated",
            side_effect=fake_generate_validated,
        ):
            _llm_domain_java(
                files=files, domain="Order", root_ns="acme", domain_tables=["ORDERS"],
                antipatterns=[], context="ctx", prod_rules="", source_sec="", guide_sec="",
                model="qwen3.5:9b", system="sys", tables=["ORDERS"],
                target={"backend_tech": "Spring Boot 3", "db_target": "postgres"},
                on_step=None, generate=lambda *a, **k: "",
            )

        self.assertEqual(len(captured_kwargs), 2)  # Controller and Entity+DTO
        for kwargs in captured_kwargs:
            self.assertEqual(kwargs.get("generation_max_seconds"), _JAVA_FILE_GENERATION_MAX_SECONDS)


if __name__ == "__main__":
    unittest.main()
