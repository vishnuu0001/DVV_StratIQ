# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: LabRobot — start (start.ps1)
# Date: 2025-07-16
# ---------------------------------------------------------------------------
# Start the Lab Chemical Management project
# Backend: FastAPI on port 8000
# Frontend: Vite dev server

$root = $PSScriptRoot

# Free port 8000 if already in use
$be = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
if ($be) { Stop-Process -Id $be -Force -ErrorAction SilentlyContinue; Write-Host "Freed port 8000 (PID $be)" }

# Free port 7000 if already in use
$fe = Get-NetTCPConnection -LocalPort 7000 -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
if ($fe) { Stop-Process -Id $fe -Force -ErrorAction SilentlyContinue; Write-Host "Freed port 7000 (PID $fe)" }

# Start backend in a new terminal window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m uvicorn main:app --reload --port 8000 --app-dir '$root\backend'"

# Start frontend in a new terminal window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm --prefix '$root\frontend' run dev"

Write-Host "Starting backend at http://localhost:8000"
Write-Host "Starting frontend at http://localhost:7000 (or next available port >= 7000)"
