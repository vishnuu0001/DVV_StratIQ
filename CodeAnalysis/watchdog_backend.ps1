# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: CodeAnalysis — watchdog_backend (watchdog_backend.ps1)
# Date: 2026-02-06
# ---------------------------------------------------------------------------
# StratApp CodeAnalysis Backend Watchdog
# Monitors the FastAPI backend on port 8082 and restarts it if it stops.
# IIS reverse proxy routes /api/* -> http://127.0.0.1:8082

$ProjectDir  = $PSScriptRoot
$PythonExe   = Join-Path $ProjectDir '.venv\Scripts\python.exe'
$LogFile     = 'E:\codeanalysis_stderr.log'
$StdoutFile  = 'E:\codeanalysis_stdout.log'
$CheckSecs   = 30

# Function: Is-CodeAnalysisRunning
function Is-CodeAnalysisRunning {
    $conn = Get-NetTCPConnection -LocalPort 8082 -State Listen -ErrorAction SilentlyContinue
    return ($null -ne $conn)
}

# Function: Start-CodeAnalysis
function Start-CodeAnalysis {
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName               = $PythonExe
    $psi.Arguments              = '-m uvicorn api.server:app --host 0.0.0.0 --port 8082'
    $psi.WorkingDirectory       = $ProjectDir
    $psi.UseShellExecute        = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError  = $true
    $psi.CreateNoWindow         = $true

    $proc = New-Object System.Diagnostics.Process
    $proc.StartInfo = $psi

    $stdoutAction = { Add-Content -Path $StdoutFile -Value $Event.SourceEventArgs.Data }
    $stderrAction = { Add-Content -Path $LogFile -Value $Event.SourceEventArgs.Data }
    Register-ObjectEvent -InputObject $proc -EventName OutputDataReceived -Action $stdoutAction | Out-Null
    Register-ObjectEvent -InputObject $proc -EventName ErrorDataReceived -Action $stderrAction | Out-Null

    $proc.Start() | Out-Null
    $proc.BeginOutputReadLine()
    $proc.BeginErrorReadLine()

    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    "[Watchdog $timestamp] CodeAnalysis started (PID $($proc.Id))" | Add-Content $LogFile
    return $proc
}

$codeAnalysisProc = $null
while ($true) {
    if (-not (Is-CodeAnalysisRunning)) {
        $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
        "[Watchdog $timestamp] Port 8082 not listening - starting CodeAnalysis..." | Add-Content $LogFile

        $codeAnalysisProc = Start-CodeAnalysis
        Start-Sleep -Seconds 8
    }
    Start-Sleep -Seconds $CheckSecs
}