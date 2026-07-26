# Novastra-ITSM Architecture Upgrade

**Date**: May 2026  
**Version**: 2.0  
**Status**: Production Ready

## Overview

The Novastra-ITSM system has been upgraded to use **LanceDB** as the primary local vector store with **GPU-accelerated embeddings**. This upgrade provides:

- ✅ **Native GPU acceleration** for faster embedding generation
- ✅ **Local vector storage** (no external vector DB required)
- ✅ **Reduced latency** for similarity search
- ✅ **Lower operational overhead** (fewer external services)
- ✅ **Backward compatibility** with existing PostgreSQL operational data

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│          ServiceNow API / REST Sources          │
└──────────────────────┬──────────────────────────┘
                       │
         ┌─────────────▼──────────────┐
         │  Python Ingestion Program  │
         │  (servicenow_sync.py)      │
         └─────────────┬──────────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
       ▼               ▼               ▼
 ┌──────────────┐ ┌──────────────┐ ┌────────────────┐
 │ PostgreSQL   │ │  LanceDB     │ │ Embedding      │
 │  (Postgres)  │ │ (Local       │ │ Generator      │
 │              │ │  Vector Store)│ │ (GPU-native)   │
 │ Operational  │ │              │ │                │
 │ Data:        │ │ Vector       │ │ Models:        │
 │ - incidents  │ │ Embeddings   │ │ - nomic-embed  │
 │ - metadata   │ │ - similarity │ │ - all-minilm   │
 │              │ │   search     │ │ - BGE models   │
 └──────────────┘ └──────────────┘ └────────────────┘
       │               │
       └───────────────┼───────────────┐
                       │               │
                ┌──────▼───────┐       │
                │  Search/RAG  │◄──────┘
                │  API         │
                │  - /api/search│
                │  - /api/agent │
                │  - Hybrid Q&A │
                └──────────────┘
```

---

## Component Details

### 1. ServiceNow API Integration
**File**: `backend/services/servicenow_sync.py`

- Fetches incidents from ServiceNow with fields:
  - `incident_id`, `number`, `short_description`, `description`
  - `category`, `priority`, `state`, `assignment_group`
  - `created_on`, `updated_on`, work notes, close notes

### 2. PostgreSQL Storage (Operational)
**File**: `backend/services/operational_ingestion.py`

Stores raw incident data for operational querying:
```sql
CREATE TABLE sn_incidents (
    incident_id TEXT PRIMARY KEY,
    number TEXT,
    short_description TEXT,
    description TEXT,
    category TEXT,
    priority TEXT,
    assignment_group TEXT,
    state TEXT,
    created_on TIMESTAMPTZ,
    updated_on TIMESTAMPTZ,
    raw_json JSONB,
    last_synced_at TIMESTAMPTZ
);
```

### 3. LanceDB Vector Store (NEW)
**File**: `backend/services/lancedb_store.py`

Local GPU-optimized vector database:
- Path: `./vectorstore/lancedb` (configurable)
- Table: `incidents_vectors`
- Stores: embeddings + text chunks + metadata

```python
{
    "id": "uuid-based-chunk-id",
    "vector": [384-dim embedding],  # or 768-dim based on model
    "ticket_id": "INC0001234",
    "source_type": "incident",
    "short_description": "Server down",
    "description_chunk": "...",
    "category": "Incident",
    "state": "Resolved",
    "group": "IT Support",
    "source_name": "servicenow_incidents_...",
    "chunk_index": 0
}
```

### 4. GPU-Accelerated Embeddings (NEW)
**File**: `backend/services/embedding_worker_lancedb.py`

Features:
- **Automatic GPU detection** using CUDA/ROCm
- **Batch processing** for efficiency
- **Fallback support** (Ollama/OpenAI)
- **Local models** (no API calls required)

Supported Models:
- `nomic-embed-text` (384-dim, fast, local)
- `all-minilm-l6-v2` (384-dim, smaller)
- `bge-small-en-v1.5` (384-dim, multilingual)
- `bge-base-en-v1.5` (768-dim, better quality)

### 5. Search/RAG API
**File**: `backend/api/search.py` + `backend/rag/vectorstore.py`

Endpoints:
- `POST /api/search/semantic` — Vector similarity search
- `POST /api/search/answer` — Full RAG pipeline with LLM synthesis
- Supports hybrid search (vector + text)

---

## Installation & Setup

### Prerequisites
```bash
# GPU Support (choose one):
# For NVIDIA GPUs:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For AMD GPUs (ROCm):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.7

