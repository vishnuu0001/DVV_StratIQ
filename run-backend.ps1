# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: run-backend.ps1 — run-backend (run-backend.ps1)
# Date: 2025-10-01
# ---------------------------------------------------------------------------
[CmdletBinding()]
param(
    [ValidateSet('CodeAnalysis', 'Novastra-ITSM', 'Dashboard', 'IntuneAutomation', 'ToolAnalysis')]
    [string]$Backend = 'CodeAnalysis',

    [int]$Port = 0,

    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSCommandPath
$logDir = Join-Path $repoRoot 'Data\logs'

$backendConfig = @{
    CodeAnalysis = @{
        Directory = Join-Path $repoRoot 'CodeAnalysis'
        App = 'api.server:app'
        Port = 8082
        ExtraEnv = @{}
    }
    'Novastra-ITSM' = @{
        Directory = Join-Path $repoRoot 'Novastra-ITSM'
        App = 'backend.main:app'
        Port = 8086
        ExtraEnv = @{}
    }
    Dashboard = @{
        Directory = Join-Path $repoRoot 'Dashboard\backend'
        App = 'main:app'
        Port = 8087
        ExtraEnv = @{}
    }
    IntuneAutomation = @{
        Directory = Join-Path $repoRoot 'IntuneAutomation\backend'
        App = 'app.main:app'
        Port = 8088
        ExtraEnv = @{
            CORS_ORIGINS = 'http://localhost,http://localhost/intune,http://localhost:5179,http://localhost:8080'
            REDIRECT_URI = 'http://localhost/intune/auth/callback'
        }
    }
    ToolAnalysis = @{
        Directory = Join-Path $repoRoot 'Tool_Analysis_Qualification\backend'
        App = 'app.main:app'
        Port = 8010
        ExtraEnv = @{
            OLLAMA_BASE_URL = 'http://localhost:11434'
            OLLAMA_MODEL = 'llama3.1'
            OLLAMA_NUM_GPU = '-1'
        }
    }
}

$config = $backendConfig[$Backend]
if (-not $config) {
    throw "Unsupported backend: $Backend"
}

$backendDir = $config.Directory
if (-not (Test-Path -LiteralPath $backendDir)) {
    throw "$Backend backend directory not found: $backendDir"
}

if ($Port -le 0) {
    $Port = [int]$config.Port
}

if (-not (Test-Path -LiteralPath $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

$venvPython = Join-Path $backendDir '.venv\Scripts\python.exe'
$pythonExe = if (Test-Path -LiteralPath $venvPython) { $venvPython } else { 'python' }
$logFile = Join-Path $logDir "Strat-Aqorynth-$Backend.out"
$app = [string]$config.App

foreach ($name in $config.ExtraEnv.Keys) {
    Set-Item -Path "Env:$name" -Value $config.ExtraEnv[$name]
}

$message = "Starting $Backend backend on port $Port at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
if ($DryRun) {
    Write-Host "DRY-RUN: $message" -ForegroundColor Yellow
    Write-Host "DRY-RUN: Set-Location '$backendDir'" -ForegroundColor Yellow
    Write-Host "DRY-RUN: & '$pythonExe' -m uvicorn $app --host 127.0.0.1 --port $Port --log-level info --access-log" -ForegroundColor Yellow
    Write-Host "DRY-RUN: log file: $logFile" -ForegroundColor Yellow
    return
}

Set-Location -LiteralPath $backendDir
Write-Output $message | Tee-Object -FilePath $logFile -Append

$ErrorActionPreference = 'Continue'
& $pythonExe -m uvicorn $app --host 127.0.0.1 --port $Port --log-level info --access-log
