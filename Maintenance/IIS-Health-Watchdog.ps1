# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Maintenance — IIS-Health-Watchdog (IIS-Health-Watchdog.ps1)
# Date: 2026-01-04
# ---------------------------------------------------------------------------
<#
.SYNOPSIS
  Checks that the StratIQ IIS site is actually responding, and restarts the
  StratIQ-Project app pool if it isn't.

.DESCRIPTION
  Root cause this addresses: the app pool can go fully unresponsive (worker
  process alive but not serving any requests, seen as a burst of stuck
  CLOSE_WAIT connections on port 8090) even with startMode=AlwaysRunning and
  idleTimeout=0 set — those two settings only prevent *idle*-triggered
  shutdown, not an outright hang. `Restart-WebAppPool` fixes it immediately
  once detected; this task automates the detection + restart.
#>

$ErrorActionPreference = 'Continue'
$LogFile  = Join-Path $PSScriptRoot 'iis-health-watchdog.log'
$CheckUrl = 'http://localhost:8090/'
$AppPool  = 'StratIQ-Project'

# Function: Write-Log
function Write-Log {
    param([string]$Message)
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | $Message"
    Add-Content -Path $LogFile -Value $line
    Write-Host $line
}

try {
    $resp = Invoke-WebRequest -Uri $CheckUrl -TimeoutSec 15 -UseBasicParsing -ErrorAction Stop
    if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 400) {
        Write-Log "OK: $CheckUrl responded $($resp.StatusCode)"
    } else {
        Write-Log "WARNING: $CheckUrl responded $($resp.StatusCode) - restarting app pool"
        Import-Module WebAdministration
        Restart-WebAppPool -Name $AppPool
        Write-Log "Restarted app pool '$AppPool'"
    }
} catch {
    Write-Log "FAIL: $CheckUrl did not respond ($($_.Exception.Message)) - restarting app pool"
    Import-Module WebAdministration
    Restart-WebAppPool -Name $AppPool
    Write-Log "Restarted app pool '$AppPool'"
}

# Keep this script's own log from growing unbounded
if (Test-Path $LogFile) {
    $lines = Get-Content $LogFile
    if ($lines.Count -gt 2000) {
        $lines[-2000..-1] | Set-Content $LogFile
    }
}
