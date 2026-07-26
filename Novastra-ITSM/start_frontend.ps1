# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Novastra-ITSM — start_frontend (start_frontend.ps1)
# Date: 2026-03-25
# ---------------------------------------------------------------------------
# Start frontend dev server (Windows)
Write-Host "Starting Novastra-ITSM frontend..." -ForegroundColor Cyan
Set-Location "$PSScriptRoot\frontend"
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm packages..." -ForegroundColor Yellow
    npm install
}
npm run dev
