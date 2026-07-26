#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Setup script for PostgreSQL + pgvector indexing.
# Date: 2025-09-27
# ---------------------------------------------------------------------------
"""Setup script for PostgreSQL + pgvector indexing.

Steps:
  1. Copies .env.example -> .env (first run only)
  2. Installs backend Python dependencies
  3. Optionally wipes existing pgvector collection
  4. Indexes all documents in data/ into PostgreSQL

Run: python setup.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
ENV_FILE = ROOT / ".env"
ENV_EXAMPLE = ROOT / ".env.example"

SUPPORTED_EXTENSIONS = {
    ".docx",
    ".xlsx",
    ".xls",
    ".csv",
    ".txt",
    ".md",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
}


# Function: run
def run(cmd, **kw):
    print(f"\n>> {' '.join(cmd)}")
    subprocess.run(cmd, check=True, **kw)


if not ENV_FILE.exists():
    shutil.copy(ENV_EXAMPLE, ENV_FILE)
    print("Created .env from .env.example — edit it before running in production!")
else:
    print(".env already exists, skipping copy.")

run([sys.executable, "-m", "pip", "install", "-r", str(ROOT / "backend" / "requirements.txt")])

sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ENV_FILE)

import backend.config as cfg
from backend.rag.document_loader import load_file
from backend.rag.vectorstore import get_collection_stats, index_documents, wipe_collection

print("\n" + "=" * 62)
print("  INDEXING data/ -> PostgreSQL pgvector")
print("=" * 62)

print("\n>> Wiping existing vector collection…")
deleted = wipe_collection(provider=cfg.LLM_PROVIDER)
print(f"   Cleared {deleted} existing chunks from collection '{cfg.VECTOR_COLLECTION}'.")

data_dir = Path(cfg.DATA_DIR)
if not data_dir.exists():
    print(f"\n[WARN] data/ directory not found: {data_dir}")
    sys.exit(1)

files = sorted(
    fp
    for fp in data_dir.iterdir()
    if fp.is_file() and not fp.name.startswith("~$") and fp.suffix.lower() in SUPPORTED_EXTENSIONS
)

if not files:
    print("\nNo supported documents found in data/. Add files and re-run.")
    sys.exit(0)

all_docs = []
for fp in files:
    try:
        docs = load_file(fp)
    except Exception as exc:
        print(f"[FAIL] {fp.name}: {exc}")
        continue

    if not docs:
        print(f"[SKIP] {fp.name}: no content extracted")
        continue

    all_docs.extend(docs)
    print(f"[OK]   {fp.name}: {len(docs)} records")

if not all_docs:
    print("\n[WARN] No documents were loaded. Nothing indexed.")
    sys.exit(0)

chunks = index_documents(all_docs, provider=cfg.LLM_PROVIDER)
stats = get_collection_stats(cfg.LLM_PROVIDER)

print("\n" + "=" * 62)
print("  INDEXING SUMMARY")
print("=" * 62)
print(f"Files indexed: {len(files)}")
print(f"Chunks indexed this run: {chunks}")
print(f"Chunks currently in collection: {stats.get('total_chunks', 0)}")
print("\n[OK] PostgreSQL pgvector indexing complete.")
