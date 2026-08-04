# Strat-IQ Azure Reverse Proxy

## Overview

This Node.js application provides a reverse proxy for the Strat-IQ Azure Service located at `https://strat-iq.azurewebsites.net/`.

The proxy runs locally on **http://localhost:8097/** and:
- ✅ Forwards all requests to the Azure backend when it's available
- ⚠️ Shows a status page when the Azure service is unavailable (HTTP 403 or network errors)
- 📊 Logs all request activity to console
- 🔄 Automatically detects Azure service status on each request

## Architecture

```
Local Client
    ↓
http://localhost:8097/  (Proxy Server)
    ↓
[Status Check] ← Test Azure Connectivity
    ↓
Azure Backend (if available)
    ├─ Forward request → https://strat-iq.azurewebsites.net/
    └─ Return response
    OR
Status Page (if unavailable)
    └─ Show service status information
```

## Setup

### Prerequisites
- Node.js v14+ ([Download](https://nodejs.org/))
- npm (comes with Node.js)

### Installation

1. Navigate to the proxy directory:
   ```bash
   cd LaunchModules/azure-proxy-root
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

### Starting the Proxy

**Windows:**
```batch
start-proxy.bat
```

**macOS/Linux:**
```bash
bash start-proxy.sh
```

**Manual (any platform):**
```bash
node proxy-server.js
```

### Expected Output

```
╔════════════════════════════════════════════════════╗
║    Strat-IQ Azure Reverse Proxy Server             ║
╚════════════════════════════════════════════════════╝

Proxy Server started:
  Local Address:  http://localhost:8097/
  Azure Backend:  https://strat-iq.azurewebsites.net/
  
All requests to localhost:8097 will be forwarded to:
  https://strat-iq.azurewebsites.net/

Status:
  - Testing Azure connectivity on each request
  - Falls back to status page if Azure is unavailable
  - Logs all activity to console

Ctrl+C to stop the server
```

## Usage

### Access the Proxy

```
http://localhost:8097/
http://localhost:8097/api/endpoint
http://localhost:8097/any/path
```

### What Happens

**When Azure is Available (HTTP 200-399):**
- Request is forwarded to Azure
- Azure response is returned as-is
- Request is logged: `[PROXY] Forwarding to Azure (status: 200)`

**When Azure is Unavailable (HTTP 403/404/5xx or Network Error):**
- Status page is shown instead (HTTP 503)
- User-friendly message explains the situation
- Request is logged: `[PROXY] Azure unreachable, showing status page`

## Status Page

When Azure is unavailable, users see a professional status page that includes:
- Current proxy status
- Backend service address
- Local proxy address
- Troubleshooting guidance
- Current timestamp

## Configuration

Edit `proxy-server.js` to modify:

```javascript
const AZURE_HOST = 'strat-iq.azurewebsites.net';  // Azure service hostname
const LISTEN_PORT = 8097;                          // Local port for proxy
```

## Troubleshooting

### Port Already in Use
If you see `EADDRINUSE` error:

**Windows (PowerShell):**
```powershell
Get-Process | Where-Object { $_.Name -eq "node" } | Stop-Process
```

**Find the process using the port:**
```bash
netstat -ano | findstr :8097
```

### Azure Service Returns 403
This is expected when the Azure App Service is disabled or the user lacks permissions. The proxy will:
1. Detect the 403 status
2. Show the status page
3. Log the error for debugging

### Proxy Not Responding
Check that:
1. Node.js is installed: `node --version`
2. Dependencies are installed: `npm list`
3. No firewall is blocking port 8097
4. No other application is using the port

## Performance

- Response time: ~100-500ms (depending on Azure)
- Memory usage: ~30-50 MB
- Handles concurrent requests
- Automatic timeout: 10 seconds per request

## Security Considerations

⚠️ **This is a development proxy only.** For production use:
1. Add authentication/authorization
2. Implement rate limiting
3. Add request validation
4. Use HTTPS
5. Restrict allowed paths
6. Add CORS headers if needed

## Logs

All requests are logged to console with timestamps:

```
2026-08-04T09:21:51.934Z - GET /
[PROXY] Forwarding to Azure (status: 200)

2026-08-04T09:21:52.156Z - GET /api/data
[PROXY] Azure unreachable, showing status page
```

## Stopping the Proxy

Press `Ctrl+C` in the terminal window where the proxy is running.

## Files

- `proxy-server.js` - Main proxy application
- `package.json` - Node.js dependencies
- `node_modules/` - Installed packages
- `start-proxy.bat` - Windows startup script
- `start-proxy.sh` - Linux/macOS startup script
- `PROXY_README.md` - This file

## Support

For issues, check:
1. Azure App Service status in Azure Portal
2. Browser console for network errors
3. Proxy console output for detailed logs
4. Firewall/antivirus settings

## Version

- Node.js Proxy v1.0.0
- Built for Strat-IQ Azure Service
- Last updated: 2026-08-04
