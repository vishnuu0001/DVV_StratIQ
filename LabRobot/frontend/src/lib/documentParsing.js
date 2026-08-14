// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: LabRobot — frontend/src/lib (documentParsing.js)
// Date: 2026-08-14
// ---------------------------------------------------------------------------
// Client-side, dependency-minimal text extraction for the AI Lab "Studio"
// document Q&A simulation (AILabCatalog.jsx). Everything here is a
// deterministic parser, not an LLM call:
//
//   .pdf  — pdfjs-dist (Mozilla's PDF.js) reads the real text layer.
//   .docx — a .docx is a ZIP of XML; unzip with jszip and read the <w:t>
//           text runs out of word/document.xml with the browser's native
//           DOMParser. No mammoth/docx-specific library needed.
//   .xlsx — same idea: unzip with jszip, resolve xl/sharedStrings.xml
//           against each xl/worksheets/sheetN.xml to get real cell values.
//
// The `xlsx` and `mammoth` npm packages were deliberately NOT used — at the
// time this was written, the npm-published `xlsx` package carries two
// unpatched high-severity advisories (prototype pollution + ReDoS) with no
// fix available via npm, and pulling `mammoth` for a single-tag extraction
// job wasn't worth another dependency once the ZIP+XML approach was already
// needed for .xlsx. See heuristicQA.js for how this extracted text is
// searched/summarized — also heuristic, not model-based.
import * as pdfjsLib from 'pdfjs-dist'
import pdfjsWorkerUrl from 'pdfjs-dist/build/pdf.worker.min.mjs?url'
import JSZip from 'jszip'
import { ACCEPTED_EXTENSIONS, MAX_FILE_BYTES } from './documentTypes'

pdfjsLib.GlobalWorkerOptions.workerSrc = pdfjsWorkerUrl

// Function: extensionOf
function extensionOf(fileName) {
  const dot = fileName.lastIndexOf('.')
  return dot === -1 ? '' : fileName.slice(dot).toLowerCase()
}

// Function: countWords
function countWords(text) {
  const matches = text.match(/\S+/g)
  return matches ? matches.length : 0
}

// ─── PDF ─────────────────────────────────────────────────────────────────

// Function: extractPdf
async function extractPdf(arrayBuffer) {
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
    stats: { 'Pages': doc.numPages, 'Words': countWords(segments.map((s) => s.text).join(' ')) },
  }
}

// ─── DOCX ────────────────────────────────────────────────────────────────

// Function: extractDocx
async function extractDocx(arrayBuffer) {
  const zip = await JSZip.loadAsync(arrayBuffer)
  const xmlText = await zip.file('word/document.xml')?.async('text')
  if (!xmlText) throw new Error('word/document.xml not found — this .docx may be corrupt or password-protected.')

  const xml = new DOMParser().parseFromString(xmlText, 'application/xml')
  if (xml.querySelector('parsererror')) throw new Error('Could not parse document.xml as XML.')

  const WORD_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
  const paragraphs = Array.from(xml.getElementsByTagNameNS(WORD_NS, 'p'))
  const segments = paragraphs
    .map((p, idx) => {
      const runs = Array.from(p.getElementsByTagNameNS(WORD_NS, 't'))
      const text = runs.map((t) => t.textContent).join('').trim()
      return { ref: `Paragraph ${idx + 1}`, text }
    })
    .filter((seg) => seg.text.length > 0)

  return {
    kind: 'docx',
    segments,
    stats: { 'Paragraphs': segments.length, 'Words': countWords(segments.map((s) => s.text).join(' ')) },
  }
}

// ─── XLSX ────────────────────────────────────────────────────────────────

const COLUMN_LETTERS_RE = /^[A-Z]+/

// Function: columnLetters
function columnLetters(cellRef) {
  return (cellRef.match(COLUMN_LETTERS_RE) || [''])[0]
}

