// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: LabRobot — frontend/src/lib (documentTypes.js)
// Date: 2026-08-14
// ---------------------------------------------------------------------------
// Deliberately its own tiny, dependency-free module. documentParsing.js
// statically imports pdfjs-dist + jszip (~1.3 MB combined) — components
// that only need the accepted-extension list for a file input's `accept`
// attribute should import it from here, not from documentParsing.js,
// otherwise every consumer would eagerly pull that ~1.3 MB into the main
// bundle just to read two constants. See DocumentStudio.jsx for how the
// actual parser is loaded on demand instead.
export const ACCEPTED_EXTENSIONS = ['.pdf', '.docx', '.xlsx']
export const MAX_FILE_BYTES = 20 * 1024 * 1024 // 20 MB — keeps in-browser parsing snappy
