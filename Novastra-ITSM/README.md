# Novastra-ITSM — AI Support Agent

A **RAG-powered AI Support Agent** that helps IT support teams resolve incidents faster by retrieving grounded answers from a knowledge repository. Built with **FastAPI + PostgreSQL pgvector + LangChain**, supporting **Ollama (open-source)** and **OpenAI** as pluggable LLM backends.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend (Vite)                   │
│  ┌──────────┐ ┌──────────────┐ ┌────────┐ ┌────────────┐  │
│  │ Chat     │ │ ServiceNow   │ │ Admin  │ │ Settings   │  │
│  │ (RAG Q&A)│ │ Integration  │ │ Panel  │ │ (LLM pick) │  │
│  └──────────┘ └──────────────┘ └────────┘ └────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ REST / multipart
┌────────────────────────▼────────────────────────────────────┐
│                    FastAPI Backend                          │
│  /api/agent    → RAG query with anti-hallucination guard   │
│  /api/servicenow → Live fetch / manual / screenshot (OCR) │
│  /api/admin    → Upload, index, delete knowledge docs      │
│  /api/feedback → Thumbs up/down ratings                    │
│  /api/settings → Runtime LLM provider switching           │
└──────────┬──────────────────────────┬───────────────────────┘
           │                          │
┌──────────▼──────┐        ┌──────────▼──────────────────────┐
│ PostgreSQL+pgvector │    │   LLM Router                    │
│  (vector store) │        │   Ollama  ←── default           │
│  + embeddings   │        │   OpenAI  ←── optional (API key)│
└─────────────────┘        └─────────────────────────────────┘
```

---

## Features

| Feature | Details |
|---|---|
| **RAG Q&A** | Grounded answers with source citations and confidence scores |
| **Anti-hallucination** | Relevance score gate · strict context-only system prompt · explicit "I don't know" when no match |
| **ServiceNow** | Live ticket fetch (REST API) · manual entry · screenshot OCR |
| **Admin Panel** | Upload/delete documents · index / re-index · collection stats |
| **Dual LLM** | Ollama (any local model) + OpenAI — switchable at runtime |
| **Feedback** | Thumbs up/down per answer · statistics dashboard · ranking |
| **Document types** | .docx · .xlsx · .csv · .txt · .pdf · .md · .png / .jpg (OCR) |

---

## Quick Start (Local Dev)

### Prerequisites
- Python 3.10+
- Node.js 18+
- [Ollama](https://ollama.ai) installed and running

### 1 — Pull an Ollama model
```bash
ollama pull mistral           # chat model
ollama pull nomic-embed-text  # embedding model
```

### 2 — Set up the backend
```bash
# Windows PowerShell
cd e:\techmaapprationalization\Novastra-ITSM

# Create .env
Copy-Item .env.example .env   # then edit .env as needed

# Install dependencies
pip install -r backend/requirements.txt

# Index the data folder
python setup.py

# Start API
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 3 — Start the frontend
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

### Or use the PowerShell helpers
```powershell
# Terminal 1
.\start_backend.ps1

# Terminal 2
.\start_frontend.ps1
```

---

## Docker (full stack)

```bash
cp .env.example .env        # edit settings
docker-compose up --build

# Pull models into the Ollama container
docker exec -it kgdemo-ollama ollama pull mistral
docker exec -it kgdemo-ollama ollama pull nomic-embed-text
```
- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs

---

## Configuration (`.env`)

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `ollama` | `ollama` or `openai` |
| `OLLAMA_MODEL` | `mistral` | Any model pulled in Ollama |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Embedding model |
| `OPENAI_API_KEY` | *(blank)* | Set to enable OpenAI |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model name |
| `MIN_RELEVANCE_SCORE` | `0.35` | Anti-hallucination gate (0–1) |
| `CHUNK_SIZE` | `800` | RAG chunk size (tokens) |
| `ADMIN_SECRET` | `admin_change_me_in_prod` | Admin panel password |
| `SERVICENOW_BASE_URL` | *(blank)* | SN instance URL |
| `SERVICENOW_USERNAME` | *(blank)* | SN credentials |
| `SERVICENOW__PASSWORD` | *(blank)* | SN credentials |

---

## API Reference

Full interactive docs at **http://localhost:8000/docs**

| Endpoint | Method | Description |
|---|---|---|
| `/api/agent/query` | POST | RAG-grounded support query |
| `/api/servicenow/fetch-and-resolve` | POST | Live SN ticket resolution |
| `/api/servicenow/manual-resolve` | POST | Manual ticket entry |
| `/api/servicenow/screenshot-resolve` | POST | Screenshot OCR + resolve |
| `/api/admin/index` | POST | Index / re-index data folder |
| `/api/admin/upload` | POST | Upload a new document |
| `/api/admin/documents` | GET | List indexed documents |
| `/api/admin/document` | DELETE | Remove a document |
| `/api/admin/stats` | GET | Vector collection stats |
| `/api/feedback` | POST | Submit thumbs up/down |
| `/api/feedback/stats` | GET | Aggregated feedback stats |
| `/api/settings` | GET/POST | Get / update LLM settings |
| `/health` | GET | Service health check |

---

## Anti-Hallucination Design

1. **Relevance gate** — chunks below `MIN_RELEVANCE_SCORE` are discarded
2. **Context-only prompt** — LLM is instructed to answer _only_ from provided context
3. **Explicit fallback** — returns a fixed "not enough information" message when no chunks pass the gate
4. **Source attribution** — every answer includes the source document(s) and relevance scores
5. **Temperature = 0** — deterministic output, no creative drift

---

## Project Structure

```
Novastra-ITSM/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── config.py            # All settings
│   ├── api/
│   │   ├── agent.py         # RAG query endpoint
│   │   ├── admin.py         # Knowledge management
│   │   ├── servicenow.py    # SN integration
│   │   ├── feedback.py      # Ratings API
│   │   └── settings.py      # LLM config API
│   ├── rag/
│   │   ├── pipeline.py      # RAG + anti-hallucination
│   │   ├── vectorstore.py   # PostgreSQL pgvector operations
│   │   └── document_loader.py  # DOCX/XLSX/PDF/OCR
│   ├── llm/
│   │   └── router.py        # Ollama / OpenAI switcher
│   └── models/
│       └── schemas.py       # Pydantic models
├── frontend/
│   └── src/
│       ├── pages/           # Chat, SN, Admin, Feedback, Settings
│       ├── components/      # SourceBadges, ConfidenceBadge
│       └── services/api.js  # Axios API client
├── data/                    # Knowledge documents (your incidents)
├── postgres/                # PostgreSQL persistence
├── docker-compose.yml
├── setup.py                 # One-time setup + indexing
└── .env.example
```
# 1. Pull Ollama models
ollama pull mistral ; ollama pull nomic-embed-text

# 2. Setup backend + index the data/ folder
cd e:\techmaapprationalization\Novastra-ITSM
pip install -r backend/requirements.txt
python setup.py          # creates .env, indexes all docs

# 3. Run backend  (terminal 1)
.\start_backend.ps1      # http://localhost:8000/docs

# 4. Run frontend (terminal 2)
.\start_frontend.ps1     # http://localhost:5173