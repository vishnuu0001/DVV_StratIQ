# StratIQ — Azure App Service Mapping Deployment Guide

**Purpose:** Map `https://strat-iq.azurewebsites.net/` to the StratIQ platform running on the Azure VM `StratDev`, keeping Ollama on the VM's local GPU.
**Last Updated:** July 2026
**Status:** ✅ **WORKING** — verified end-to-end, including live Ollama data flowing through the full chain.
**VM:** `StratDev` (resource group `mxc`, West US, GPU size `Standard_NV12ads_A10_v5`, private IP `10.0.0.4`, static public IP `104.45.218.69`)

---

## Final Architecture (verified working)

```
Internet
    │  HTTPS
    ▼
strat-iq.azurewebsites.net   ← Azure App Service (resource group "mxc", East US 2, Linux/Python 3.14)
    │
    │  FastAPI reverse-proxy app (main.py) — forwards every request
    │  to the VM's public IP on port 8090, preserving method/headers/body,
    │  streaming the response back
    ▼
http://104.45.218.69:8090   ← VM's public IP, NSG rule scoped to App Service's outbound IPs only
    │
    ▼
IIS on the VM — site "StratIQ", bound to *:8090:, *:8090:strat-iq.azurewebsites.net, and *:80:localhost
    │  physical root: D:\StartIQ\AppRationalization\frontend\build
    │  web.config URL Rewrite rules proxy /api/<module>/* to each backend
    ├── /scm/            → supply-chain-disruption-manager\apps\web-ui\dist
    ├── /novastra-itsm/             → Novastra-ITSM\frontend\dist
    ├── (10 other module virtual apps — see Port Map below)
    │
    ├── /api/kg/*        → localhost:8001 (SCM kg-service)
    ├── /api/inspector/* → localhost:8003 (SCM signal-inspector)
    ├── /api/agents/*    → localhost:8002 (SCM agent-service)
    ├── /api/novastra-itsm/*        → localhost:8086 (Novastra-ITSM)
    ├── ... (other module API proxy rules)
    │
    └── backends call → Ollama (http://localhost:11434, model llama3.1:8b)
```

**Why port 8090 and not port 80:** the VM's public IP hits an unexplained Windows HTTP.sys-level `403 Forbidden` (`Server: Microsoft-HTTPAPI/2.0`) specifically on port 80, even with a correct `Host: localhost` header, no IIS IP restrictions, and Windows Firewall confirmed not blocking it (tested by briefly disabling the Public firewall profile — still failed). The exact same site is also bound to port 8090 with **no host-header restriction at all**, which sidesteps whatever HTTP.sys quirk exists on port 80. If you ever want to revisit port 80, that's an unresolved side-mystery, not a blocker — 8090 works cleanly and is what's actually deployed.

---

## Why this replaced the Hybrid Connection approach

This session first attempted **Azure Relay Hybrid Connections** (a valid pattern for genuinely on-premises machines), assuming there was no Azure VM involved. That attempt hit a persistent, unexplained `unauthorized operation` error from Azure Relay that survived fresh resources, fresh keys, fresh namespaces, both old and current SDK versions, and extensive tenant-permission auditing (documented in a separate diagnostic runbook produced during troubleshooting).

It turned out **this machine is itself an Azure VM** (`StratDev`, resource group `mxc`) — confirmed via its own Instance Metadata Service (`curl -H "Metadata:true" http://169.254.169.254/metadata/instance?api-version=2021-02-01`). That makes Hybrid Connections unnecessary entirely: an App-Service-to-VM connection over the VM's public IP (with NSG scoped to only the App Service's outbound IPs) is simpler, avoids the mystery Relay auth failure, and is what's actually deployed today.

The VM (West US) and the App Service (East US 2) are in different Azure regions, which also ruled out same-region VNet Integration as an option — the public-IP + scoped-NSG approach was chosen deliberately over cross-region VNet peering for simplicity.

---

## The Reverse-Proxy App

