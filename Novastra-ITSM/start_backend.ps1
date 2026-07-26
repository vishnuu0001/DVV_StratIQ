# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Novastra-ITSM — start_backend (start_backend.ps1)
# Date: 2025-11-24
# ---------------------------------------------------------------------------
# Start Novastra-ITSM — backend + frontend together (Windows)
$root = $PSScriptRoot
Set-Location $root

if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "Created .env from .env.example. Edit it before use." -ForegroundColor Yellow
    } else {
        Write-Host "ERROR: .env file not found!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Starting Novastra-ITSM backend  -> http://localhost:8086" -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root'; uvicorn backend.main:app --reload --host 0.0.0.0 --port 8086" -WindowStyle Normal

Write-Host "Starting Novastra-ITSM frontend -> http://localhost:5173" -ForegroundColor Cyan
$frontendPath = Join-Path $root "frontend"
Set-Location $frontendPath
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm packages..." -ForegroundColor Yellow
    npm install
}

Write-Host "`nBackend running in a separate window. Press Ctrl+C here to stop the frontend.`n" -ForegroundColor Green
npm run dev
