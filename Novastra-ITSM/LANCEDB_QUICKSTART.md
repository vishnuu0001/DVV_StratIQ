# LanceDB Setup Quick Start

## Architecture Upgrade Summary

Novastra-ITSM has been upgraded to use **LanceDB** (local GPU-accelerated vector store) instead of requiring external Qdrant or relying only on PostgreSQL pgvector.

### Benefits
- ✅ GPU acceleration for embeddings (2-10x faster than CPU)
- ✅ No external vector database required
- ✅ Lower latency searches (local storage)
- ✅ Reduced operational complexity
- ✅ Backward compatible with PostgreSQL operational data

---

## Step-by-Step Setup

### 1. Prerequisites

#### GPU Support (Choose ONE)

**NVIDIA GPU (Recommended for most setups):**
```bash
# Check CUDA version
nvidia-smi

# Install PyTorch with CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# OR for CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**AMD GPU (ROCm):**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.7
```

**CPU Only (No GPU):**
```bash
pip install torch torchvision torchaudio
# Note: CPU embeddings are ~10x slower, not recommended for production
```

### 2. Install Dependencies

```bash
cd Novastra-ITSM

# Install backend requirements (includes LanceDB, sentence-transformers)
pip install -r backend/requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and update key settings:

```bash
cp .env.example .env

# Edit .env with your settings:
nano .env  # or use your editor
```

**Critical settings for LanceDB:**
```bash
# Vector store backend (changed to lancedb)
VECTOR_BACKEND=lancedb

# LanceDB paths
LANCEDB_PATH=./vectorstore/lancedb
LANCEDB_TABLE=incidents_vectors

# GPU settings
GPU_ENABLED=true
EMBEDDING_DEVICE=cuda  # or rocm, cpu
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_BATCH_SIZE=32

# ServiceNow (update with your instance)
SERVICENOW_BASE_URL=https://your-instance.service-now.com
SERVICENOW_USERNAME=your_username
SERVICENOW_PASSWORD=your_password

# PostgreSQL (for operational data)
POSTGRES_DSN=postgresql://user:pass@localhost:5432/ki_db
```

### 4. Initialize LanceDB

```bash
# Create LanceDB directory structure
python -c "from backend.services.lancedb_store import ensure_table; ensure_table(384)"
```

### 5. Verify GPU Detection

```bash
# Check if GPU is detected
python -c "import torch; print(f'GPU Available: {torch.cuda.is_available()}'); print(f'Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU\"}')"

# Check embedding model
python -c "from sentence_transformers import SentenceTransformer; m = SentenceTransformer('nomic-embed-text'); print(f'Model loaded on device: {m.device}')"
```

### 6. Start Backend

```bash
# With auto-reload (development)
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8086

# OR without auto-reload (production)
uvicorn backend.main:app --host 0.0.0.0 --port 8086 --workers 4
```

### 7. Ingest ServiceNow Data

Via API:
```bash
curl -X POST http://localhost:8086/api/servicenow/sync \
  -H "Content-Type: application/json" \
  -d '{
    "base_url": "https://your-instance.service-now.com",
    "username": "your_username",
    "password": "your_password",
    "query": "active=true",
    "limit": 100
  }'
```

Via Python:
```python
import asyncio
from backend.services.servicenow_sync import one_time_sync

result = asyncio.run(one_time_sync(
    base_url="https://your-instance.service-now.com",
    username="your_username",
    password="your_password",
    query="active=true",
    limit=100
))
print(result)
```

### 8. Test Search

```bash
curl -X POST http://localhost:8086/api/search/semantic \
  -H "Content-Type: application/json" \
  -d '{
    "query": "server down connection timeout",
    "top_k": 5
  }'
```

---

## Embedding Model Selection

Choose based on your needs:

| Model | Dim | Speed | Quality | Use Case |
|-------|-----|-------|---------|----------|
| `nomic-embed-text` | 384 | Fast | High | **Recommended (general purpose)** |
| `all-minilm-l6-v2` | 384 | Very Fast | Medium | Resource-constrained |
| `bge-small-en-v1.5` | 384 | Fast | High | Semantic search (open-source) |
| `bge-base-en-v1.5` | 768 | Medium | Very High | High-quality search |

Update in `.env`:
```bash
EMBEDDING_MODEL=nomic-embed-text  # or bge-base-en-v1.5, etc.
```

---

## Performance Tuning

### For RTX 3090 / 4090 (High VRAM):
```bash
EMBEDDING_BATCH_SIZE=64
OLLAMA_NUM_GPU=1
```

### For RTX 3080 / 4080 (12GB VRAM):
```bash
EMBEDDING_BATCH_SIZE=32
OLLAMA_NUM_GPU=1
```

### For RTX 3070 / 4070 (8GB VRAM):
```bash
EMBEDDING_BATCH_SIZE=16
OLLAMA_NUM_GPU=1
```

### For RTX 3060 / CPU:
```bash
EMBEDDING_BATCH_SIZE=8
GPU_ENABLED=false  # Use CPU
EMBEDDING_DEVICE=cpu
```

---

## Troubleshooting

### GPU Not Detected

**Symptom:** `torch.cuda.is_available() → False`

**Fix:**
```bash
# 1. Check GPU is detected by system
nvidia-smi

