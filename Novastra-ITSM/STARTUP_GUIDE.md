# Novastra-ITSM Backend & Frontend Setup Guide

## ⚠️ Current Issue: Port Mismatch

Your frontend is trying to connect to `:5000` (AppRationalization backend), but the Novastra-ITSM backend runs on `:8086`.

### Port Allocation

| Service | Port | Status | Purpose |
|---------|------|--------|---------|
| Novastra-ITSM Backend | 8086 | Running ✓ | FastAPI with LanceDB/Ollama |
| Novastra-ITSM Frontend (built) | 8086 | Served from backend | React SPA |
| Novastra-ITSM Frontend (dev) | 5177 | Development server | Vite dev server with proxy |
| AppRationalization Backend | 5000 | Running ✓ | Flask (separate project) |

## Recommended Setup Options

### Option A: Development Mode (Recommended for debugging)
Run the frontend dev server and backend separately:

```bash
# Terminal 1: Start Novastra-ITSM backend
cd Novastra-ITSM\backend
python -m uvicorn main:app --host 0.0.0.0 --port 8086 --reload

# Terminal 2: Start Novastra-ITSM frontend dev server
cd Novastra-ITSM\frontend
npm install
npm run dev

# Frontend will be available at: http://localhost:5177
# API requests automatically proxy to: http://localhost:8086
```

**Benefits:**
- Hot-reload on code changes
- Better debugging with source maps
- Proxy configuration in vite.config.js handles routing

**Vite Proxy Configuration** (already configured):
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8086',
    changeOrigin: true,
  }
}
```

### Option B: Production Mode
Build frontend and serve both from the same backend:

```bash
# Build frontend
cd Novastra-ITSM\frontend
npm install
npm run build

# Start backend (it automatically serves the built frontend from /)
cd Novastra-ITSM\backend
python -m uvicorn main:app --host 0.0.0.0 --port 8086

# Access at: http://localhost:8086
```

**Benefits:**
- Single service to manage
- Optimal performance
- Frontend bundled with backend

## Recent Fixes Applied

### 1. ✓ Installed psycopg-pool
- **Issue**: "PostgreSQL pool unavailable, using direct connections"
- **Fix**: Installed `psycopg-pool>=3.1.0`
- **Effect**: PostgreSQL connection pooling now works efficiently

### 2. ✓ Added OAuth Providers Endpoint
- **Issue**: Frontend expected `/api/auth/oauth/providers` endpoint
- **Fix**: Added endpoint that returns available OAuth providers
- **Response**:
```json
{
  "providers": [
    {"id": "github", "name": "GitHub", "enabled": true|false, "icon": "github"},
    {"id": "google", "name": "Google", "enabled": true|false, "icon": "google"}
  ]
}
```

### 3. ✓ Updated requirements.txt
- Added `psycopg-pool>=3.1.0` for optimal PostgreSQL pooling

## Testing Authentication

### Login Endpoint
```bash
curl -X POST http://localhost:8086/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Response:
# {
#   "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "token_type": "bearer",
#   "user": {...}
# }
```

### OAuth Providers
```bash
curl http://localhost:8086/api/auth/oauth/providers

# Response:
# {
#   "providers": [
#     {"id": "github", "name": "GitHub", "enabled": false, ...},
#     {"id": "google", "name": "Google", "enabled": false, ...}
#   ]
# }
```

### Verify Backend Health
```bash
curl http://localhost:8086/health
```

## Environment Variables

### Backend (.env in Novastra-ITSM/backend/)

Essential OAuth config:
```
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_secret
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_secret

APP_BASE_URL=http://localhost:8086
JWT_SECRET=your-secret-key-change-this

# LanceDB + GPU settings
VECTOR_BACKEND=lancedb
GPU_ENABLED=true
EMBEDDING_MODEL=nomic-embed-text

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

### Frontend (.env in Novastra-ITSM/frontend/)

Portal integration:
```
VITE_PORTAL_HOME_URL=http://localhost:3000/launch-modules
VITE_PORTAL_LOGIN_URL=http://localhost:3000/login
```

(Note: API URL is NOT hardcoded - it uses relative URLs that proxy through vite or backend)

## Troubleshooting

### Issue: `ERR_CONNECTION_REFUSED` on port 5000

**Cause**: Frontend is hitting wrong port

**Solutions**:
1. **Dev Mode**: Use `npm run dev` - it proxies to 8086
2. **Production Mode**: Rebuild with `npm run build` and serve from 8086
3. **Clear browser cache**: Ctrl+Shift+Delete (Chrome)

### Issue: 500 Error on `/api/auth/login`

**Cause**: PostgreSQL connection issues (now fixed with psycopg-pool)

**Solution**: Already fixed! psycopg-pool installed.

### Issue: Frontend takes 60+ seconds to respond

**Cause**: 
- Ollama LLM cold-start
- First-time vectorstore load
- GPU initialization

**Solution**: Normal behavior. First request warms up Ollama. Subsequent requests are fast.

## Architecture Changes (Recent)

Your backend was recently upgraded from Qdrant to LanceDB with GPU acceleration:

- **Vector Store**: LanceDB (local, GPU-accelerated, file-based)
- **Embeddings**: sentence-transformers (GPU support with CPU fallback)
- **Data Flow**: ServiceNow → PostgreSQL → LanceDB (automatic)
- **Schema**: incident_id, embedding (384-dim), text_chunk, metadata
- **Backward Compatibility**: Old Qdrant data still accessible

See [ARCHITECTURE_UPGRADE.md](../../ARCHITECTURE_UPGRADE.md) for details.

## Next Steps

1. **Choose deployment mode** (Dev or Production)
2. **Verify backend runs on 8086**: `curl http://localhost:8086/health`
3. **Test authentication**: See "Testing Authentication" section above
4. **Check frontend connectivity**: Browser console should show successful API calls

## Support

For issues, check logs:
- Backend: `Novastra-ITSM/backend/backend.log`
- Vectorstore: Look for "LanceDB" messages in startup log
- LLM: Look for "Ollama runtime" messages
