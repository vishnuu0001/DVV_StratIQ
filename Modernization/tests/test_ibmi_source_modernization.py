# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — tests (test_ibmi_source_modernization.py)
# Date: 2026-05-28
# ---------------------------------------------------------------------------
import tempfile
import unittest
from pathlib import Path

from services.analyzer import analyze_project
from services.modernizer.conversion_pipeline import (
    _CONVERTIBLE,
    _collect_source_files,
    _extract_file_structure,
    _stack_conversion_hints,
)
from services.modernizer._shared import _make_output_path
from services.modernizer.docs_generation import _read_source_files


class IbmiSourceModernizationTests(unittest.TestCase):
    # Function: test_all_core_ibmi_source_families_are_convertible
    def test_all_core_ibmi_source_families_are_convertible(self):
        expected = {
            ".rpg": "rpg", ".rpgle": "rpg", ".sqlrpgle": "rpg",
            ".clp": "ibmi_cl", ".clle": "ibmi_cl",
            ".dds": "ibmi_dds", ".pf": "ibmi_dds", ".lf": "ibmi_dds",
            ".dspf": "ibmi_display", ".prtf": "ibmi_printer",
            ".cpy": "ibmi_copybook",
        }
        for extension, language in expected.items():
            self.assertEqual(language, _CONVERTIBLE[extension])

    # Function: test_ibmi_analysis_extracts_dependencies_and_source_semantics
    def test_ibmi_analysis_extracts_dependencies_and_source_semantics(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "ORDER.sqlrpgle").write_text(
                """**free
ctl-opt main(Main);
/copy QRPGLESRC,COMMON
dcl-f ORDHDR keyed usage(*update);
dcl-proc Main;
  chain orderId ORDHDR;
  exec sql update ORDHDR set STATUS = 'P' where ORDER_ID = :orderId;
  callp PriceOrder(orderId);
  *inlr = *on;
end-proc;
""",
                encoding="utf-8",
            )
            (root / "JOB.clle").write_text(
                "PGM\nCALL PGM(ORDER) PARM(&ID)\nMONMSG MSGID(CPF0000)\nENDPGM\n",
                encoding="utf-8",
            )
            (root / "ORDHDR.pf").write_text(
                "     A          R ORDHDRR\n     A            ORDERID       9P 0\n",
                encoding="utf-8",
            )
            (root / "ORDERDSP.dspf").write_text(
                "     A          R ORDERFMT\n     A                                      CF03(03)\n",
                encoding="utf-8",
            )

            report = analyze_project(str(root), target_stack="dotnet_react")
            ibmi = report["ibmi"]

            self.assertTrue(ibmi["detected"])
            self.assertEqual(4, ibmi["source_files"])
            self.assertIn("ORDHDR", ibmi["database_and_device_files"])
            self.assertIn("QRPGLESRC,COMMON", ibmi["copybooks"])
            self.assertIn("ibmi_rpg", report["tech_stack"])
            self.assertEqual("IBM i / AS400 RPG application", report["architecture"]["pattern"])
            collected = {path.suffix.casefold() for path in _collect_source_files(str(root))}
            self.assertEqual({".sqlrpgle", ".clle", ".pf", ".dspf"}, collected)
            csharp_context = _read_source_files(str(root), "csharp", "order")
            self.assertIn("ORDER.sqlrpgle", csharp_context)
            self.assertIn("chain orderId ORDHDR", csharp_context)

    # Function: test_rpg_structure_and_target_hints_preserve_business_semantics
    def test_rpg_structure_and_target_hints_preserve_business_semantics(self):
        source = """**free
dcl-f CUSTOMER keyed;
dcl-proc Calculate;
end-proc;
/copy QRPGLESRC,COMMON
"""
        structure = _extract_file_structure(source, "rpg")
        self.assertIn("PROCEDURE: Calculate", structure)
        self.assertIn("FILE: CUSTOMER", structure)
        self.assertIn("COPYBOOK: QRPGLESRC,COMMON", structure)

        for language in ("java", "csharp", "python", "typescript", "go"):
            with self.subTest(language=language):
                hints = _stack_conversion_hints("rpg", {"language": language})
                self.assertIn("packed/zoned decimal", hints)
                self.assertIn("CHAIN/SETLL/READE", hints)
                self.assertIn("DDS", hints)
                self.assertIn("CL CALL/SBMJOB", hints)

    # Function: test_same_named_ibmi_members_do_not_overwrite_each_other
    def test_same_named_ibmi_members_do_not_overwrite_each_other(self):
        root = Path("legacy")
        outputs = {
            _make_output_path(root / f"ORDER{extension}", root, "java", "Demo", "spring_boot")
            for extension in (".rpgle", ".clle", ".pf", ".lf", ".dspf", ".prtf")
        }
        self.assertEqual(6, len(outputs))
        self.assertTrue(any(path.endswith("ORDERRpgProgram.java") for path in outputs))
        self.assertTrue(any(path.endswith("ORDERDisplayFile.java") for path in outputs))


if __name__ == "__main__":
    unittest.main()
