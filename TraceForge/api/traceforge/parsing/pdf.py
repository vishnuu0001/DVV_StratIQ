# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: §4.2 .pdf parser: pymupdf text + layout, OCR fallback if the text layer is thin.
# Date: 2026-03-14
# ---------------------------------------------------------------------------
"""§4.2 .pdf parser: pymupdf text + layout, OCR fallback if the text layer is thin."""
from __future__ import annotations

import fitz  # pymupdf

from traceforge.parsing.common import ParsedBlock, ParsedDocument

_OCR_THRESHOLD_CHARS_PER_PAGE = 100


# Function: _ocr_page
def _ocr_page(page: "fitz.Page") -> str:
    try:
        import pytesseract
        from PIL import Image
        import io
        pix = page.get_pixmap(dpi=200)
        image = Image.open(io.BytesIO(pix.tobytes("png")))
        return pytesseract.image_to_string(image)
    except Exception:  # noqa: BLE001 — tesseract binary may not be installed on this VM
        return ""


# Function: parse_pdf
def parse_pdf(path: str) -> ParsedDocument:
    doc = fitz.open(path)
    blocks: list[ParsedBlock] = []
    cursor = 0
    try:
        for page_number, page in enumerate(doc, start=1):
            page_text = page.get_text("text")
            if len(page_text.strip()) < _OCR_THRESHOLD_CHARS_PER_PAGE:
                ocr_text = _ocr_page(page)
                if len(ocr_text.strip()) > len(page_text.strip()):
                    page_text = ocr_text

            for block in page.get_text("blocks"):
                text = str(block[4]).strip()
                if not text:
                    continue
                start = cursor
                end = start + len(text)
                blocks.append(ParsedBlock(text=text, section_path=f"Page {page_number}", char_start=start, char_end=end, page=page_number))
                cursor = end + 1
    finally:
        doc.close()

    return ParsedDocument(blocks=blocks)
