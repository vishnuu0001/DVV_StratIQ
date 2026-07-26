[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$port = 8084
$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot 'Modernization'
$pythonExe = Join-Path $backendDir '.venv\Scripts\python.exe'

$listener = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue |
    Select-Object -First 1
if ($listener) {
    $worker = Get-CimInstance Win32_Process -Filter "ProcessId=$($listener.OwningProcess)"
    $parent = if ($worker) {
        Get-CimInstance Win32_Process -Filter "ProcessId=$($worker.ParentProcessId)"
    } else {
        $null
    }
    $candidate = if (
        $parent -and (
            $parent.CommandLine -match 'uvicorn\s+api\.server:app'
            -or $parent.ExecutablePath -eq $pythonExe
        )
    ) {
        $parent
    } elseif (
        $worker -and (
            $worker.CommandLine -match 'uvicorn\s+api\.server:app'
            -or $worker.ExecutablePath -eq $pythonExe
        )
    ) {
        $worker
    } else {
        throw "Port $port is owned by an unrecognized process; refusing to terminate it."
    }
    & taskkill.exe /PID $candidate.ProcessId /T /F | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to terminate Modernization process tree $($candidate.ProcessId)."
    }
}

$deadline = (Get-Date).AddSeconds(45)
do {
    Start-Sleep -Seconds 2
    $listening = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
} while (-not $listening -and (Get-Date) -lt $deadline)

if (-not $listening) {
    . (Join-Path $PSScriptRoot 'Shared-Auth.ps1')
    $env:AUTH_TOKEN_SECRET = Get-Strat-AqorynthSharedAuthSecret -RepoRoot $repoRoot
    $env:AUTH_TOKEN_TTL_SECONDS = '28800'
    $env:AUTH_REQUIRED = 'true'
    $env:CORS_ORIGINS = 'http://localhost,http://127.0.0.1,http://localhost:8090,http://127.0.0.1:8090,http://localhost:3000,http://127.0.0.1:3000,https://stratapp.org'
    $env:OLLAMA_BASE_URL = 'http://localhost:11434'
    Start-Process -FilePath $pythonExe `
        -ArgumentList @('-m', 'uvicorn', 'api.server:app', '--host', '0.0.0.0', '--port', '8084', '--log-level', 'info') `
        -WorkingDirectory $backendDir -WindowStyle Hidden
}