**Location:** `C:\StratIQ\AppServiceProxy\` (source of truth on this VM; deployed via `az webapp deploy` zip)

```python
# main.py — thin FastAPI reverse proxy
VM_TARGET = "http://104.45.218.69:8090"
# forwards every method/path/header/body to VM_TARGET, streams response back unchanged
```

**Deployment gotcha:** `az webapp deploy --type zip` does **not** run build automation (pip install) by default on Linux App Service. The app setting `SCM_DO_BUILD_DURING_DEPLOYMENT=true` must be set first, or the deployment "succeeds" but the site fails to start (missing `fastapi`/`uvicorn`/`httpx`).

```bash
az webapp config appsettings set -g mxc -n strat-iq --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true
az webapp config set -g mxc -n strat-iq --startup-file "python -m uvicorn main:app --host 0.0.0.0 --port 8000"
az webapp deploy -g mxc -n strat-iq --src-path proxy.zip --type zip
```

**Diagnosing it, if it ever breaks again:**
```bash
az webapp log config -g mxc -n strat-iq --application-logging filesystem --docker-container-logging filesystem --level information
az webapp log download -g mxc -n strat-iq --log-file applogs.zip
# extract, check LogFiles/<date>_<instance>_containerStream.log for uvicorn's own request log lines
```
(Kudu's SCM basic-auth debug console is disabled on this App Service — `az webapp log download` is the reliable path, not `az webapp log tail` or the Kudu REST API.)

---

## Host-Header Bug: "Open Dashboard" redirected to `localhost` (fixed)

**Symptom:** From `https://strat-iq.azurewebsites.net`, clicking any module launch button (e.g. "Open Dashboard") navigated to `http://localhost/dash/...` and 404'd. Reproduced in a fresh incognito window, so not a caching issue.

**Root cause:** IIS's own automatic trailing-slash redirect (`/dash` → `/dash/`) builds an **absolute** `Location` header from the request's `Host` header. The proxy (`main.py`) was overriding every forwarded request's `Host` header to `"localhost"` — done originally so the request would match the VM's `*:8090:` binding — so IIS always generated `Location: http://localhost/dash/` regardless of what hostname the remote browser actually used. The user's own clarifying question ("I am trying from strat-iq.azurewebsites.net, then why is it opening localhost") pointed straight at the proxy's own Host-header rewrite as the culprit.

**Fix (two parts, both required):**
1. Added a matching IIS binding so the VM's IIS recognizes the public hostname:
   ```powershell
   New-WebBinding -Name "StratIQ" -Protocol http -Port 8090 -HostHeader "strat-iq.azurewebsites.net"
   ```
2. Changed the proxy's `VM_HOST_HEADER` (in `main.py`) from `"localhost"` to `"strat-iq.azurewebsites.net"`, so the Host header the VM's IIS sees — and therefore the Host it uses to build redirect URLs — matches the real public domain.
3. Also rewrite the scheme on any `Location` header pointing back at `VM_HOST_HEADER`: the VM is only reached over plain HTTP (`http://104.45.218.69:8090`), so IIS's redirect comes back as `http://strat-iq.azurewebsites.net/...`. Left unrewritten, the browser gets bounced to `http`, and only Azure's own HTTPS-only enforcement silently upgrades it back — an extra unnecessary round trip that would break if that enforcement were ever disabled. The proxy now rewrites `http://{VM_HOST_HEADER}` → `https://{VM_HOST_HEADER}` in any `Location` response header before relaying it.

Verified: `curl -svL https://strat-iq.azurewebsites.net/dash` now shows a single `301 → https://strat-iq.azurewebsites.net/dash/ → 200`, and all other module launch paths (`/ca`, `/infra`, `/ki`, `/mod`, `/ssdlc`, `/ot`, `/reman`, `/vl`, `/scm`, `/lab`) redirect the same way.

**If this pattern shows up again** (any new module, or a rewritten proxy): any reverse proxy sitting in front of IIS must either (a) forward the *real* public Host header end-to-end and have a matching IIS binding for it, or (b) explicitly rewrite absolute `Location`/redirect URLs on the way back out. Silently rewriting the Host header without doing one of these will always leak whatever hostname the proxy used internally into user-facing redirects.