# 2. Verify CUDA version matches PyTorch installation
nvidia-smi | grep CUDA

# 3. Reinstall PyTorch with correct CUDA version
pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Out of Memory (OOM)

**Symptom:** `CUDA out of memory. Tried to allocate X MB`

**Fix:**
```bash
# Solution 1: Reduce batch size
EMBEDDING_BATCH_SIZE=8

# Solution 2: Use smaller model
EMBEDDING_MODEL=all-minilm-l6-v2

# Solution 3: Switch to CPU (slower)
GPU_ENABLED=false
EMBEDDING_DEVICE=cpu
```

### Slow Embedding Generation

**Symptom:** Embedding 100 chunks takes > 30 seconds

**Possible causes:**
- CPU is being used instead of GPU
- Batch size is too small
- Model is still loading (check logs)

**Debug:**
```bash
# Monitor GPU usage
watch -n 1 nvidia-smi

# Check logs
grep -i "cuda\|gpu\|device" backend.log

# Profile embedding
python -c "
import time
from backend.services.embedding_worker_lancedb import index_incidents_to_lancedb

records = [{'number': f'INC{i}', 'short_description': 'test', 'description': 'test content'} for i in range(10)]
start = time.time()
indexed = index_incidents_to_lancedb(records, 'test')
elapsed = time.time() - start
print(f'{indexed} chunks in {elapsed:.1f}s = {indexed/elapsed:.1f} chunks/sec')
"
```

### LanceDB Connection Issues

**Symptom:** `LanceDB backend is disabled by configuration`

**Fix:**
```bash
# Check environment variables
echo $VECTOR_BACKEND  # Should be 'lancedb'
echo $LANCEDB_PATH    # Should be './vectorstore/lancedb' (not empty)

# Ensure directory is created
mkdir -p ./vectorstore/lancedb

# Verify in .env
VECTOR_BACKEND=lancedb
LANCEDB_PATH=./vectorstore/lancedb
```

---

## Migration from Qdrant

If upgrading from existing Qdrant setup:

```bash
# 1. Backup Qdrant data (if needed)
# Qdrant data is already accessible via migration script

# 2. Run migration
python scripts/migrate_qdrant_to_lancedb.py --verbose

# 3. Verify
python scripts/migrate_qdrant_to_lancedb.py --verify-only

# 4. Update .env
VECTOR_BACKEND=lancedb

# 5. Restart backend
```

---

## Monitoring

### Check LanceDB Status

```python
from backend.services.lancedb_store import get_table_stats
import json

stats = get_table_stats()
print(json.dumps(stats, indent=2))
# Output: {
#   "table_name": "incidents_vectors",
#   "row_count": 5432,
#   "schema": "...",
#   "status": "ready"
# }
```

### Check Embedding Model

```python
from backend.services.embedding_worker_lancedb import _get_embeddings
model = _get_embeddings()
print(f"Model type: {type(model)}")
print(f"Model device: {model.device if hasattr(model, 'device') else 'N/A'}")
```

### Monitor in Docker (optional)

```bash
# Check GPU usage during ingestion
docker stats  # Overall container stats

# Inside container
watch -n 1 nvidia-smi  # GPU usage
htop  # CPU/memory usage
```

---

## Next Steps

1. ✅ Test search with `/api/search/semantic`
2. ✅ Test Q&A with `/api/search/answer`
3. ✅ Set up scheduled ingestion (cron/API)
4. ✅ Configure monitoring alerts
5. ✅ Tune batch size based on actual performance
6. ✅ Plan for scaling (if needed)

---

## Support & Debugging

Enable debug logging:
```bash
export LOGLEVEL=DEBUG
uvicorn backend.main:app --log-level debug 2>&1 | tee debug.log
```

Check logs for "LanceDB" or "GPU":
```bash
grep -i "lancedb\|gpu\|embedding" debug.log
```

---

**For detailed documentation, see [ARCHITECTURE_UPGRADE.md](./ARCHITECTURE_UPGRADE.md)**
