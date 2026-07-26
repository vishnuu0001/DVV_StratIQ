# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: OpportunityTracker — watchdog_backend (watchdog_backend.ps1)
# Date: 2026-03-12
# ---------------------------------------------------------------------------
# OpportunityTracker Backend Watchdog
# Monitors the FastAPI backend on port 8092 and restarts it if it stops.
# Intended to be launched via scheduled task at logon, or via Start-AllServices.ps1.

$ProjectDir = Join-Path $PSScriptRoot 'backend'
$PythonExe  = Join-Path $ProjectDir '.venv\Scripts\python.exe'
$LogsDir    = Join-Path (Split-Path $PSScriptRoot -Parent) 'logs'
if (-not (Test-Path $LogsDir)) { New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null }
$LogFile    = Join-Path $LogsDir 'ot_backend.log'
$StdoutFile = Join-Path $LogsDir 'ot_backend_stdout.log'
$CheckSecs  = 30

# Function: Is-OTRunning
function Is-OTRunning {
    $conn = Get-NetTCPConnection -LocalPort 8092 -State Listen -ErrorAction SilentlyContinue
    return ($null -ne $conn)
}

# Function: Start-OTBackend
function Start-OTBackend {
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName               = $PythonExe
    $psi.Arguments              = '-m uvicorn main:app --host 0.0.0.0 --port 8092'
    $psi.WorkingDirectory       = $ProjectDir
    $psi.UseShellExecute        = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError  = $true
    $psi.CreateNoWindow         = $true

    $proc = New-Object System.Diagnostics.Process
    $proc.StartInfo = $psi

    $stdoutAction = { Add-Content -Path $StdoutFile -Value $Event.SourceEventArgs.Data }
    $stderrAction = { Add-Content -Path $LogFile    -Value $Event.SourceEventArgs.Data }
    Register-ObjectEvent -InputObject $proc -EventName OutputDataReceived -Action $stdoutAction | Out-Null
    Register-ObjectEvent -InputObject $proc -EventName ErrorDataReceived  -Action $stderrAction | Out-Null

    $proc.Start() | Out-Null
    $proc.BeginOutputReadLine()
    $proc.BeginErrorReadLine()

    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    "[Watchdog $timestamp] OpportunityTracker backend started (PID $($proc.Id))" | Add-Content $LogFile
    return $proc
}

$otProc = $null
while ($true) {
    if (-not (Is-OTRunning)) {
        $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
        "[Watchdog $timestamp] Port 8092 not listening - starting OT backend..." | Add-Content $LogFile

        $zombie = Get-NetTCPConnection -LocalPort 8092 -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($zombie) { Stop-Process -Id $zombie.OwningProcess -Force -ErrorAction SilentlyContinue }
        Start-Sleep -Seconds 2

        $otProc = Start-OTBackend
        Start-Sleep -Seconds 8
    }
    Start-Sleep -Seconds $CheckSecs
}
