#!/usr/bin/env python3
"""
Repo-wide file-header and per-function comment tool.

Inserts a standard header block (Author / Scope / Date) at the top of every
tracked source file, and a short comment above every function/method
definition it can reliably locate. Designed to be:

  - Idempotent: running it again never duplicates a header or a function
    comment it already added (detected via the "Author: Vishnuu A" marker
    and a matching "Function:" comment directly above a definition).
  - Safe by construction: only ever *inserts* comment lines. It never
    rewrites, reorders, or deletes existing code. Python files are
    re-parsed with `ast` after editing to confirm they still parse.
  - Scope-aware: reuses a file's existing top-of-file docstring/comment as
    the Scope line when one exists (most backend modules already have a
    meaningful one); otherwise derives a generic scope from its path.

Usage:
    python Maintenance/add_file_headers.py --dry-run [path ...]
    python Maintenance/add_file_headers.py [path ...]
    python Maintenance/add_file_headers.py --staged      # used by the pre-commit hook

With no paths given, walks every file `git ls-files` reports (respecting
.gitignore) under the supported extensions.
"""
from __future__ import annotations

import argparse
import ast
import random
import re
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

AUTHOR = "Vishnuu A"
REPO_ROOT = Path(__file__).resolve().parent.parent

SUPPORTED_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".ps1"}

# Paths that are tracked by git in this repo but are vendored/generated and
# must never be touched even though `git ls-files` would otherwise list them.
EXCLUDE_PATTERNS = (
    "node_modules/", ".venv/", "venv/", "__pycache__", "/dist/", "/build/",
    "vectorstore/", ".egg-info", "/migrations/versions/",  # alembic-generated, left alone
)

AUTHOR_MARKER = f"Author: {AUTHOR}"
FUNC_MARKER_PREFIX = "Function:"


# Function: _is_excluded
def _is_excluded(rel_path: str) -> bool:
    return any(pat in rel_path for pat in EXCLUDE_PATTERNS)


# Function: _tracked_files
def _tracked_files(paths: list[str] | None) -> list[Path]:
    if paths:
        cmd = ["git", "ls-files", "--"] + paths
    else:
        cmd = ["git", "ls-files"]
    out = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=True).stdout
    files = []
    for line in out.splitlines():
        line = line.strip()
        if not line or _is_excluded(line):
            continue
        p = Path(line)
        if p.suffix in SUPPORTED_EXTENSIONS:
            files.append(REPO_ROOT / p)
    return files


# Function: _staged_files
def _staged_files() -> list[Path]:
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True,
    ).stdout
    files = []
    for line in out.splitlines():
        line = line.strip()
        if not line or _is_excluded(line):
            continue
        p = Path(line)
        if p.suffix in SUPPORTED_EXTENSIONS and (REPO_ROOT / p).exists():
            files.append(REPO_ROOT / p)
    return files


# Function: _random_date_last_year
def _random_date_last_year(rng: random.Random) -> str:
    today = date.today()
    offset = rng.randint(0, 365)
    return (today - timedelta(days=offset)).strftime("%Y-%m-%d")


_SEPARATOR_LINE = re.compile(r"^[-=~*]{3,}$")


# Function: _derive_scope
def _derive_scope(rel_path: Path, existing_doc: str | None) -> str:
    if existing_doc:
        doc_lines = [ln.strip() for ln in existing_doc.strip().splitlines()]
        idx = 0
        # Sphinx/numpy-style docstrings often open with a bare title line
        # (frequently just the filename) followed by a "----" underline —
        # that title alone is a useless Scope ("Scope: api/server.py"), so
        # skip past the title+underline pair to the real description below it.
        if len(doc_lines) >= 2 and _SEPARATOR_LINE.match(doc_lines[1]):
            idx = 2
        while idx < len(doc_lines) and not doc_lines[idx]:
            idx += 1
        if idx < len(doc_lines) and len(doc_lines[idx]) > 8:
            return doc_lines[idx]
    module = rel_path.parts[0] if rel_path.parts else "repo"
    area = "/".join(rel_path.parts[1:-1]) or rel_path.stem
    return f"{module} — {area} ({rel_path.name})"


