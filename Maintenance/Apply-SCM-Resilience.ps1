# ---------------------------------------------------------------------------
# Applies the IIS ARR streaming fix and installs the backend watchdog.
# Must be run from an elevated Windows PowerShell session.
# ---------------------------------------------------------------------------
[CmdletBinding()]
param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'
$transcriptPath = Join-Path $RepoRoot '.tmp\scm-resilience-admin.log'
$null = New-Item -ItemType Directory -Path (Split-Path $transcriptPath) -Force
Start-Transcript -Path $transcriptPath -Force | Out-Null

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Administrator privileges are required.'
}

Import-Module WebAdministration -ErrorAction Stop
$proxy = Get-WebConfiguration -Filter 'system.webServer/proxy' -PSPath 'IIS:\'
if ($null -eq $proxy) {
    throw 'IIS ARR proxy configuration is unavailable.'
}

Set-WebConfigurationProperty `
    -Filter 'system.webServer/proxy' `
    -PSPath 'IIS:\' `
    -Name 'enabled' `
    -Value $true
Set-WebConfigurationProperty `
    -Filter 'system.webServer/proxy' `
    -PSPath 'IIS:\' `
    -Name 'bufferChunkedResponses' `
    -Value $false

$watchdogPath = Join-Path $RepoRoot 'watchdog_all_backends.ps1'
if (-not (Test-Path -LiteralPath $watchdogPath)) {
    throw "Watchdog not found: $watchdogPath"
}

$taskName = 'Strat-Aqorynth-Master-Watchdog'
$action = New-ScheduledTaskAction `
    -Execute (Join-Path $PSHOME 'powershell.exe') `
    -Argument "-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File `"$watchdogPath`""
$trigger = New-ScheduledTaskTrigger -AtStartup
$taskPrincipal = New-ScheduledTaskPrincipal `
    -UserId 'SYSTEM' `
    -LogonType ServiceAccount `
    -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -RestartCount 10 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit ([TimeSpan]::Zero)

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Principal $taskPrincipal `
    -Settings $settings `
    -Force | Out-Null
Start-ScheduledTask -TaskName $taskName
Start-Sleep -Seconds 5

$configured = Get-WebConfiguration -Filter 'system.webServer/proxy' -PSPath 'IIS:\'
$task = Get-ScheduledTask -TaskName $taskName

[pscustomobject]@{
    ComputerName           = $env:COMPUTERNAME
    ArrEnabled             = [bool]$configured.enabled
    BufferChunkedResponses = [bool]$configured.bufferChunkedResponses
    WatchdogTask           = $task.TaskName
    WatchdogState          = $task.State
} | Format-List

if (-not [bool]$configured.enabled -or [bool]$configured.bufferChunkedResponses) {
    throw 'ARR configuration verification failed.'
}

Stop-Transcript | Out-Null
