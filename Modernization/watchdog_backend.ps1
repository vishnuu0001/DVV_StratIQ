# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — watchdog_backend (watchdog_backend.ps1)
# Date: 2026-05-21
# ---------------------------------------------------------------------------
# Modernization Backend Watchdog
# Monitors uvicorn on port 8084, restarts it if down.
# Runs forever - launched via scheduled task at logon.

$BackendDir  = Join-Path $PSScriptRoot ''
$PythonExe   = "$BackendDir\.venv\Scripts\python.exe"
$LogFile     = 'C:\STIQ\Strat-Aqorynth_VM_AWS\logs\modernization_stderr.log'
$StdoutFile  = 'C:\STIQ\Strat-Aqorynth_VM_AWS\logs\modernization_stdout.log'
$CheckSecs   = 30
$Port        = 8084
$FrontendDir = Join-Path $BackendDir 'frontend'
$FrontendSyncScript = Join-Path $BackendDir 'Sync-ProductionBuild.ps1'
$FrontendSyncPidFile = Join-Path $BackendDir 'data\frontend-sync.pid'
$BackendSourceDirs = @(
    (Join-Path $BackendDir 'api'),
    (Join-Path $BackendDir 'services')
)
. (Join-Path (Split-Path -Parent $PSScriptRoot) 'Maintenance\Shared-Auth.ps1')
$SharedAuthSecret = Get-Strat-AqorynthSharedAuthSecret -RepoRoot (Split-Path -Parent $PSScriptRoot)

# Function: Ensure-FrontendProductionSync
function Ensure-FrontendProductionSync {
    if (-not (Test-Path -LiteralPath $FrontendSyncScript)) { return }
    $syncRunning = $false
    if (Test-Path -LiteralPath $FrontendSyncPidFile) {
        $syncPid = Get-Content -LiteralPath $FrontendSyncPidFile -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($syncPid) { $syncRunning = $null -ne (Get-Process -Id $syncPid -ErrorAction SilentlyContinue) }
    }
    if ($syncRunning) { return }

    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $FrontendSyncPidFile) | Out-Null
    $syncProcess = Start-Process -FilePath 'powershell.exe' `
        -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $FrontendSyncScript) `
        -WindowStyle Hidden -PassThru
    Set-Content -LiteralPath $FrontendSyncPidFile -Value $syncProcess.Id
}

# Function: Is-BackendRunning
function Is-BackendRunning {
    $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    return ($null -ne $conn)
}

# Function: Get-BackendListenerProcess
function Get-BackendListenerProcess {
    $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $connection) { return $null }
    return Get-Process -Id $connection.OwningProcess -ErrorAction SilentlyContinue
}

# Function: Get-LatestBackendSourceWrite
function Get-LatestBackendSourceWrite {
    $latest = [datetime]::MinValue
    foreach ($sourceDir in $BackendSourceDirs) {
        if (-not (Test-Path -LiteralPath $sourceDir)) { continue }
        $candidate = Get-ChildItem -LiteralPath $sourceDir -Recurse -File -Filter '*.py' -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
        if ($candidate -and $candidate.LastWriteTimeUtc -gt $latest) { $latest = $candidate.LastWriteTimeUtc }
    }
    return $latest
}

# Function: Restart-BackendWhenSourceChanged
function Restart-BackendWhenSourceChanged {
    $process = Get-BackendListenerProcess
    if (-not $process) { return }
    $latestSource = Get-LatestBackendSourceWrite
    if ($latestSource -le $process.StartTime.ToUniversalTime()) { return }

    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    "[Watchdog $timestamp] Backend source changed after process start; restarting PID $($process.Id)." | Add-Content $LogFile
    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# Function: Start-Backend
function Start-Backend {
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName  = $PythonExe
    $psi.Arguments = '-m uvicorn api.server:app --host 0.0.0.0 --port 8084 --log-level info'
    $psi.WorkingDirectory       = $BackendDir
    $psi.UseShellExecute        = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError  = $true
    $psi.CreateNoWindow         = $true

    $psi.EnvironmentVariables['AUTH_TOKEN_SECRET']   = $SharedAuthSecret
    $psi.EnvironmentVariables['AUTH_TOKEN_TTL_SECONDS'] = '28800'
    $psi.EnvironmentVariables['AUTH_REQUIRED']       = 'true'
    $psi.EnvironmentVariables['CORS_ORIGINS']        = 'http://localhost,http://127.0.0.1,http://localhost:8090,http://127.0.0.1:8090,http://localhost:3000,http://127.0.0.1:3000'
    $psi.EnvironmentVariables['OLLAMA_BASE_URL']     = 'http://localhost:11434'
    # Model is forced to qwen3.5:9b in services/llm.py — not configurable via env var.

    $proc = New-Object System.Diagnostics.Process
    $proc.StartInfo = $psi

    $stdoutAction = { Add-Content -Path $StdoutFile -Value $Event.SourceEventArgs.Data }
    $stderrAction = { Add-Content -Path $LogFile    -Value $Event.SourceEventArgs.Data }
    Register-ObjectEvent -InputObject $proc -EventName OutputDataReceived -Action $stdoutAction | Out-Null
    Register-ObjectEvent -InputObject $proc -EventName ErrorDataReceived  -Action $stderrAction | Out-Null

    $proc.Start()             | Out-Null
    $proc.BeginOutputReadLine()
    $proc.BeginErrorReadLine()

    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    "[Watchdog $timestamp] Modernization backend started (PID $($proc.Id))" | Add-Content $LogFile
    return $proc
}

$backendProc = $null
while ($true) {
    Ensure-FrontendProductionSync
    Restart-BackendWhenSourceChanged
    if (-not (Is-BackendRunning)) {
        $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
        "[Watchdog $timestamp] Port $Port not listening - starting Modernization backend..." | Add-Content $LogFile

        $zombie = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($zombie) { Stop-Process -Id $zombie.OwningProcess -Force -ErrorAction SilentlyContinue }
        Start-Sleep -Seconds 2

        $backendProc = Start-Backend
        Start-Sleep -Seconds 10
    }
    Start-Sleep -Seconds $CheckSecs
}
