# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: supply-chain-disruption-manager — Start+Services (Start+Services.ps1)
# Date: 2026-05-13
# ---------------------------------------------------------------------------
param(
    [switch]$NoBrowser,
    [switch]$SkipUi,
    [switch]$NoWait,
    [switch]$RestartApps
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$logs = Join-Path $root "logs"
New-Item -ItemType Directory -Path $logs -Force | Out-Null

# Function: Write-Step
function Write-Step($Message) {
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

# Function: Ensure-EnvFile
function Ensure-EnvFile {
    $envPath = Join-Path $root ".env"
    $localEnvPath = Join-Path $root ".env.localhost"
    if (-not (Test-Path $envPath)) {
        Copy-Item $localEnvPath $envPath -Force
        Write-Host "Created .env from .env.localhost"
    }
}

# Function: Test-PortOpen
function Test-PortOpen($Port) {
    $client = [System.Net.Sockets.TcpClient]::new()
    try {
        $connect = $client.BeginConnect("127.0.0.1", $Port, $null, $null)
        if (-not $connect.AsyncWaitHandle.WaitOne(1000, $false)) {
            return $false
        }
        $client.EndConnect($connect)
        return $true
    }
    catch {
        return $false
    }
    finally {
        $client.Close()
    }
}

# Function: Wait-Port
function Wait-Port($Port, $Name, $TimeoutSeconds = 90) {
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-PortOpen $Port) {
            Write-Host "$Name is listening on localhost:$Port" -ForegroundColor Green
            return
        }
        Start-Sleep -Seconds 2
    }
    throw "$Name did not start on localhost:$Port within $TimeoutSeconds seconds."
}

# Function: Wait-Http
function Wait-Http($Url, $Name, $Headers = @{}, $TimeoutSeconds = 90) {
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            Invoke-RestMethod -Uri $Url -Headers $Headers -TimeoutSec 5 | Out-Null
            Write-Host "$Name health check passed" -ForegroundColor Green
            return
        }
        catch {
            Start-Sleep -Seconds 2
        }
    }
    throw "$Name health check failed at $Url within $TimeoutSeconds seconds."
}

# Function: Stop-ProcessOnPort
function Stop-ProcessOnPort($Port, $Name) {
    $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    $processIds = @($connections | Select-Object -ExpandProperty OwningProcess -Unique)
    foreach ($processId in $processIds) {
        if (-not $processId) {
            continue
        }
        try {
            $process = Get-Process -Id $processId -ErrorAction Stop
            Write-Host "Stopping $Name on localhost:$Port (PID $processId, $($process.ProcessName))..."
            Stop-Process -Id $processId -Force
        }
        catch {
            Write-Warning "Could not stop $Name process on port $Port. $($_.Exception.Message)"
        }
    }
}

# Function: Start-WindowsServiceIfPresent
function Start-WindowsServiceIfPresent($Name, $DisplayName) {
    $service = Get-Service -Name $Name -ErrorAction SilentlyContinue
    if (-not $service) {
        Write-Warning "$DisplayName service '$Name' was not found."
        return
    }

    if ($service.Status -ne "Running") {
        Write-Host "Starting $DisplayName..."
        try {
            Start-Service -Name $Name
        }
        catch {
            throw "Could not start $DisplayName service '$Name'. Run PowerShell as Administrator and retry. $($_.Exception.Message)"
        }
    }
    else {
        Write-Host "$DisplayName is already running"
    }
}

