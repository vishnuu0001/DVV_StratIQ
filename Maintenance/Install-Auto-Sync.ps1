# ---------------------------------------------------------------------------
# Installs the production watchdog and Git/publish loop with separate identities.
# Must be run from an elevated Windows PowerShell session.
# ---------------------------------------------------------------------------
[CmdletBinding()]
param(
    [string]$RepoRoot = ''
)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = Split-Path -Parent $PSScriptRoot
}
$logPath = Join-Path $RepoRoot '.tmp\auto-sync-install.log'
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $logPath) | Out-Null
Start-Transcript -Path $logPath -Force | Out-Null
trap {
    Write-Error "Auto-sync installation failed: $($_.Exception.Message)"
    Stop-Transcript | Out-Null
    exit 1
}

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Administrator privileges are required.'
}

$watchdogPath = Join-Path $RepoRoot 'watchdog_all_backends.ps1'
$syncLoopPath = Join-Path $RepoRoot 'Maintenance\Auto-Git-Sync-Loop.ps1'
foreach ($path in @($watchdogPath, $syncLoopPath)) {
    if (-not (Test-Path -LiteralPath $path)) { throw "Required script not found: $path" }
}

$unqualifiedUser = [Environment]::UserName
$userDomain = [Environment]::UserDomainName
$interactiveUser = if ($userDomain) { "$userDomain\$unqualifiedUser" } else { $unqualifiedUser }
$powerShell = Join-Path $PSHOME 'powershell.exe'
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -RestartCount 10 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit ([TimeSpan]::Zero)

$watchdogAction = New-ScheduledTaskAction -Execute $powerShell `
    -Argument "-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File `"$watchdogPath`""
$watchdogPrincipal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' `
    -LogonType ServiceAccount -RunLevel Highest

# A previously registered task can leave its long-lived PowerShell child
# detached after the task definition is replaced. That orphan retains the
# global watchdog mutex and causes the new SYSTEM task to exit successfully
# without monitoring anything. Stop only watchdog script hosts; backend child
# processes remain alive and are adopted by the replacement watchdog.
Stop-ScheduledTask -TaskName 'StratIQ-Master-Watchdog' -ErrorAction SilentlyContinue
$staleWatchdogs = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object {
        $_.ProcessId -ne $PID -and
        $_.Name -eq 'powershell.exe' -and
        $_.CommandLine -and
        $_.CommandLine.Contains($watchdogPath)
    }
foreach ($process in $staleWatchdogs) {
    Stop-Process -Id $process.ProcessId -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 2

Register-ScheduledTask -TaskName 'StratIQ-Master-Watchdog' `
    -Action $watchdogAction -Trigger (New-ScheduledTaskTrigger -AtStartup) `
    -Principal $watchdogPrincipal -Settings $settings -Force | Out-Null

$syncAction = New-ScheduledTaskAction -Execute $powerShell `
    -Argument "-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File `"$syncLoopPath`""
$syncPrincipal = New-ScheduledTaskPrincipal -UserId $interactiveUser `
    -LogonType Interactive -RunLevel Limited
$syncTriggers = @(
    (New-ScheduledTaskTrigger -AtLogOn -User $interactiveUser),
    (New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1))
)
Register-ScheduledTask -TaskName 'StratIQ-Auto-Git-Sync-And-Publish' `
    -Action $syncAction -Trigger $syncTriggers `
    -Principal $syncPrincipal -Settings $settings -Force | Out-Null

Start-ScheduledTask -TaskName 'StratIQ-Master-Watchdog'
Start-ScheduledTask -TaskName 'StratIQ-Auto-Git-Sync-And-Publish'
Start-Sleep -Seconds 3

$watchdog = Get-ScheduledTask -TaskName 'StratIQ-Master-Watchdog'
$sync = Get-ScheduledTask -TaskName 'StratIQ-Auto-Git-Sync-And-Publish'
[pscustomobject]@{
    WatchdogTask = $watchdog.TaskName
    WatchdogIdentity = $watchdog.Principal.UserId
    WatchdogState = $watchdog.State
    SyncTask = $sync.TaskName
    SyncIdentity = $sync.Principal.UserId
    SyncState = $sync.State
    IntervalSeconds = 300
} | Format-List
Stop-Transcript | Out-Null
