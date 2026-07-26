# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: TraceForge — api/tests (test_text_parser.py)
# Date: 2025-12-26
# ---------------------------------------------------------------------------
from traceforge.parsing.text import parse_text


# Function: test_markdown_is_parsed_into_section_aware_chunks
def test_markdown_is_parsed_into_section_aware_chunks(tmp_path):
    source = tmp_path / "features.md"
    source.write_text("# Novastra-ITSM\n\nTicket intelligence and duplicate detection.\n\n## TraceForge\n\nGenerate requirements and tests.\n", encoding="utf-8")

    parsed = parse_text(str(source))
    assert [block.section_path for block in parsed.blocks] == [
        "Novastra-ITSM", "Novastra-ITSM", "TraceForge", "TraceForge"
    ]
    combined = "\n".join(block.text for block in parsed.blocks)
    assert "Ticket intelligence" in combined
    assert "Generate requirements" in combined
