# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: supply-chain-disruption-manager — scripts (Build-IIS.ps1)
# Date: 2025-09-14
# ---------------------------------------------------------------------------
param(
    [string]$SitePath = "C:\inetpub\wwwroot\sc-disruption-manager"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$uiPath = Join-Path $root "apps\web-ui"
$distPath = Join-Path $uiPath "dist"

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw "npm was not found. Install Node.js 20+ and reopen PowerShell."
}

$env:VITE_KG_API_URL = "http://localhost:8001"
$env:VITE_BASE_PATH = "/sc-disruption-manager/"
$env:VITE_KG_API_KEY = "kg-dev-key-change-in-prod"
$env:VITE_INSPECTOR_API_URL = "http://localhost:8003"
$env:VITE_INSPECTOR_API_KEY = "inspector-dev-key"
$env:VITE_AGENT_API_URL = "http://localhost:8002"
$env:VITE_AGENT_API_KEY = "agent-dev-key-change-in-prod"
$env:VITE_PORTAL_HOME_URL = "http://localhost:8090/launch-modules"
$env:VITE_PORTAL_LOGIN_URL = "http://localhost:8090/login"

Push-Location $uiPath
npm install
npm run build
Pop-Location

if (-not (Test-Path $SitePath)) {
    New-Item -ItemType Directory -Path $SitePath -Force | Out-Null
}

Copy-Item "$distPath\*" $SitePath -Recurse -Force

Write-Host ""
Write-Host "IIS build copied to $SitePath"
Write-Host "Point an IIS site or application at that folder."
Write-Host "The UI will call APIs on http://localhost:8001, :8002, and :8003."
