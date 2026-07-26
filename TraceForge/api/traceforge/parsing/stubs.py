# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §4.2 parsers not implemented this pass either — narrower formats than the
# Date: 2026-02-02
# ---------------------------------------------------------------------------
"""§4.2 parsers not implemented this pass either — narrower formats than the
JIRA/GitHub/ServiceNow + BRD/FSD/SolutionDoc/TestPlan/TestCase/TestScript scope this
build actually targets. Each raises a clear, typed error instead of silently accepting
a file it can't actually parse. See TraceForge/PROGRESS.md."""
from __future__ import annotations


class ParserNotImplemented(NotImplementedError):
    # Function: __init__
    def __init__(self, doc_type: str):
        super().__init__(
            f"'{doc_type}' parsing is not implemented (pptx/python-pptx, vsdx/bpmn shape "
            f"parsing, vision-model process-map OCR). docx, pdf, xlsx, and legacy code "
            f"(tree-sitter) are all real — see TraceForge/PROGRESS.md."
        )


# Function: parse_pptx
def parse_pptx(path: str):
    raise ParserNotImplemented("pptx")


# Function: parse_bpmn
def parse_bpmn(path: str):
    raise ParserNotImplemented("bpmn/vsdx")


# Function: parse_image
def parse_image(path: str):
    raise ParserNotImplemented("process-map image (vision model)")
