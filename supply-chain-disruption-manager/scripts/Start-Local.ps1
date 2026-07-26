# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: supply-chain-disruption-manager — scripts (Start-Local.ps1)
# Date: 2025-09-09
# ---------------------------------------------------------------------------
param(
    [switch]$SkipUi
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
New-Item -ItemType Directory -Path (Join-Path $root "logs") -Force | Out-Null

if (-not (Test-Path (Join-Path $root ".env"))) {
    Copy-Item (Join-Path $root ".env.localhost") (Join-Path $root ".env")
}

# Function: Import-DotEnv
function Import-DotEnv($Path) {
    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#") -or -not $line.Contains("=")) {
            return
        }
        $parts = $line.Split("=", 2)
        [Environment]::SetEnvironmentVariable($parts[0], $parts[1], "Process")
    }
}

# Function: Test-Port
function Test-Port($Port, $Name) {
    $ok = Test-NetConnection -ComputerName localhost -Port $Port -InformationLevel Quiet
    if (-not $ok) {
        Write-Warning "$Name is not reachable on localhost:$Port. Start it before using the app."
    }
}

# Function: Start-ServiceWindow
function Start-ServiceWindow($Title, $ServicePath, $Module, $Port) {
    $fullPath = Join-Path $root $ServicePath
    $python = Join-Path $fullPath ".venv\Scripts\python.exe"
    if (-not (Test-Path $python)) {
        throw "Missing virtual environment for $Title. Run .\scripts\Install-Local.ps1 first."
    }

    $src = Join-Path $fullPath "src"
    $cmdPath = Join-Path $root "logs\start-$Title.cmd"
    $cmd = @"
@echo off
cd /d "$root"
set "PYTHONPATH=$src"
set "ENVIRONMENT=development"
set "DEBUG=true"
set "LOG_JSON=false"
set "NEO4J_URI=bolt://localhost:7687"
set "NEO4J_USER=neo4j"
set "NEO4J_PASSWORD=disruption123"
set "KG_API_KEY=kg-dev-key-change-in-prod"
set "KG_BASE_URL=http://localhost:8001"
set "POSTGRES_URL=postgresql+asyncpg://sc_admin:sc_secret@localhost:5432/disruption_mgr"
set "REDIS_URL=redis://localhost:6379/0"
set "AGENT_API_KEY=agent-dev-key-change-in-prod"
set "AGENT_BASE_URL=http://localhost:8002"
set "INSPECTOR_ERP_HMAC_SECRET=erp-hmac-secret-change-in-prod"
set "MOCK_AGENTS=true"
"$python" -m uvicorn $Module --host 127.0.0.1 --port $Port --reload
pause
"@
    Set-Content -Path $cmdPath -Value $cmd -Encoding ASCII

    Start-Process -FilePath "cmd.exe" -ArgumentList @("/k", "`"$cmdPath`"") -WindowStyle Normal
}

Import-DotEnv (Join-Path $root ".env")

Test-Port 7474 "Neo4j HTTP"
Test-Port 7687 "Neo4j Bolt"
Test-Port 5432 "Postgres"
Test-Port 6379 "Redis"

Start-ServiceWindow "KG Service" "services\kg-service" "kg.main:app" 8001
Start-ServiceWindow "Signal Inspector" "services\signal-inspector" "inspector.main:app" 8003
Start-ServiceWindow "Agent Service" "services\agent-service" "agents.main:app" 8002

if (-not $SkipUi) {
    $uiPath = Join-Path $root "apps\web-ui"
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "cd '$uiPath'; npm run dev -- --host 127.0.0.1"
    ) -WindowStyle Normal
}

Write-Host ""
Write-Host "Services are starting:"
Write-Host "  Web UI            http://localhost:5173"
Write-Host "  KG Service        http://localhost:8001"
Write-Host "  Agent Service     http://localhost:8002"
Write-Host "  Signal Inspector  http://localhost:8003"