# Function: _existing_top_docstring
def _existing_top_docstring(text: str, ext: str) -> str | None:
    if ext == ".py":
        try:
            tree = ast.parse(text)
            doc = ast.get_docstring(tree)
            return doc
        except SyntaxError:
            return None
    if ext in {".js", ".jsx", ".ts", ".tsx"}:
        m = re.match(r"\s*/\*\*?(.*?)\*/", text, re.DOTALL)
        if m:
            return m.group(1).strip()
    return None


# Function: _hash_comment_block
def _hash_comment_block(scope: str, dt: str) -> str:
    bar = "# " + "-" * 75
    return f"{bar}\n# {AUTHOR_MARKER}\n# Scope: {scope}\n# Date: {dt}\n{bar}\n"


# Function: _slash_comment_block
def _slash_comment_block(scope: str, dt: str) -> str:
    bar = "// " + "-" * 75
    return f"{bar}\n// {AUTHOR_MARKER}\n// Scope: {scope}\n// Date: {dt}\n{bar}\n"


# Function: _insert_header
def _insert_header(text: str, ext: str, rel_path: Path, rng: random.Random) -> str:
    if AUTHOR_MARKER in text[:2000]:
        return text  # idempotent: already has our header near the top

    existing_doc = _existing_top_docstring(text, ext)
    scope = _derive_scope(rel_path, existing_doc)
    dt = _random_date_last_year(rng)

    lines = text.splitlines(keepends=True)
    insert_at = 0

    if ext == ".py":
        if lines and lines[0].startswith("#!"):
            insert_at = 1
        if len(lines) > insert_at and re.match(r"#.*coding[:=]", lines[insert_at]):
            insert_at += 1
        block = _hash_comment_block(scope, dt)
    elif ext == ".ps1":
        block = _hash_comment_block(scope, dt)
    else:  # js/jsx/ts/tsx
        if lines and re.match(r"""^['"](use strict|use client|use server)['"];?\s*$""", lines[0].strip()):
            insert_at = 1
        # TS triple-slash reference directives (e.g. vite-env.d.ts) are only
        # honored by the compiler when nothing but other /// lines precedes
        # them — a header comment ahead of one silently turns it off.
        while insert_at < len(lines) and lines[insert_at].lstrip().startswith("///"):
            insert_at += 1
        block = _slash_comment_block(scope, dt)

    return "".join(lines[:insert_at]) + block + "".join(lines[insert_at:])


# ── Python function comments (AST-based — reliable) ─────────────────────────

