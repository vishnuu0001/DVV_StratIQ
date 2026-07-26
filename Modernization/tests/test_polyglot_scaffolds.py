# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — tests (test_polyglot_scaffolds.py)
# Date: 2025-09-06
# ---------------------------------------------------------------------------
import unittest

from services.modernizer.scaffolds.polyglot import generate_polyglot_project


class PolyglotScaffoldTests(unittest.TestCase):
    # Function: test_every_new_polyglot_route_emits_language_correct_project
    def test_every_new_polyglot_route_emits_language_correct_project(self):
        extensions = {
            "c": ".c", "cpp": ".cpp", "cobol": ".cob", "ruby": ".rb",
            "kotlin": ".kt", "rust": ".rs", "php": ".php", "dart": ".dart",
            "swift": ".swift", "scala": ".scala", "clojure": ".clj",
            "shell": ".sh", "r": ".R", "julia": ".jl", "haskell": ".hs",
            "lisp": ".lisp", "rpg": ".rpgle",
            "elixir": ".ex", "erlang": ".erl",
        }
        for language, extension in extensions.items():
            with self.subTest(language=language):
                files = generate_polyglot_project(language, "Demo", "Orders", {})
                self.assertTrue(files)
                self.assertTrue(any(path.endswith(extension) for path in files))
                self.assertTrue(all(path.startswith("ModernizedApp/") for path in files))

    # Function: test_ibmi_project_contains_rpg_cl_db2_and_project_metadata
    def test_ibmi_project_contains_rpg_cl_db2_and_project_metadata(self):
        files = generate_polyglot_project("rpg", "Demo", "Orders", {})
        paths = "\n".join(files).casefold()
        contents = "\n".join(files.values()).casefold()
        self.assertIn(".rpgle", paths)
        self.assertIn(".clle", paths)
        self.assertIn("schema.sql", paths)
        self.assertIn("iproj.json", paths)
        self.assertIn("crtbnrpg", contents)
        self.assertIn("db2 for i", contents)


if __name__ == "__main__":
    unittest.main()