# For CPU only (slower):
pip install torch torchvision torchaudio
```

### Installation
```bash
cd Novastra-ITSM

# Install dependencies
pip install -r backend/requirements.txt

# Initialize LanceDB schema
python -c "from backend.services.lancedb_store import ensure_table; ensure_table(384)"
```

### Environment Configuration
```bash
# .env or system environment

# ── Vector Store ──────────────────────────
VECTOR_BACKEND=lancedb           # Use LanceDB instead of Qdrant
LANCEDB_PATH=./vectorstore/lancedb
LANCEDB_TABLE=incidents_vectors

# ── GPU/Embeddings ──────────────────────
GPU_ENABLED=true
EMBEDDING_MODEL=nomic-embed-text  # or all-minilm-l6-v2, bge-base-en-v1.5
EMBEDDING_DEVICE=cuda             # cuda, rocm, cpu
EMBEDDING_BATCH_SIZE=32           # Adjust based on GPU VRAM

# ── ServiceNow ──────────────────────────
SERVICENOW_BASE_URL=https://dev12345.service-now.com
SERVICENOW_USERNAME=your_username
SERVICENOW_PASSWORD=your_password

# ── PostgreSQL (Operational Data) ──────
POSTGRES_DSN=postgresql://user:pass@localhost:5432/ki_db
```

---

## Migration from Qdrant

If upgrading from Qdrant:

```bash
# 1. Backup existing Qdrant data
# (Already stored in PostgreSQL, safe to proceed)

# 2. Run migration script
python scripts/migrate_qdrant_to_lancedb.py --batch-size 100 --verbose

# 3. Verify migration
python scripts/migrate_qdrant_to_lancedb.py --verify-only

# 4. Update .env
# Change: VECTOR_BACKEND=qdrant → VECTOR_BACKEND=lancedb

# 5. Restart backend
# systemctl restart ki-backend
# or
# pkill -f "uvicorn.*main:app"
# uvicorn backend.main:app --reload
```

---

## Data Flow

### Ingestion Flow
```
1. ServiceNow API
   ↓
2. servicenow_sync.py::one_time_sync()
   ├─ Fetch incidents (batch)
   ├─ Persist to PostgreSQL (operational_ingestion.py)
   └─ Generate embeddings (embedding_worker_lancedb.py)
       ├─ Load local GPU model (nomic-embed-text, etc.)
       ├─ Chunk text
       ├─ Embed in batches
       └─ Upsert to LanceDB
```

### Search/Query Flow
```
1. User Query
   ↓
2. /api/search/answer
   ├─ Embed query (GPU model)
   ├─ Search LanceDB (vector similarity)
   ├─ Optional: Qdrant fallback (hybrid)
   ├─ Optional: PostgreSQL fallback (pgvector)
   └─ Rerank + synthesize with LLM
       ├─ Ollama (default, local)
       └─ OpenAI (optional, API)
```

---

## Performance Characteristics

### Embedding Generation (per incident)
| Model | Device | Speed | Quality | VRAM |
|-------|--------|-------|---------|------|
| nomic-embed-text | GPU (RTX 3090) | ~2s/100 chunks | High | 2GB |
| nomic-embed-text | CPU | ~30s/100 chunks | High | 1GB |
| all-minilm-l6-v2 | GPU | ~1s/100 chunks | Medium | 1.5GB |

### Search Latency (per query)
| Operation | Time | Notes |
|-----------|------|-------|
| Query embedding | 50-100ms | GPU |
| LanceDB search | 10-50ms | Local, depends on table size |
| Reranking | 200-500ms | Optional |
| LLM synthesis | 1-5s | Ollama/OpenAI |

### Storage
- PostgreSQL: ~1-2KB per incident
- LanceDB: ~1-2KB per chunk + embedding (384-dim @ 4bytes = 1.5KB)
- Estimate: ~100K incidents → ~500MB PostgreSQL + 2-5GB LanceDB

---

## Configuration Reference

### Core Settings
```python
# Vector Backend
VECTOR_BACKEND = "lancedb"  # | "qdrant" | "postgres" | "hybrid"