# Function: Start-Backend
function Start-Backend($Title, $ServicePath, $Module, $Port) {
    if (Test-PortOpen $Port) {
        Write-Host "$Title is already listening on localhost:$Port" -ForegroundColor Green
        return
    }

    $serviceRoot = Join-Path $root $ServicePath
    $python = Join-Path $serviceRoot ".venv\Scripts\python.exe"
    $src = Join-Path $serviceRoot "src"
    if (-not (Test-Path $python)) {
        throw "Missing Python venv for $Title at $python. Run .\scripts\Install-Local.ps1 first."
    }

    $safeTitle = $Title.Replace(" ", "-")
    $cmdPath = Join-Path $logs "run-$safeTitle.cmd"
    $cmd = @"
@echo off
title $Title
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
"$python" -m uvicorn $Module --host 127.0.0.1 --port $Port
pause
"@
    Set-Content -Path $cmdPath -Value $cmd -Encoding ASCII

    Write-Host "Launching $Title..."
    Start-Process -FilePath "cmd.exe" -ArgumentList @("/k", "`"$cmdPath`"") -WorkingDirectory $root -WindowStyle Normal
}

# Function: Start-WebUi
function Start-WebUi {
    if (Test-PortOpen 5173) {
        Write-Host "Web UI is already listening on localhost:5173" -ForegroundColor Green
        return
    }

    $uiPath = Join-Path $root "apps\web-ui"
    if (-not (Test-Path (Join-Path $uiPath "package.json"))) {
        throw "Web UI package.json not found at $uiPath"
    }

    $cmdPath = Join-Path $logs "run-Web-UI.cmd"
    $cmd = @"
@echo off
title Web UI
cd /d "$uiPath"
set "VITE_KG_API_URL=http://localhost:8001"
set "VITE_KG_API_KEY=kg-dev-key-change-in-prod"
set "VITE_INSPECTOR_API_URL=http://localhost:8003"
set "VITE_INSPECTOR_API_KEY=inspector-dev-key"
set "VITE_AGENT_API_URL=http://localhost:8002"
set "VITE_AGENT_API_KEY=agent-dev-key-change-in-prod"
npm run dev -- --host 127.0.0.1
pause
"@
    Set-Content -Path $cmdPath -Value $cmd -Encoding ASCII

    Write-Host "Launching Web UI..."
    Start-Process -FilePath "cmd.exe" -ArgumentList @("/k", "`"$cmdPath`"") -WorkingDirectory $uiPath -WindowStyle Normal
}

Write-Step "Preparing local environment"
Ensure-EnvFile

Write-Step "Starting infrastructure services"
Start-WindowsServiceIfPresent "postgresql-x64-16" "PostgreSQL 16"
Start-WindowsServiceIfPresent "Memurai" "Redis-compatible Memurai"
Start-WindowsServiceIfPresent "neo4j" "Neo4j"

if (-not $NoWait) {
    Wait-Port 5432 "PostgreSQL"
    Wait-Port 6379 "Redis-compatible Memurai"
    Wait-Port 7474 "Neo4j HTTP"
    Wait-Port 7687 "Neo4j Bolt"
}

Write-Step "Launching backend APIs"
if ($RestartApps) {
    Stop-ProcessOnPort 8001 "KG Service"
    Stop-ProcessOnPort 8003 "Signal Inspector"
    Stop-ProcessOnPort 8002 "Agent Service"
    if (-not $SkipUi) {
        Stop-ProcessOnPort 5173 "Web UI"
    }
}
Start-Backend "KG Service" "services\kg-service" "kg.main:app" 8001
Start-Backend "Signal Inspector" "services\signal-inspector" "inspector.main:app" 8003
Start-Backend "Agent Service" "services\agent-service" "agents.main:app" 8002

if (-not $SkipUi) {
    Write-Step "Launching Web UI"
    Start-WebUi
}

if (-not $NoWait) {
    Write-Step "Waiting for application health checks"
    Wait-Http "http://localhost:8001/health" "KG Service"
    Wait-Http "http://localhost:8003/health" "Signal Inspector"
    Wait-Http "http://localhost:8002/health" "Agent Service" @{ "X-API-Key" = "agent-dev-key-change-in-prod" }
    if (-not $SkipUi) {
        Wait-Port 5173 "Web UI"
    }
}

Write-Step "Application is ready"
Write-Host "Web UI:            http://localhost:5173"
Write-Host "KG Service:        http://localhost:8001"
Write-Host "Agent Service:     http://localhost:8002"
Write-Host "Signal Inspector:  http://localhost:8003"
Write-Host "Neo4j Browser:     http://localhost:7474"

if (-not $NoBrowser -and -not $SkipUi) {
    Start-Process "http://localhost:5173"
}
