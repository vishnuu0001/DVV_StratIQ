// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: LabRobot — frontend/src/lib (pdfExtraction.js)
// Date: 2026-08-15
// ---------------------------------------------------------------------------
// Split out of documentParsing.js on purpose: this is the ONLY file that
// imports pdfjs-dist. documentParsing.js dynamic-imports this module lazily,
// and only for a .pdf upload — a DOCX or XLSX upload never touches this file
// or pdfjs-dist at all. Previously pdfjs-dist was imported unconditionally
// at documentParsing.js's top level, so if pdfjs-dist's own module
// evaluation ever failed in a given browser (locked-down enterprise policy,
// a privacy extension stubbing Canvas/DOMMatrix APIs pdfjs touches at
// import time, etc.), EVERY upload — including DOCX/XLSX, which don't need
// pdfjs-dist — broke with it. This isolation means a PDF-specific failure
// stays PDF-specific.
import * as pdfjsLib from 'pdfjs-dist'
import pdfjsWorkerUrl from 'pdfjs-dist/build/pdf.worker.min.mjs?url'

pdfjsLib.GlobalWorkerOptions.workerSrc = pdfjsWorkerUrl

// Function: countWords
function countWords(text) {
  const matches = text.match(/\S+/g)
  return matches ? matches.length : 0
}

// Function: extractPdf
export async function extractPdf(arrayBuffer) {
  const doc = await pdfjsLib.getDocument({ data: arrayBuffer }).promise
  const segments = []
  for (let pageNum = 1; pageNum <= doc.numPages; pageNum++) {
    const page = await doc.getPage(pageNum)
    const content = await page.getTextContent()
    const text = content.items.map((item) => item.str).join(' ').replace(/\s+/g, ' ').trim()
    segments.push({ ref: `Page ${pageNum}`, text })
  }
  return {
    kind: 'pdf',
    segments,
    stats: { Pages: doc.numPages, Words: countWords(segments.map((s) => s.text).join(' ')) },
  }
}
