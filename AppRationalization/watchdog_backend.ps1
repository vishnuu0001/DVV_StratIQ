# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: AppRationalization — watchdog_backend (watchdog_backend.ps1)
# Date: 2026-02-20
# ---------------------------------------------------------------------------
# StratApp Flask Backend Watchdog
# Monitors Flask on port 5000, restarts it if down.
# Runs forever - intended to be launched via scheduled task at logon.
#
# Production: uses Waitress WSGI server (multi-threaded, Windows-safe).
# Fallback: Flask dev server if Waitress is not installed.

$BackendDir   = Join-Path $PSScriptRoot 'backend'
$PythonExe    = "$BackendDir\.venv\Scripts\python.exe"
$WaitressExe  = "$BackendDir\.venv\Scripts\waitress-serve.exe"
$RunScript    = "$BackendDir\run.py"
$LogFile      = 'C:\STIQ\Strat-Aqorynth_VM_AWS\logs\flask_stderr.log'
$StdoutFile   = 'C:\STIQ\Strat-Aqorynth_VM_AWS\logs\flask_stdout.log'
$CheckSecs    = 30   # how often to check (seconds)

# Function: Is-FlaskRunning
function Is-FlaskRunning {
    $conn = Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue
    return ($null -ne $conn)
}

# Function: Start-Flask
function Start-Flask {
    $env:FLASK_DEBUG = 'false'
    $env:FLASK_ENV   = 'production'

    $psi = New-Object System.Diagnostics.ProcessStartInfo

    if (Test-Path $WaitressExe) {
        # Production: Waitress is a multi-threaded WSGI server suitable for Windows.
        # run:app refers to the `app` variable in run.py (the Flask WSGI object).
        $psi.FileName  = $WaitressExe
        $psi.Arguments = '--host=0.0.0.0 --port=5000 --threads=4 run:app'
    } else {
        # Fallback: Flask built-in dev server (install waitress for production)
        $psi.FileName  = $PythonExe
        $psi.Arguments = "`"$RunScript`""
    }

    $psi.WorkingDirectory       = $BackendDir
    $psi.UseShellExecute        = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError  = $true
    $psi.CreateNoWindow         = $true

    $proc = New-Object System.Diagnostics.Process
    $proc.StartInfo = $psi

    # Async log stdout/stderr
    $stdoutAction = { Add-Content -Path $StdoutFile -Value $Event.SourceEventArgs.Data }
    $stderrAction = { Add-Content -Path $LogFile    -Value $Event.SourceEventArgs.Data }
    Register-ObjectEvent -InputObject $proc -EventName OutputDataReceived -Action $stdoutAction | Out-Null
    Register-ObjectEvent -InputObject $proc -EventName ErrorDataReceived  -Action $stderrAction | Out-Null

    $proc.Start()      | Out-Null
    $proc.BeginOutputReadLine()
    $proc.BeginErrorReadLine()

    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    "[Watchdog $timestamp] Flask started (PID $($proc.Id))" | Add-Content $LogFile
    return $proc
}

# Main watchdog loop
$flaskProc = $null
while ($true) {
    if (-not (Is-FlaskRunning)) {
        $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
        "[Watchdog $timestamp] Port 5000 not listening - starting Flask..." | Add-Content $LogFile

        # Kill ONLY the process holding port 5000 (never kill all python - other services use python too)
        $zombie = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($zombie) { Stop-Process -Id $zombie.OwningProcess -Force -ErrorAction SilentlyContinue }
        Start-Sleep -Seconds 2

        $flaskProc = Start-Flask
        Start-Sleep -Seconds 8   # wait for Flask to bind
    }
    Start-Sleep -Seconds $CheckSecs
}