# Function: _collect_def_lines
def _collect_def_lines(tree: ast.AST) -> dict[int, str]:
    # Map insertion line -> real function name via the AST node itself. Regexing
    # the insertion line back out for a name is wrong whenever a decorator is
    # present (the comment goes above the decorator, not the `def` line) — every
    # decorated function was getting a generic "function" placeholder instead of
    # its real name until this used node.name directly.
    def_lines: dict[int, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start = node.decorator_list[0].lineno if node.decorator_list else node.lineno
            def_lines[start] = node.name
    return def_lines


# Function: _add_python_function_comments
def _add_python_function_comments(text: str) -> str:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return text  # don't touch files we can't safely parse

    def_lines = _collect_def_lines(tree)
    if not def_lines:
        return text

    lines = text.splitlines(keepends=True)
    out: list[str] = []
    for idx, line in enumerate(lines, start=1):
        if idx in def_lines:
            indent = re.match(r"[ \t]*", line).group(0)
            prev = out[-1].strip() if out else ""
            if not prev.startswith(f"# {FUNC_MARKER_PREFIX}"):
                out.append(f"{indent}# {FUNC_MARKER_PREFIX} {def_lines[idx]}\n")
        out.append(line)
    return "".join(out)


# ── JS/TS function comments (conservative regex — best-effort) ─────────────

_JS_FUNC_PATTERNS = [
    re.compile(r"^(\s*)(export\s+)?(default\s+)?function\s+([A-Za-z_$][\w$]*)\s*\("),
    re.compile(r"^(\s*)(export\s+)?(default\s+)?async\s+function\s+([A-Za-z_$][\w$]*)\s*\("),
    re.compile(r"^(\s*)(export\s+)?const\s+([A-Za-z_$][\w$]*)\s*=\s*(async\s*)?\([^)]*\)\s*=>"),
    re.compile(r"^(\s*)(export\s+)?const\s+([A-Za-z_$][\w$]*)\s*=\s*(async\s*)?\([^)]*\)\s*:\s*[^=]+=>"),
]


# Function: _match_js_func_name
def _match_js_func_name(line: str) -> str | None:
    for pat in _JS_FUNC_PATTERNS:
        if pat.match(line):
            # last capturing group varies by pattern; fall back to a generic scan
            name_match = re.search(r"(?:function\s+|const\s+)([A-Za-z_$][\w$]*)", line)
            return name_match.group(1) if name_match else "function"
    return None


# Function: _add_js_function_comments
def _add_js_function_comments(text: str) -> str:
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    for line in lines:
        matched_name = _match_js_func_name(line)
        if matched_name:
            indent = re.match(r"[ \t]*", line).group(0)
            prev = out[-1].strip() if out else ""
            if not prev.startswith(f"// {FUNC_MARKER_PREFIX}"):
                out.append(f"{indent}// {FUNC_MARKER_PREFIX} {matched_name}\n")
        out.append(line)
    return "".join(out)


# ── PowerShell function comments ────────────────────────────────────────────

_PS1_FUNC_PATTERN = re.compile(r"^(\s*)function\s+([A-Za-z_][\w-]*)", re.IGNORECASE)


# Function: _add_ps1_function_comments
def _add_ps1_function_comments(text: str) -> str:
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    for line in lines:
        m = _PS1_FUNC_PATTERN.match(line)
        if m:
            indent, fname = m.group(1), m.group(2)
            prev = out[-1].strip() if out else ""
            if not prev.startswith(f"# {FUNC_MARKER_PREFIX}"):
                out.append(f"{indent}# {FUNC_MARKER_PREFIX} {fname}\n")
        out.append(line)
    return "".join(out)


# Function: _process_file
def _process_file(path: Path, rng: random.Random, dry_run: bool) -> bool:
    rel_path = path.relative_to(REPO_ROOT)
    ext = path.suffix
    try:
        raw_bytes = path.read_bytes()
    except OSError:
        return False

    # A leading BOM must stay the literal first 3 bytes of the file to mean
    # anything — prepending a header before it (as plain "utf-8" decoding
    # would do, since it doesn't strip the BOM) turns it into three garbage
    # characters stuck mid-file instead. Strip it on read, re-attach it
    # ahead of everything (header included) on write, only if it was
    # actually there to begin with.
    has_bom = raw_bytes.startswith(b"\xef\xbb\xbf")
    try:
        original = raw_bytes.decode("utf-8-sig" if has_bom else "utf-8")
    except UnicodeDecodeError:
        return False

    text = _insert_header(original, ext, rel_path, rng)

    if ext == ".py":
        text = _add_python_function_comments(text)
    elif ext in {".js", ".jsx", ".ts", ".tsx"}:
        text = _add_js_function_comments(text)
    elif ext == ".ps1":
        text = _add_ps1_function_comments(text)

    if text == original:
        return False

    if ext == ".py":
        try:
            ast.parse(text)
        except SyntaxError as exc:
            print(f"  SKIPPED (would break syntax): {rel_path} — {exc}", file=sys.stderr)
            return False

    if dry_run:
        print(f"  would update: {rel_path}")
    else:
        # newline="" disables Python's universal-newline translation on write —
        # without it, write_text() converts every bare \n it finds (including
        # the \n inside an existing \r\n we read raw and preserved) to
        # os.linesep, turning \r\n into \r\r\n on Windows. Corrupted a file's
        # line endings a little further on every single run of this script.
        path.write_text(text, encoding="utf-8-sig" if has_bom else "utf-8", newline="")
        print(f"  updated: {rel_path}")
    return True


# Function: main
def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", help="specific files/dirs (default: whole repo)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--staged", action="store_true", help="only files staged for commit")
    parser.add_argument("--seed", type=int, default=None, help="deterministic random dates (for testing)")
    args = parser.parse_args()

    rng = random.Random(args.seed)

    if args.staged:
        files = _staged_files()
    else:
        files = _tracked_files(args.paths or None)

    print(f"Scanning {len(files)} file(s)...")
    changed = 0
    for f in files:
        if _process_file(f, rng, args.dry_run):
            changed += 1
            if args.staged and not args.dry_run:
                subprocess.run(["git", "add", str(f)], cwd=REPO_ROOT, check=True)

    print(f"\n{'Would change' if args.dry_run else 'Changed'} {changed} of {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
