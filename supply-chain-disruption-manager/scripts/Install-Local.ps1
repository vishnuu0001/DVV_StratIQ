# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: supply-chain-disruption-manager — scripts (Install-Local.ps1)
# Date: 2026-06-14
# ---------------------------------------------------------------------------
param(
    [switch]$SkipNode
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

# Function: Ensure-Command
function Ensure-Command($Name, $InstallHint) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "$Name was not found. $InstallHint"
    }
}

Ensure-Command python "Install Python 3.11+ and reopen PowerShell."
if (-not $SkipNode) {
    Ensure-Command npm "Install Node.js 20+ and reopen PowerShell."
}

if (-not (Test-Path (Join-Path $root ".env"))) {
    Copy-Item (Join-Path $root ".env.localhost") (Join-Path $root ".env")
    Write-Host "Created .env from .env.localhost"
}

$services = @(
    @{ Name = "kg-service"; Path = "services\kg-service" },
    @{ Name = "signal-inspector"; Path = "services\signal-inspector" },
    @{ Name = "agent-service"; Path = "services\agent-service" }
)

foreach ($service in $services) {
    $servicePath = Join-Path $root $service.Path
    $venvPath = Join-Path $servicePath ".venv"
    if (-not (Test-Path $venvPath)) {
        Write-Host "Creating virtual environment for $($service.Name)..."
        python -m venv $venvPath
    }

    $python = Join-Path $venvPath "Scripts\python.exe"
    Write-Host "Installing Python dependencies for $($service.Name)..."
    & $python -m pip install --upgrade pip
    & $python -m pip install -e $servicePath
}

if (-not $SkipNode) {
    Write-Host "Installing Web UI dependencies..."
    Push-Location (Join-Path $root "apps\web-ui")
    npm install
    Pop-Location
}

Write-Host ""
Write-Host "Local dependencies installed. Start Neo4j, Postgres, and Redis, then run:"
Write-Host "  .\scripts\Start-Local.ps1"
