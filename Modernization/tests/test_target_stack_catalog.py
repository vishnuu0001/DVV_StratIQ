# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — tests (test_target_stack_catalog.py)
# Date: 2026-01-11
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Scope: Complete selectable Modernization target-stack catalog
# ---------------------------------------------------------------------------
import asyncio
import unittest

from api.server import target_stacks
from services.validators import _resolve_sql_dialect


class TargetStackCatalogTests(unittest.TestCase):
    # Function: test_every_supported_language_and_artifact_is_selectable
    def test_every_supported_language_and_artifact_is_selectable(self):
        catalog = asyncio.run(target_stacks())
        stacks = catalog["stacks"]
        searchable = [
            f"{stack['name']} {stack['language']}".casefold()
            for stack in stacks
        ]
        for capability in (
            *catalog["supported_languages"],
            *catalog["supported_artifacts"],
        ):
            with self.subTest(capability=capability):
                value = capability.casefold()
                self.assertTrue(
                    any(value in entry or entry.split()[-1] in value for entry in searchable),
                    f"{capability} is advertised but has no selectable target stack",
                )

    # Function: test_stack_ids_are_unique
    def test_stack_ids_are_unique(self):
        stacks = asyncio.run(target_stacks())["stacks"]
        identifiers = [stack["id"] for stack in stacks]
        self.assertEqual(len(identifiers), len(set(identifiers)))

    # Function: test_guided_stacks_use_custom_engine
    def test_guided_stacks_use_custom_engine(self):
        stacks = asyncio.run(target_stacks())["stacks"]
        self.assertTrue(all(
            stack["native"] or stack["engine_target"] == "custom"
            for stack in stacks
        ))

    # Function: test_vendor_targets_are_visible_but_not_falsely_ready
    def test_vendor_targets_are_visible_but_not_falsely_ready(self):
        catalog = asyncio.run(target_stacks())
        by_id = {stack["id"]: stack for stack in catalog["stacks"]}
        for identifier in ("abap_application", "salesforce_apex", "jenkins_pipeline"):
            with self.subTest(identifier=identifier):
                self.assertFalse(by_id[identifier]["available"])
                self.assertTrue(by_id[identifier]["blocked_reason"])
                self.assertIn(
                    by_id[identifier]["language"],
                    (
                        catalog["externally_gated_artifacts"]
                        if identifier == "jenkins_pipeline"
                        else catalog["externally_gated_languages"]
                    ),
                )

    # Function: test_legacy_source_journeys_are_gated_by_modern_target_toolchains
    def test_legacy_source_journeys_are_gated_by_modern_target_toolchains(self):
        by_id = {
            stack["id"]: stack for stack in asyncio.run(target_stacks())["stacks"]
        }
        expected_targets = {
            "fortran_native": "Java", "ada_native": "Java",
            "pascal_delphi": "C#", "ocaml_application": "Java",
            "prolog_application": "Java", "pli_batch": "Java",
            "rpg_application": "Java", "jcl_batch": "Java",
            "mumps_application": "C#", "natural_application": "Java",
            "progress_openedge": "C#",
        }
        for identifier, target_language in expected_targets.items():
            with self.subTest(identifier=identifier):
                stack = by_id[identifier]
                self.assertEqual(target_language, stack["language"])
                self.assertTrue(stack["available"])
                self.assertTrue(stack["project_ready"])
                self.assertTrue(stack["full_generation"])
                self.assertIsNone(stack["blocked_reason"])

    # Function: test_selectable_sql_stacks_resolve_expected_dialect
    def test_selectable_sql_stacks_resolve_expected_dialect(self):
        stacks = asyncio.run(target_stacks())["stacks"]
        expected = {
            "oracle_to_postgres": "postgres", "oracle_to_mssql": "tsql",
            "mssql_to_postgres": "postgres", "oracle_sql": "oracle",
            "db2_sql": "db2", "mysql_sql": "mysql",
            "sql_generic": "", "postgresql_sql": "postgres",
            "plsql_oracle": "oracle", "tsql_sqlserver": "tsql",
        }
        by_id = {stack["id"]: stack for stack in stacks}
        for identifier, dialect in expected.items():
            with self.subTest(identifier=identifier):
                stack = by_id[identifier]
                hint = f"{stack['database']} {stack['backend']}"
                self.assertEqual(dialect, _resolve_sql_dialect(hint))

    # Function: test_requested_stacks_are_engine_native_full_generation_targets
    def test_requested_stacks_are_engine_native_full_generation_targets(self):
        catalog = asyncio.run(target_stacks())
        by_id = {stack["id"]: stack for stack in catalog["stacks"]}
        requested = {
            "dotnet_react", "dotnet_angular", "dotnet_microservices",
            "node_nest_react", "nextjs_fullstack", "kotlin_spring",
            "go_fiber_vue", "rust_axum_react", "php_laravel_vue",
            "flutter_dotnet", "javascript_node", "swift_vapor",
            "kotlin_ktor", "shell_automation", "r_analytics", "scala_play",
            "clojure_ring", "haskell_servant", "common_lisp",
            "julia_application", "ibmi_as400", "react_native_node",
            "cobol_java", "cobol_dotnet", "elixir_phoenix",
            "erlang_otp", "dart_server",
        }
        self.assertTrue(requested <= set(by_id))
        for identifier in requested:
            with self.subTest(identifier=identifier):
                self.assertTrue(by_id[identifier]["native"])
                # Availability remains an environment/toolchain concern; the
                # engine's generation capability must not depend on installation.
                if by_id[identifier]["available"]:
                    self.assertTrue(by_id[identifier]["full_generation"])

    # Function: test_as400_is_identified_as_source_to_java_journey
    def test_as400_is_identified_as_source_to_java_journey(self):
        stack = next(
            item for item in asyncio.run(target_stacks())["stacks"]
            if item["id"] == "ibmi_as400"
        )
        self.assertIn("AS/400", stack["name"])
        self.assertEqual("Java", stack["language"])
        self.assertIn("Spring Boot", stack["backend"])
        self.assertTrue(stack["full_generation"])


if __name__ == "__main__":
    unittest.main()
