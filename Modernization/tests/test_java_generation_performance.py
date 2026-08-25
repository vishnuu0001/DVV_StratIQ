import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from services.modernizer.conversion_pipeline import (
    _dom_cache_key,
    _mp_java_domain_analysis,
    _mp_java_verified_database_tables,
)
from services.validators import ValidationResult


class JavaGenerationEvidenceTests(unittest.TestCase):
    def test_java_database_evidence_ignores_javascript_and_comment_prose(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "jquery.min.js").write_text(
                "update this option; select all from the wrapper", encoding="utf-8"
            )
            (root / "Legacy.java").write_text(
                '// update PATH set this is only a comment\n'
                '@Entity class CustomerAccount {}\n'
                'String sql = "select id from CUSTOMER_ORDER where id = ?";\n',
                encoding="utf-8",
            )

            tables = _mp_java_verified_database_tables(temp_dir)

        self.assertEqual(tables, ["CUSTOMER_ACCOUNT", "CUSTOMER_ORDER"])

    def test_java_prompt_analysis_excludes_non_java_antipatterns(self):
        original = {
            "database": {"table_names": ["WRAPPER", "CUSTOMER"]},
            "antipatterns": [
                {"file": "vendor/jquery.min.js", "type": "large_file"},
                {"file": "src/Customer.java", "type": "god_class"},
            ],
        }

        filtered = _mp_java_domain_analysis(original, ["CUSTOMER"])

        self.assertEqual(filtered["database"]["table_names"], ["CUSTOMER"])
        self.assertEqual(filtered["antipatterns"], [original["antipatterns"][1]])
        self.assertEqual(original["database"]["table_names"], ["WRAPPER", "CUSTOMER"])

    def test_java_domain_cache_changes_when_source_changes_at_same_loc(self):
        target = {"id": "spring", "language": "java"}
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "Sample.java"
            analysis = {
                "folder_path": temp_dir,
                "metrics": {"total_loc": 1},
                "antipatterns": [],
            }
            source.write_text("class First {}", encoding="utf-8")
            first = _dom_cache_key("Core", target, "sample", [], analysis)
            source.write_text("class Other {}", encoding="utf-8")
            second = _dom_cache_key("Core", target, "sample", [], analysis)

        self.assertNotEqual(first, second)


class JavaDuplicateInferenceTests(unittest.TestCase):
    def test_java_domain_does_not_regenerate_already_validated_sources(self):
        from services.modernizer.domain_generators import dispatch

        def backend(_lang, files, *_args, **_kwargs):
            path = "ModernizedApp/services/core-service/src/main/java/Core.java"
            files[path] = "class Core {}"
            return {path}

        def frontend(_lang, _target, files, *_args, **_kwargs):
            path = "ModernizedApp/src/components/Core/CorePage.tsx"
            files[path] = "export const CorePage = () => null;"
            return {path}

        target = {
            "id": "spring",
            "name": "Spring Boot + React",
            "language": "java",
            "backend_tech": "Spring Boot 3",
            "frontend_tech": "React",
        }
        analysis = {
            "folder_path": "",
            "architecture": {},
            "metrics": {},
            "antipatterns": [],
        }
        with patch(
            "services.modernizer.conversion_pipeline._load_dom_cache", return_value=None
        ), patch(
            "services.modernizer.conversion_pipeline._save_dom_cache"
        ), patch.object(
            dispatch, "_dispatch_backend_generation", side_effect=backend
        ), patch.object(
            dispatch, "_maybe_generate_frontend", side_effect=frontend
        ), patch.object(
            dispatch, "_ollama_generate_all_sources"
        ) as blanket_generation:
            files = dispatch._llm_gen_domain(
                "Core", target, analysis, "sample", [], model="test-model"
            )

        blanket_generation.assert_not_called()
        provenance = json.loads(
            files["ModernizedApp/.strat-aqorynth/ollama-core-provenance.json"]
        )
        self.assertEqual(len(provenance["source_files"]), 2)
        self.assertEqual(provenance["generator"], "ollama")

    def test_invalid_java_domain_artifact_fails_instead_of_emitting_placeholder(self):
        from services.modernizer.domain_generators.java import _llm_domain_java

        failed = ValidationResult(
            "Controller.java", "java", "compiler", False, ["missing class terminator"]
        )
        with patch(
            "services.modernizer.validation_orchestration._generate_validated",
            return_value=("class Broken {", failed, 2),
        ):
            with self.assertRaisesRegex(RuntimeError, "controller generation failed"):
                _llm_domain_java(
                    files={}, domain="Core", root_ns="sample", domain_tables=[],
                    antipatterns=[], context="", prod_rules="", source_sec="",
                    guide_sec="", model="test-model", system="system", tables=[],
                    target={"backend_tech": "Spring Boot", "db_target": "postgres"},
                    on_step=None, generate=lambda *_args, **_kwargs: "",
                )

    def test_failed_java_conversion_is_not_cached(self):
        from services.modernizer import conversion_pipeline

        failed = ValidationResult(
            "Sample.java", "java", "compiler", False, ["syntax error"]
        )
        target = {
            "id": "spring",
            "name": "Spring Boot",
            "language": "java",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "Sample.java"
            source.write_text("class Sample {}", encoding="utf-8")
            with patch.object(
                conversion_pipeline, "_read_conversion_cache", return_value=None
            ), patch.object(
                conversion_pipeline, "_write_conversion_cache"
            ) as cache_write, patch(
                "services.modernizer.validation_orchestration._generate_validated",
                return_value=("class Broken {", failed, 2),
            ):
                conversion_pipeline._convert_file_with_llm(
                    source, source.read_text(encoding="utf-8"), "java", target,
                    analysis={}, root_ns="sample", model="test-model", system="system",
                    out_path="ModernizedApp/src/main/java/sample/Sample.java",
                )

        cache_write.assert_not_called()


if __name__ == "__main__":
    unittest.main()
