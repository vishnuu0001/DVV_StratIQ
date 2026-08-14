// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: LabRobot — frontend/src/lib (heuristicQA.js)
// Date: 2026-08-14
// ---------------------------------------------------------------------------
// Answers a question about a parsed document (see documentParsing.js) using
// plain keyword-frequency heuristics — NOT an LLM. No model, no network
// call, no prompt sent anywhere: just tokenizing, substring/whole-word
// matching, and term-frequency scoring over the text already extracted
// client-side. See AILabCatalog.jsx's file header for why this app keeps
// the AI Lab tab's "AI" behavior entirely heuristic.
const STOPWORDS = new Set([
  'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
  'to', 'of', 'in', 'on', 'at', 'for', 'with', 'about', 'as', 'by', 'from',
  'and', 'or', 'but', 'if', 'so', 'than', 'that', 'this', 'these', 'those',
  'what', 'when', 'where', 'which', 'who', 'whom', 'why', 'how',
  'does', 'do', 'did', 'can', 'could', 'would', 'should', 'will',
  'it', 'its', 'i', 'you', 'your', 'me', 'my', 'we', 'our', 'they', 'their',
  'document', 'file', 'please', 'tell', 'me', 'show', 'give', 'summarise', 'summarize',
])

// Function: tokenize
function tokenize(text) {
  const matches = (text.toLowerCase().match(/[a-z0-9]+/g)) || []
  return matches.filter((w) => w.length > 1 && !STOPWORDS.has(w))
}

// Function: buildTermFrequency
function buildTermFrequency(segments) {
  const freq = new Map()
  for (const seg of segments) {
    for (const term of tokenize(seg.text)) {
      freq.set(term, (freq.get(term) || 0) + 1)
    }
  }
  return freq
}

const COUNT_INTENTS = [
  { pattern: /how many pages|page count|number of pages/i, statKey: 'Pages' },
  { pattern: /how many sheets|sheet count|number of sheets/i, statKey: 'Sheets' },
  { pattern: /how many rows|row count|number of rows/i, statKey: 'Rows' },
  { pattern: /how many paragraphs|paragraph count/i, statKey: 'Paragraphs' },
  { pattern: /how many words|word count/i, statKey: 'Words' },
  { pattern: /how many cells|cell count/i, statKey: 'Non-empty cells' },
]

// Function: snippetAround
// Trims a matched segment to a readable window around the first hit instead
// of dumping a whole page/paragraph/row back at the user.
function snippetAround(text, terms, radius = 90) {
  const lower = text.toLowerCase()
  let hitAt = -1
  for (const term of terms) {
    const idx = lower.indexOf(term)
    if (idx !== -1 && (hitAt === -1 || idx < hitAt)) hitAt = idx
  }
  if (hitAt === -1) return text.length > 220 ? `${text.slice(0, 220)}…` : text
  const start = Math.max(0, hitAt - radius)
  const end = Math.min(text.length, hitAt + radius)
  return `${start > 0 ? '…' : ''}${text.slice(start, end)}${end < text.length ? '…' : ''}`
}

// Function: answerHeuristically
// Returns { kind: 'stat' | 'summary' | 'answer' | 'empty' | 'none', text, citations }
export function answerHeuristically(question, doc) {
  if (!doc || !doc.segments || doc.segments.length === 0) {
    return { kind: 'empty', text: "This document didn't yield any extractable text to search.", citations: [] }
  }

  const q = question.trim()
  if (!q) return { kind: 'empty', text: 'Type a question about the document, or click "Summarize".', citations: [] }

  for (const { pattern, statKey } of COUNT_INTENTS) {
    if (pattern.test(q) && doc.stats[statKey] != null) {
      return { kind: 'stat', text: `${statKey}: ${doc.stats[statKey]}`, citations: [] }
    }
  }

  const isSummaryRequest = /summar/i.test(q)
  const queryTerms = tokenize(q)

  if (isSummaryRequest || queryTerms.length === 0) {
    const freq = buildTermFrequency(doc.segments)
    const ranked = doc.segments
      .map((seg) => {
        const terms = tokenize(seg.text)
        const score = terms.reduce((sum, t) => sum + (freq.get(t) || 0), 0)
        return { seg, score }
      })
      .filter((r) => r.seg.text.length > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, 3)

    if (ranked.length === 0) {
      return { kind: 'empty', text: 'Not enough text in this document to summarize.', citations: [] }
    }
    return {
      kind: 'summary',
      text: `Heuristic extractive summary (top ${ranked.length} highest keyword-density section${ranked.length === 1 ? '' : 's'}):`,
      citations: ranked.map((r) => ({ ref: r.seg.ref, snippet: snippetAround(r.seg.text, []) })),
    }
  }

  const scored = doc.segments
    .map((seg) => {
      const lower = seg.text.toLowerCase()
      let score = 0
      for (const term of queryTerms) {
        if (lower.includes(term)) score += 1
        const wholeWordHit = new RegExp(`\\b${term}\\b`, 'i').test(seg.text)
        if (wholeWordHit) score += 1
      }
      return { seg, score }
    })
    .filter((r) => r.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 3)

  if (scored.length === 0) {
    const freq = buildTermFrequency(doc.segments)
    const topTerms = [...freq.entries()].sort((a, b) => b[1] - a[1]).slice(0, 6).map(([term]) => term)
    return {
      kind: 'none',
      text: `No direct mention of "${queryTerms.join(' ')}" found in ${doc.fileName}. ` +
        (topTerms.length ? `Frequently-occurring terms in this document: ${topTerms.join(', ')}.` : ''),
      citations: [],
    }
  }

  return {
    kind: 'answer',
    text: `Found ${scored.length} matching section${scored.length === 1 ? '' : 's'} for "${queryTerms.join(' ')}" ` +
      `(keyword match, not model-generated):`,
    citations: scored.map((r) => ({ ref: r.seg.ref, snippet: snippetAround(r.seg.text, queryTerms) })),
  }
}
