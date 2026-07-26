# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Maintenance — Auto-Git-Sync-Loop (Auto-Git-Sync-Loop.ps1)
# Date: 2026-07-24
# ---------------------------------------------------------------------------
<#
.SYNOPSIS
  Persistent-loop wrapper around Auto-Git-Sync.ps1.

.DESCRIPTION
  StratIQ-Auto-Git-Sync (a repeating Task Scheduler trigger) has been
  intermittently failing to actually launch a new process on its 5-minute
  trigger (Task Scheduler reports LastTaskResult=0x800710E0 "already running"
  even with no real process alive - a stuck internal state, root cause
  undiagnosed since Microsoft-Windows-TaskScheduler/Operational logging is
  disabled on this box). This script sidesteps that unreliable trigger
  mechanism entirely: it is itself launched ONCE (by a Task Scheduler logon
  trigger, same pattern as watchdog_all_backends.ps1) and stays resident,
  invoking Auto-Git-Sync.ps1 on the same 5-minute cadence from inside a
  single long-lived process instead of relying on repeated fresh launches.
#>
$ErrorActionPreference = 'Continue'
$ScriptPath = Join-Path $PSScriptRoot 'Auto-Git-Sync.ps1'
$IntervalSeconds = 300

while ($true) {
    try {
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptPath
    } catch {
        Write-Host "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | Auto-Git-Sync-Loop: invocation error - $($_.Exception.Message)"
    }
    Start-Sleep -Seconds $IntervalSeconds
}
