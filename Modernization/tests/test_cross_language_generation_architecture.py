import json
import unittest

from services.modernizer.build_artifacts import (
    _backend_manifest_files,
    _frontend_scaffold_files,
)
from services.modernizer.prompt_pipeline import (
    _default_file_list,
    _npm_dependency_declaration_diagnostics,
    _pf_generate_project_files_template,
    _pf_resolve_target,
    _requirement_coverage_diagnostics,
)
from services.modernizer.scaffolds.polyglot import generate_polyglot_project
from services.modernizer.target_config import TARGET_STACKS


class CrossLanguageGenerationArchitectureTests(unittest.TestCase):
    def test_selected_target_supplies_omitted_layer_facts(self):
        angular, angular_signals, full_stack, language, _ = _pf_resolve_target(
            "Build an inventory dashboard", "angular_ts", "",
        )
        self.assertEqual("typescript", language)
        self.assertEqual("Angular", angular_signals["frontend"])
        self.assertIsNone(angular_signals["backend"])
        self.assertFalse(full_stack)
        self.assertIn("Angular", angular["frontend_tech"])

        spring, spring_signals, _, language, _ = _pf_resolve_target(
            "Build inventory management", "spring_boot", "",
        )
        self.assertEqual("java", language)
        self.assertIn("Spring Boot", spring_signals["backend"])
        self.assertEqual("postgres", spring["db_target"])

        node, node_signals, full_stack, language, _ = _pf_resolve_target(
            "Build inventory management", "node_express_react", "",
        )
        self.assertEqual("typescript", language)
        self.assertEqual("Node.js + Express", node_signals["backend"])
        self.assertEqual("React", node_signals["frontend"])
        self.assertTrue(full_stack)
        self.assertEqual("mongodb", node["db_target"])

    def test_prompt_facts_override_target_and_unknowns_fail_closed(self):
        target, signals, _, _, _ = _pf_resolve_target(
            "Use React as the frontend", "angular_ts", "",
        )
        self.assertEqual("React", signals["frontend"])
        self.assertEqual("React", target["frontend_tech"])
        with self.assertRaisesRegex(ValueError, "Unknown target stack"):
            _pf_resolve_target("Build an app", "missing-stack", "")

        custom, _, _, _, _ = _pf_resolve_target(
            "Build a Rust Axum API with no persistence", "custom", "",
        )
        self.assertEqual("rust", custom["language"])
        self.assertEqual("", custom["db_target"])

    def test_node_and_python_manifests_follow_framework_and_database(self):
        express = _backend_manifest_files(
            "typescript", "Orders", "Node.js + Express", False, False, "mongodb",
        )
        package = json.loads(express["backend/package.json"])
        self.assertIn("express", package["dependencies"])
        self.assertIn("mongoose", package["dependencies"])
        self.assertNotIn("pg", package["dependencies"])
        self.assertIn("backend/tsconfig.json", express)

        graphql = json.loads(_backend_manifest_files(
            "typescript", "Orders", "Node.js + GraphQL", False, False, "postgres",
        )["backend/package.json"])
        self.assertIn("@apollo/server", graphql["dependencies"])
        self.assertIn("pg", graphql["dependencies"])
        self.assertNotIn("express", graphql["dependencies"])

        django = _backend_manifest_files(
            "python", "Orders", "Django 5 + Django REST Framework", False, False, "postgres",
        )["requirements.txt"]
        self.assertIn("Django", django)
        self.assertIn("psycopg", django)
        self.assertNotIn("fastapi", django)

        mongo_fastapi = _backend_manifest_files(
            "python", "Orders", "Python FastAPI", False, False, "mongodb",
        )["requirements.txt"]
        self.assertIn("motor", mongo_fastapi)
        self.assertNotIn("asyncpg", mongo_fastapi)

    def test_react_vue_and_angular_scaffolds_are_bootstrap_closed(self):
        cases = {
            "React 18 + TypeScript + Vite": ("frontend/src/main.tsx", "frontend/src/App.tsx"),
            "Vue 3 + TypeScript + Vite": ("frontend/src/main.ts", "frontend/src/App.vue"),
            "Angular 17 + TypeScript": ("frontend/src/main.ts", "frontend/angular.json"),
        }
        for framework, required in cases.items():
            with self.subTest(framework=framework):
                files = _frontend_scaffold_files(framework, "Demo", False)
                self.assertIn("frontend/package.json", files)
                self.assertIn("frontend/tsconfig.json", files)
                for path in required:
                    self.assertIn(path, files)
                rooted = {f"Demo/{path}": content for path, content in files.items()}
                self.assertEqual([], _npm_dependency_declaration_diagnostics(rooted))

    def test_node_and_django_polyglot_contracts_are_framework_native(self):
        for target_id, tokens in {
            "node_express_react": ("express", "mongoose", "main.tsx"),
            "node_graphql_react": ("@apollo/server", "graphql", "main.tsx"),
            "javascript_node": ("express", "server.js"),
            "python_django": ("Django==", "manage.py", "test_health.py"),
        }.items():
            target = TARGET_STACKS[target_id]
            files = generate_polyglot_project(target["language"], "Demo", "Orders", target)
            searchable = "\n".join(files) + "\n" + "\n".join(files.values())
            for token in tokens:
                self.assertIn(token, searchable)

    def test_offline_polyglot_fallback_uses_buildable_native_contract(self):
        target = TARGET_STACKS["rust_axum_react"]
        output = {}
        file_list = _pf_generate_project_files_template(
            target, "Demo", "Build an Axum service", True, True, True, "rust",
            output, (), output.__setitem__, lambda *_: None,
        )
        self.assertTrue(any(path.endswith("Cargo.toml") for path in file_list))
        self.assertTrue(any(path.endswith("src/main.rs") for path in output))
        self.assertFalse(any(path.endswith(".cs") for path in output))

    def test_architecture_and_dependency_coverage_fail_closed(self):
        incomplete = {
            "Demo/frontend/package.json": '{"dependencies":{"react":"^18"}}',
            "Demo/frontend/src/App.tsx": "import axios from 'axios'; export default ()=>null;",
        }
        diagnostics = _requirement_coverage_diagnostics(
            incomplete, "Build a React application with automated tests", "typescript",
        )
        self.assertTrue(any("Undeclared npm dependency 'axios'" in item for item in diagnostics))
        self.assertTrue(any("React requires" in item for item in diagnostics))
        self.assertTrue(any("automated tests" in item for item in diagnostics))

    def test_unsupported_default_never_falls_back_to_csharp(self):
        self.assertEqual([], _default_file_list({"language": "rust"}, "Demo"))


if __name__ == "__main__":
    unittest.main()