# LanceDB
LANCEDB_PATH = "./vectorstore/lancedb"
LANCEDB_TABLE = "incidents_vectors"
LANCEDB_METRIC = "cosine"  # | "euclidean" | "dot"

# GPU
GPU_ENABLED = True
EMBEDDING_DEVICE = "cuda"  # | "rocm" | "cpu"
EMBEDDING_MODEL = "nomic-embed-text"
EMBEDDING_BATCH_SIZE = 32

# Chunk Configuration
CHUNK_SIZE = 1500  # Max tokens per chunk
CHUNK_OVERLAP = 400  # Overlap for context preservation
TOP_K_RESULTS = 20  # Results before reranking
```

---

## Troubleshooting

### GPU Not Detected
```bash
# Check GPU
python -c "import torch; print(torch.cuda.is_available())"

# Fix: Reinstall PyTorch with correct CUDA version
# Find your CUDA version: nvidia-smi
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Out of Memory (CUDA)
```bash
# Solution 1: Reduce batch size
EMBEDDING_BATCH_SIZE=8

# Solution 2: Use smaller model
EMBEDDING_MODEL=all-minilm-l6-v2

# Solution 3: Use CPU
EMBEDDING_DEVICE=cpu
GPU_ENABLED=false
```

### LanceDB File Locked
```bash
# Remove lock file
rm -f ./vectorstore/lancedb/.lance_lock

# Or restart the application
```

### Slow Search
```bash
# 1. Check table size
python -c "from backend.services.lancedb_store import get_table_stats; import json; print(json.dumps(get_table_stats(), indent=2))"

# 2. Rebuild indices (if using LanceDB 0.5+)
# python -c "from backend.services.lancedb_store import rebuild_indices"

# 3. Consider vector quantization for very large datasets
```

---

## API Examples

### Semantic Search
```bash
curl -X POST http://localhost:8086/api/search/semantic \
  -H "Content-Type: application/json" \
  -d '{
    "query": "server down connection timeout",
    "top_k": 10
  }'
```

### RAG Q&A
```bash
curl -X POST http://localhost:8086/api/search/answer \
  -H "Content-Type: application/json" \
  -d '{
    "query": "how to restart the database",
    "llm_provider": "ollama"
  }'
```

---

## Monitoring & Debugging

### Enable Debug Logging
```bash
export LOGLEVEL=DEBUG
uvicorn backend.main:app --log-level debug
```

### Monitor LanceDB
```python
from backend.services.lancedb_store import get_table_stats
import json

stats = get_table_stats()
print(json.dumps(stats, indent=2))
```

### Profile Embedding Generation
```python
import time
from backend.services.embedding_worker_lancedb import index_incidents_to_lancedb

start = time.time()
indexed = index_incidents_to_lancedb(records, "profile_test")
elapsed = time.time() - start
print(f"Indexed {indexed} chunks in {elapsed:.1f}s ({indexed/elapsed:.1f} chunks/sec)")
```

---

## Future Enhancements

- [ ] Vector quantization for very large datasets
- [ ] Distributed LanceDB (cloud/cluster)
- [ ] Real-time incremental indexing
- [ ] Multi-modal embeddings (text + images)
- [ ] Semantic caching layer
- [ ] Dynamic model selection based on query complexity

---

## References

- [LanceDB Documentation](https://lancedb.com/docs/)
- [Sentence-Transformers](https://www.sbert.net/)
- [Nomic AI](https://www.nomic.ai/)
- [FastAPI](https://fastapi.tiangolo.com/)