---

## Follow-on bugs found while verifying the Host-header fix (all fixed)

Once the Host-header bug above was fixed, "Open Dashboard" stopped redirecting to `localhost` but surfaced three more, unrelated bugs — each only visible once the first layer was working:

**1. `web.config` rule collision routed `/api/dashboard/*` to the wrong backend (401 on every Dashboard API call)**

`D:\StartIQ\web.config` (and its synced copies in `AppRationalization\frontend\public\` and `build\`) had two rules that both match `/api/dashboard/*`:
- `Portal API Proxy`: `^api/(upload|analysis|dashboard|correlation|capabilities|visualization|reset)(.*)` → `localhost:5000` (Flask/AppRationalization)
- `Dashboard API Proxy`: `^api/dashboard/(.*)` → `localhost:8087` (the standalone Dashboard module)

`Portal API Proxy` appeared first with `stopProcessing="true"`, so *every* `/api/dashboard/...` request — including the standalone Dashboard module's `/status`, `/config`, `/critical-alerts`, `/connect` — was being rewritten to Flask (port 5000) instead of the Dashboard backend (port 8087). Flask correctly rejected these as unauthenticated (`{"error":"Authentication required"}`, 401), since the Dashboard module's frontend never sends the portal's Bearer token.

This collision exists because Flask's own `visualization_bp.py` separately registers a single bare endpoint at exactly `/api/dashboard` (no sub-path) for App Rationalization's own portfolio-dashboard feature — an unrelated, same-named endpoint that predates the standalone Dashboard module.

**Fix:** reordered the rules so `Dashboard API Proxy` (specific, requires a trailing `/`) is checked *before* `Portal API Proxy` (general). This routes all `/api/dashboard/<subpath>` calls to port 8087 while leaving Flask's bare `/api/dashboard` (no trailing slash — never matches the more specific rule) untouched. Applied to all three synced copies of `web.config`.

**2. Dashboard backend (port 8087) wasn't running at all (502 after the routing fix)**

There is no `StratIQ-Master-Watchdog` scheduled task currently registered on this VM (contradicts what CLAUDE.md documents) — only `StratIQ-Daily-GPU-Cache-Reset` and `StratIQ-ServiceRestart` exist. Nothing was auto-starting or restarting the Dashboard backend, so it simply wasn't up.

**Fix (immediate):** started it manually — `python -m uvicorn main:app --host 0.0.0.0 --port 8087` from `Dashboard\backend`, with `AUTH_TOKEN_SECRET` and `CORS_ORIGINS` set, logging to `D:\StartIQ\logs\Dashboard_std{out,err}.log`.

**Bigger latent issue found:** `D:\StartIQ\watchdog_all_backends.ps1` (the actual watchdog script all this tooling depends on) hardcoded `$Root = 'C:\STIQ\StratIQ_VM_AWS'` — a stale path from before this repo moved to `D:\StartIQ`. Fixed this (now `$Root = 'D:\StartIQ'`, `$LogDir = 'D:\StartIQ\logs'`), but **the `StratIQ-Master-Watchdog` scheduled task itself still needs to be (re-)registered** for backends to auto-start at logon / auto-restart on crash — this has not been done yet, pending a decision on whether to enable it.

**3. `/api/dashboard/connect` → `/api/sync` timing out (500, "timeout of 120000ms exceeded" in the browser)**

`SERVICENOW_TIMEOUT_SECONDS` (in `Dashboard\backend\config.py`) defaults to 20s. This ServiceNow dev instance (`dev393867.service-now.com`) routinely takes 12–20s per paginated 1000-record page fetch, so any slightly slower page (observed on the `sc_req_item` table) exceeded the timeout and threw `httpx.ReadTimeout`, which `/api/sync` surfaces as a 500.

**Fix:** raised `SERVICENOW_TIMEOUT_SECONDS` to 60 (set as an env var on manual start; also added to the `Dashboard` service's `Env` block in `watchdog_all_backends.ps1` for when the watchdog task is running). Verified: full sync now completes (4564 incidents, 2453 changes, 5000 service requests), `/api/dashboard/status` reports `"connected":true,"synced":true"`.

---

## Network Security (NSG rules on `StratDev-nsg`, resource group `StratDev_group`)

| Rule | Port | Source | Purpose |
|---|---|---|---|
| `strat-iq-8090` | 8090 | App Service's `possibleOutboundIpAddresses` only (19 specific IPs, not "Internet") | The actual traffic path used today |
| `strat1` | 80 | Same restricted IP set (tightened this session from wide-open `*`) | Kept for potential future use; currently unused due to the port-80 HTTP.sys issue |
| `str` | 8080 | `*` | Pre-existing, unrelated to this work |
| `RDP` | 3389 | `*` | Pre-existing, unrelated to this work |

Re-fetch the App Service's outbound IPs if they ever change (Azure documents these as stable for the life of the App Service Plan, but always verify):
```bash
az webapp show -g mxc -n strat-iq --query "possibleOutboundIpAddresses" -o tsv
```

---

## Ollama Configuration

- **Runs on:** this VM, `http://localhost:11434`
- **Model:** `llama3.1:8b` (pulled locally, ~4.9GB)
- **Consumed by:**
  - **Novastra-ITSM** backend (port 8086) — confirmed live via `https://strat-iq.azurewebsites.net/api/novastra-itsm/settings`
  - **supply-chain-disruption-manager agent-service** (port 8002) — migrated off Claude API this session (`OLLAMA_BASE_URL`, `ORCHESTRATOR_MODEL=llama3.1:8b`, `SPECIALIST_MODEL=llama3.1:8b`, `MOCK_AGENTS=false`)
- Both call Ollama **server-side** (backend process → Ollama), entirely internal to the VM — this never depended on the Azure mapping working. The only thing the mapping needed to get right was the **browser-facing** API calls (see below), not the Ollama calls themselves.

---

## Frontend API URL Fixes (completed this session — required for the mapping to work at all)

Every module's frontend previously called its backend via a hardcoded absolute URL (`http://localhost:PORT`), which only works when the browser and backend are the same machine — a hard blocker for any remote/Azure access, independent of the network layer underneath. Fixed to relative paths, resolved by IIS `web.config` rewrite rules:

| Module | Old (broken for remote access) | Fixed to |
|---|---|---|
| Novastra-ITSM | `http://localhost:8086/api/novastra-itsm` | `/api/novastra-itsm` |
| SCM kg-service | `http://localhost:8001` | `/api/kg` |
| SCM signal-inspector | `http://localhost:8003` | `/api/inspector` |
| SCM agent-service | `http://localhost:8002` | `/api/agents` |
| Modernization, AI_Reman_Core, AI_Vehicle_Loan | Portal Home/Login links hardcoded to `:8090` or `:3000` | Relative (`/launch-modules`, `/login`) |

Two traps worth remembering if this breaks again after a rebuild:
1. **`vite.config.ts` can have its own `define` block** that silently re-hardcodes an absolute URL at build time, overriding the source-level fix (this happened with SCM — cost an extra rebuild cycle to catch). Check for `define: { 'import.meta.env.VITE_*': ... }` alongside the usual `.env.production` check.
2. **A base `.env` file (not `.env.production`) can also leak an absolute URL into production builds** — Vite applies the base `.env` to every mode unless overridden. Move dev-only absolute URLs into `.env.development` instead.

---

## Port Map (current, verified)

| Module | Backend Port | IIS Virtual App | IIS API Proxy Rule |
|---|---|---|---|
| AppRationalization (portal/auth) | 5000 (Flask) | site root | `/api/auth/*` |
| CodeAnalysis | 8082 | `/ca/` | `/api/(analyse\|portfolio\|jobs\|reports\|health\|modules\|ai)` |
| InfraRationalization | 8083 | `/infra/` | `/api/infra/*` |
| Modernization | 8084 | `/mod/` | `/api/mod/*` |
| Novastra-ITSM | 8086 | `/novastra-itsm/` | `/api/novastra-itsm/*` |
| Dashboard | 8087 | `/dash/` | `/api/dashboard/*` |
| SSDLC_Process_Assessment | 8091 | `/ssdlc/` | `/api/ssdlc/*`, `/api/csm/*` |
| OpportunityTracker | 8092 | `/ot/` | `/api/ot/*` |
| AI_Reman_Core | 8093 | `/reman/` | `/api/reman/*` |
| AI_Vehicle_Loan | 8094 | `/vl/` | `/api/vehicle-loan/*` |
| LabRobot | 8000 | `/lab/` | `/api/lab/*` |
| Microsite_Data_Analysis | — (static) | `/mda/` | — |
| SCM — kg-service | 8001 | `/scm/` | `/api/kg/*` |
| SCM — signal-inspector | 8003 | `/scm/` | `/api/inspector/*` |
| SCM — agent-service | 8002 | `/scm/` | `/api/agents/*` |
| Ollama | 11434 | — (not exposed to browser) | — |

IIS site: `StratIQ`, bound to `*:80:localhost`, `*:8090:`, and `*:8090:strat-iq.azurewebsites.net`. Physical root: `D:\StartIQ\AppRationalization\frontend\build`. `web.config` source of truth: `D:\StartIQ\AppRationalization\frontend\public\web.config` (copied into `build/` automatically on every `npm run build`).

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `500.19` on any IIS page after a fresh site setup | `webSocket` config section locked at machine level | `%windir%\system32\inetsrv\appcmd.exe unlock config /section:system.webServer/webSocket` |
| `502.3 Bad Gateway` on an `/api/*` path | The target backend process isn't running | Check `Get-NetTCPConnection -LocalPort <port> -State Listen`; relaunch the backend |
| Frontend loads but API calls fail after rebuild | Absolute `localhost:PORT` URL baked back in | Check source fallback, `.env.production`, base `.env`, **and** `vite.config.ts`'s `define` block; clear `node_modules/.vite` and rebuild |
| Portal Home / Login link goes to the wrong port | Stray absolute URL in `.env.production` or source fallback | Should be relative (`/launch-modules`, `/login`) |
| `strat-iq.azurewebsites.net` shows Azure's default placeholder page | No app deployed, or deployment failed silently | `az webapp deploy` with `SCM_DO_BUILD_DURING_DEPLOYMENT=true` set first; check `az webapp log download` |
| `403 Forbidden`, `Server: Microsoft-HTTPAPI/2.0`, on the VM's port 80 specifically | Unexplained HTTP.sys-level rejection, cause not fully root-caused | Use port 8090 instead (already what's deployed) — same IIS site, no host-header restriction there |
| `http://localhost` (or the Azure-mapped URL) shows the wrong/old site | Another IIS site's binding claims the same host/port ahead of the intended site | `Get-WebBinding`, then move the binding with `Remove-WebBinding` / `New-WebBinding` |
| Whole site (local and Azure-mapped) returns a bare `Internal Server Error` / times out after sitting idle for hours, with no w3wp.exe worker process actually serving requests | IIS app pool went unresponsive despite `startMode=AlwaysRunning` — `processModel.idleTimeout` was still the IIS default (20 min) and can override AlwaysRunning in practice | `Restart-WebAppPool -Name StratIQ-Project` fixes it immediately. Permanent fix (already applied and baked into `Create-IIS-StratIQProjectSite.ps1`): `Set-ItemProperty "IIS:\AppPools\StratIQ-Project" -Name processModel.idleTimeout -Value '00:00:00'` |
| Clicking a module launch link from `strat-iq.azurewebsites.net` redirects to `http://localhost/...` and 404s | Proxy (`main.py`) was rewriting every request's `Host` header to `"localhost"`, so IIS's own trailing-slash redirect built its absolute `Location` from that instead of the real public hostname | Add IIS binding `*:8090:strat-iq.azurewebsites.net`, set proxy's `VM_HOST_HEADER` to `"strat-iq.azurewebsites.net"`, and rewrite `Location: http://{VM_HOST_HEADER}/...` → `https://` before relaying — see "Host-Header Bug" section above |
| LLM calls hang/time out platform-wide after ~2 days of uptime, restarting `ollama`/`ollama app` doesn't help | Orphaned `llama-server.exe` subprocess detached from its parent and stuck holding GPU memory | Kill `llama-server.exe` by PID explicitly (not just `ollama*`), confirm GPU memory drops. Automated daily via the `StratIQ-Daily-GPU-Cache-Reset` scheduled task (`D:\StartIQ\Maintenance\Daily-GPU-Cache-Reset.ps1`, runs 3:00 AM daily) |
| `401 Unauthorized`, body `{"error":"Authentication required"}`, on every `/api/dashboard/*` call from the Dashboard module frontend | `web.config`'s general `Portal API Proxy` rule (matches literal `dashboard` in its alternation, meant only for Flask's own bare `/api/dashboard` endpoint) was shadowing the more specific `Dashboard API Proxy` rule due to rule order | Reorder so `Dashboard API Proxy` (`^api/dashboard/(.*)`, requires trailing slash) is checked before `Portal API Proxy` — already fixed in all three synced `web.config` copies |
| Dashboard module 502s even with the rule order correct | Dashboard backend (port 8087) isn't actually running — no watchdog currently restarts it | Check `Get-NetTCPConnection -LocalPort 8087 -State Listen`; start manually per the Running Services section in `CLAUDE.md`. See also the `StratIQ-Master-Watchdog` note below |
| Dashboard "Connect"/"Sync" times out client-side at 120s, backend logs show `httpx.ReadTimeout` on a ServiceNow table fetch (e.g. `sc_req_item`) | `SERVICENOW_TIMEOUT_SECONDS` (default 20s in `Dashboard\backend\config.py`) is too tight for this ServiceNow dev instance's real per-page latency (12-20s/page observed) | Set `SERVICENOW_TIMEOUT_SECONDS=60` env var when starting the Dashboard backend (already added to its `Env` block in `watchdog_all_backends.ps1`) |
| `StratIQ-Master-Watchdog` scheduled task referenced in `CLAUDE.md` doesn't exist / backends don't auto-restart on crash or VM reboot | The task was never (re-)registered on this VM, and `watchdog_all_backends.ps1` itself hardcoded a stale pre-migration path (`C:\STIQ\StratIQ_VM_AWS`) | Fixed: stale path corrected (`$Root = 'D:\StartIQ'`), and the task is now registered (`AtLogOn` trigger, `Interactive` logon type/`StratDev\stratdev` user — same as the GPU reset task, needed for GPU-backed backends) and started. Verify with `Get-ScheduledTask -TaskName StratIQ-Master-Watchdog` and `D:\StartIQ\logs\watchdog_master.log` |
| SCM module (`/scm/`) loads a blank page; console shows `GET https://strat-iq.azurewebsites.net/assets/index-*.js 404` (note: no `/scm/` prefix in the failing request) | `supply-chain-disruption-manager/apps/web-ui/vite.config.ts` defaulted `base` to `/` instead of `/scm/`, so the built `index.html` emitted root-relative asset URLs (`/assets/...`) instead of `/scm/assets/...`. Every other Vite module (CodeAnalysis, Dashboard, Novastra-ITSM, InfraRationalization, etc.) hardcodes its own subpath as `base` — SCM's web-ui was the one outlier | Fixed: `base: process.env.VITE_BASE_PATH || '/scm/'`, then rebuilt (`npm run build` in `apps/web-ui`). Verified: `index.html` now emits `/scm/assets/...`, both asset requests return 200 live |
| Whole site (local and Azure-mapped) recurs with a bare `Internal Server Error` even though `idleTimeout=0` and `startMode=AlwaysRunning` are correctly set; `netstat` shows 20+ stuck `CLOSE_WAIT` connections on port 8090 from the Azure proxy's outbound IP, only one w3wp.exe alive | `idleTimeout`/`AlwaysRunning` only prevent *idle*-triggered app-pool shutdown — they don't protect against the worker process hanging outright (e.g. from a burst of connections it never finishes responding to). This is a distinct failure mode from the original idle-timeout bug | `Restart-WebAppPool -Name StratIQ-Project` restores service immediately. Automated detection + restart via the `StratIQ-IIS-Health-Watchdog` scheduled task (`D:\StartIQ\Maintenance\IIS-Health-Watchdog.ps1`, checks `http://localhost:8090/` every 5 minutes, restarts the app pool on any non-2xx/3xx response or timeout) |
| SCM dashboard sidebar shows KG/Inspector/Agents as "DOWN" (red) even after the `/api/agents` 401 fix, all overview metrics show 0 | The 3 SCM microservices (kg-service :8001, agent-service :8002, signal-inspector :8003) had actually crashed — they were never included in `watchdog_all_backends.ps1`'s service list at all, so nothing restarted them | Restarted manually with the correct `D:\StartIQ` paths/env vars (previously only captured in stale `C:\STIQ\...`-path `.cmd` launcher files under `supply-chain-disruption-manager/logs/`). **Fixed for good**: added all 3 as `SCM-KG-Service`/`SCM-Agent-Service`/`SCM-Signal-Inspector` entries to `watchdog_all_backends.ps1` (now manages 14 services total) and restarted the `StratIQ-Master-Watchdog` task to pick them up |
| SCM services show "UP" and some data loads (e.g. the header's critical-incident count), but Overview/Knowledge Graph views hang forever on "Loading overview…"/"Loading graph…"; `netstat` shows `CLOSE_WAIT` connections on port 8090 rebuilding after every app-pool restart | **Root cause of both this AND the earlier whole-site CLOSE_WAIT/outage entry above.** IIS's global ARR proxy setting `bufferChunkedResponses` was `True`. SCM's live incident/event feed uses Server-Sent Events (`/api/agents/incidents/stream`, chunked transfer encoding, connection stays open indefinitely). ARR was trying to fully buffer each streamed response before forwarding it — since an SSE stream never completes, ARR held that connection (and its backend worker/thread) open forever waiting for a buffer that would never finish, eventually leaking into `CLOSE_WAIT` and, at scale, starving other requests through the same site of connections/threads | Fixed at the IIS machine level: `Set-WebConfigurationProperty -Filter "system.webServer/proxy" -PSPath "IIS:\" -Name "bufferChunkedResponses" -Value $false`, then `Restart-WebAppPool -Name StratIQ-Project` to clear existing stuck connections. Verified: SSE stream now delivers real events immediately; regular API calls (`incidents`, `inspector/events`, `kg/health`, `kg/entities`) all return 200 in <0.5s *while* a stream is concurrently open; `CLOSE_WAIT` count on port 8090 returned to 0 within ARR's 2-minute timeout window instead of accumulating unbounded |

---

## Quick Reference

| Item | Value |
|---|---|
| Public URL | `https://strat-iq.azurewebsites.net` |
| App Service resource group | `mxc` (East US 2) |
| App Service runtime | Python 3.14, FastAPI reverse-proxy deployed |
| VM name | `StratDev` (resource group `mxc`, West US) |
| VM public IP | `104.45.218.69` |
| VM private IP | `10.0.0.4` |
| Proxy target | `http://104.45.218.69:8090` |
| Local IIS site | `StratIQ` (`:80` host `localhost`, `:8090` no host restriction, `:8090` host `strat-iq.azurewebsites.net`) |
| Proxy app source | `C:\StratIQ\HybridBridge\...` *(legacy, unused)* / `C:\StratIQ\AppServiceProxy\main.py` *(active)* |
| Ollama | `http://localhost:11434`, model `llama3.1:8b` |
| SCM kg-service / signal-inspector / agent-service | `8001` / `8003` / `8002` |