// Function: extractXlsx
async function extractXlsx(arrayBuffer) {
  const zip = await JSZip.loadAsync(arrayBuffer)

  const sharedStringsXml = await zip.file('xl/sharedStrings.xml')?.async('text')
  const sharedStrings = []
  if (sharedStringsXml) {
    const doc = new DOMParser().parseFromString(sharedStringsXml, 'application/xml')
    Array.from(doc.getElementsByTagName('si')).forEach((si) => {
      // A shared string can be a single <t> or several <r><t> rich-text runs.
      const runs = Array.from(si.getElementsByTagName('t'))
      sharedStrings.push(runs.map((t) => t.textContent).join(''))
    })
  }

  const workbookXml = await zip.file('xl/workbook.xml')?.async('text')
  const sheetNames = []
  if (workbookXml) {
    const doc = new DOMParser().parseFromString(workbookXml, 'application/xml')
    Array.from(doc.getElementsByTagName('sheet')).forEach((s) => sheetNames.push(s.getAttribute('name')))
  }

  const sheetFiles = Object.keys(zip.files)
    .filter((path) => /^xl\/worksheets\/sheet\d+\.xml$/.test(path))
    .sort((a, b) => {
      const na = Number.parseInt(/sheet(\d+)\.xml/.exec(a)[1], 10)
      const nb = Number.parseInt(/sheet(\d+)\.xml/.exec(b)[1], 10)
      return na - nb
    })

  const segments = []
  let totalRows = 0
  let totalCells = 0

  for (let i = 0; i < sheetFiles.length; i++) {
    const sheetXml = await zip.file(sheetFiles[i]).async('text')
    const doc = new DOMParser().parseFromString(sheetXml, 'application/xml')
    const sheetName = sheetNames[i] || `Sheet${i + 1}`
    const rows = Array.from(doc.getElementsByTagName('row'))
    totalRows += rows.length

    rows.forEach((row) => {
      const rowIndex = row.getAttribute('r') || '?'
      const cells = Array.from(row.getElementsByTagName('c'))
      const values = cells.map((cell) => {
        const type = cell.getAttribute('t')
        const vNode = cell.getElementsByTagName('v')[0]
        const raw = vNode ? vNode.textContent : ''
        if (type === 's') {
          const idx = Number.parseInt(raw, 10)
          return Number.isInteger(idx) ? (sharedStrings[idx] ?? '') : ''
        }
        if (type === 'inlineStr') {
          const t = cell.getElementsByTagName('t')[0]
          return t ? t.textContent : ''
        }
        return raw
      })
      totalCells += values.filter((v) => v !== '').length
      const rowText = cells
        .map((cell, colIdx) => `${columnLetters(cell.getAttribute('r') || '')}${rowIndex}=${values[colIdx]}`)
        .filter((entry) => !entry.endsWith('='))
        .join(', ')
      if (rowText) {
        segments.push({ ref: `${sheetName}!Row ${rowIndex}`, text: rowText })
      }
    })
  }

  return {
    kind: 'xlsx',
    segments,
    stats: { 'Sheets': sheetFiles.length, 'Rows': totalRows, 'Non-empty cells': totalCells },
  }
}

// ─── Public entry point ─────────────────────────────────────────────────

// Function: parseDocument
export async function parseDocument(file) {
  const ext = extensionOf(file.name)
  if (!ACCEPTED_EXTENSIONS.includes(ext)) {
    throw new Error(`Unsupported file type "${ext || file.name}". Upload a .pdf, .docx, or .xlsx file.`)
  }
  if (file.size > MAX_FILE_BYTES) {
    throw new Error(`"${file.name}" is ${(file.size / (1024 * 1024)).toFixed(1)} MB, over the ${MAX_FILE_BYTES / (1024 * 1024)} MB limit for in-browser parsing.`)
  }

  const arrayBuffer = await file.arrayBuffer()
  let extracted
  if (ext === '.pdf') extracted = await extractPdf(arrayBuffer)
  else if (ext === '.docx') extracted = await extractDocx(arrayBuffer)
  else extracted = await extractXlsx(arrayBuffer)

  return {
    id: `${file.name}-${file.lastModified}-${file.size}`,
    fileName: file.name,
    sizeBytes: file.size,
    uploadedAt: new Date().toISOString(),
    ...extracted,
  }
}
