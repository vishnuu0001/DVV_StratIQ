# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Watch-FrontendBuild.ps1 — Watch-FrontendBuild (Watch-FrontendBuild.ps1)
# Date: 2025-11-08
# ---------------------------------------------------------------------------
<#
.SYNOPSIS
    Watches all frontend src/ directories and triggers npm run build on change.

.DESCRIPTION
    Uses PowerShell FileSystemWatcher to monitor .jsx, .js, .ts, .tsx, .css,
    .json, and .html files under each frontend/src folder. Changes are debounced
    (default 2s) before the build fires to avoid triggering mid-save.

    Watches:
        CodeAnalysis\frontend\src         → npm run build  (Vite → dist/)
        Novastra-ITSM\frontend\src → npm run build  (Vite → dist/)
        Dashboard\frontend\src            → npm run build  (Vite → dist/)

.PARAMETER DebounceMs
    Milliseconds to wait after the last file-change event before triggering a
    build. Default: 2000 (2 seconds).

.PARAMETER App
    Limit watching to a single app name (e.g. CodeAnalysis, Novastra-ITSM, Dashboard).
    Leave empty to watch all supported apps.

.EXAMPLE
    .\Watch-FrontendBuild.ps1
    .\Watch-FrontendBuild.ps1 -App CodeAnalysis
    .\Watch-FrontendBuild.ps1 -DebounceMs 1000
#>
[CmdletBinding()]
param(
    [int]    $DebounceMs = 2000,
    [string] $App        = '',
    [bool]   $AutoPublish = $true
)

Set-StrictMode -Off
$ErrorActionPreference = 'Continue'

$repoRoot = Split-Path -Parent $PSCommandPath
$logFile = Join-Path $repoRoot 'Maintenance\frontend-build-watcher.log'

# -- App registry -----------------------------------------------------------------------
$allApps = @(
    @{ Name = 'AppRationalization';     SrcDir = Join-Path $repoRoot 'AppRationalization\frontend\src';     FrontendDir = Join-Path $repoRoot 'AppRationalization\frontend' }
    @{ Name = 'CodeAnalysis';         SrcDir = Join-Path $repoRoot 'CodeAnalysis\frontend\src';         FrontendDir = Join-Path $repoRoot 'CodeAnalysis\frontend' }
    @{ Name = 'InfraRationalization';  SrcDir = Join-Path $repoRoot 'InfraRationalization\frontend\src';  FrontendDir = Join-Path $repoRoot 'InfraRationalization\frontend' }
    @{ Name = 'Novastra-ITSM'; SrcDir = Join-Path $repoRoot 'Novastra-ITSM\frontend\src'; FrontendDir = Join-Path $repoRoot 'Novastra-ITSM\frontend' }
    @{ Name = 'Dashboard';            SrcDir = Join-Path $repoRoot 'Dashboard\frontend\src';            FrontendDir = Join-Path $repoRoot 'Dashboard\frontend' }
    @{ Name = 'SSDLC';                SrcDir = Join-Path $repoRoot 'SSDLC_Process_Assessment\frontend\src'; FrontendDir = Join-Path $repoRoot 'SSDLC_Process_Assessment\frontend' }
    @{ Name = 'Modernization';        SrcDir = Join-Path $repoRoot 'Modernization\frontend\src';        FrontendDir = Join-Path $repoRoot 'Modernization\frontend' }
    @{ Name = 'LabRobot';             SrcDir = Join-Path $repoRoot 'LabRobot\frontend\src';             FrontendDir = Join-Path $repoRoot 'LabRobot\frontend' }
    @{ Name = 'OpportunityTracker';   SrcDir = Join-Path $repoRoot 'OpportunityTracker\frontend\src';   FrontendDir = Join-Path $repoRoot 'OpportunityTracker\frontend' }
    @{ Name = 'AI_Reman_Core';        SrcDir = Join-Path $repoRoot 'AI_Reman_Core\src';                  FrontendDir = Join-Path $repoRoot 'AI_Reman_Core' }
    @{ Name = 'AI_Vehicle_Loan';      SrcDir = Join-Path $repoRoot 'AI_Vehicle_Loan\frontend\src';      FrontendDir = Join-Path $repoRoot 'AI_Vehicle_Loan\frontend' }
    @{ Name = 'MicrositeDataAnalysis';SrcDir = Join-Path $repoRoot 'Microsite_Data_Analysis\src';          FrontendDir = Join-Path $repoRoot 'Microsite_Data_Analysis' }
    @{ Name = 'SupplyChain';          SrcDir = Join-Path $repoRoot 'supply-chain-disruption-manager\apps\web-ui\src'; FrontendDir = Join-Path $repoRoot 'supply-chain-disruption-manager\apps\web-ui' }
)

$apps = if ($App) {
    $allApps | Where-Object { $_.Name -eq $App }
} else {
    $allApps
}

$apps = $apps | Where-Object { Test-Path -LiteralPath $_.SrcDir }

if (-not $apps) {
    Write-Host 'No matching frontend src/ directories found.' -ForegroundColor Red
    exit 1
}

# -- Shared state: one debounce timer per app ------------------------------------------
# Key = app name, value = [datetime] last-change time
$script:LastChange  = [hashtable]::Synchronized(@{})
$script:BuildQueued = @{}
$script:Building    = @{}

foreach ($a in $apps) {
    $script:LastChange[$a.Name]  = [datetime]::MinValue
    $script:BuildQueued[$a.Name] = $false
    $script:Building[$a.Name]    = $false
}

# Function: Write-Log
function Write-Log {
    param([string]$AppName, [string]$Msg, [string]$Color = 'Cyan')
    $ts = Get-Date -Format 'HH:mm:ss'
    $line = "[$ts] [$AppName] $Msg"
    Write-Host $line -ForegroundColor $Color
    Add-Content -LiteralPath $logFile -Value "$(Get-Date -Format 'yyyy-MM-dd') $line"
}

# Function: Invoke-Build
function Invoke-Build {
    param([hashtable]$AppEntry)
    $name = $AppEntry.Name
    $dir  = $AppEntry.FrontendDir

    if ($script:Building[$name]) {
        Write-Log $name 'Build already running — queuing next trigger.' 'Yellow'
        $script:BuildQueued[$name] = $true
        return
    }

    $script:Building[$name] = $true
    Write-Log $name 'Building…' 'Green'

    Push-Location -LiteralPath $dir
    try {
        npm run build 2>&1 | ForEach-Object { Write-Log $name $_ 'DarkGray' }
        if ($LASTEXITCODE -eq 0) {
            Write-Log $name 'Build succeeded.' 'Green'
            if ($AutoPublish) {
                $syncScript = Join-Path $repoRoot 'Maintenance\Auto-Git-Sync.ps1'
                Write-Log $name 'Starting guarded Git sync and production publish.' 'Cyan'
                & $syncScript 2>&1 | ForEach-Object { Write-Log $name $_ 'DarkGray' }
                if ($LASTEXITCODE -ne 0) {
                    Write-Log $name "Auto-publish failed (exit $LASTEXITCODE); scheduled sync will retry." 'Red'
                }
            }
        } else {
            Write-Log $name "Build failed (exit $LASTEXITCODE)." 'Red'
        }
    } finally {
        Pop-Location
        $script:Building[$name] = $false

        if ($script:BuildQueued[$name]) {
            $script:BuildQueued[$name] = $false
            Write-Log $name 'Running queued build…' 'Yellow'
            Invoke-Build $AppEntry
        }
    }
}

# -- Create FileSystemWatcher for each app ---------------------------------------------
$watchers = @()

foreach ($appEntry in $apps) {
    $watcher = New-Object System.IO.FileSystemWatcher
    $watcher.Path                = $appEntry.SrcDir
    $watcher.IncludeSubdirectories = $true
    $watcher.NotifyFilter        = [System.IO.NotifyFilters]::LastWrite -bor [System.IO.NotifyFilters]::FileName
    $watcher.Filter              = '*.*'
    $watcher.EnableRaisingEvents = $false   # enable after registering handlers

    $appName = $appEntry.Name
    $eventState = @{
        Name       = $appName
        LastChange = $script:LastChange
    }

    $onChange = {
        param($src, $e)
        # Filter to relevant extensions only
        $ext = [System.IO.Path]::GetExtension($e.FullPath).ToLower()
        if ($ext -notin @('.jsx','.js','.ts','.tsx','.css','.scss','.json','.html','.svg','.png')) {
            return
        }
        $event.MessageData.LastChange[$event.MessageData.Name] = [datetime]::UtcNow
    }

    Register-ObjectEvent -InputObject $watcher -EventName Changed -MessageData $eventState -Action $onChange | Out-Null
    Register-ObjectEvent -InputObject $watcher -EventName Created -MessageData $eventState -Action $onChange | Out-Null
    Register-ObjectEvent -InputObject $watcher -EventName Renamed -MessageData $eventState -Action $onChange | Out-Null
    Register-ObjectEvent -InputObject $watcher -EventName Deleted -MessageData $eventState -Action $onChange | Out-Null

    $watcher.EnableRaisingEvents = $true
    $watchers += $watcher

    Write-Log $appEntry.Name "Watching $($appEntry.SrcDir)" 'Cyan'
}

Write-Host ''
Write-Host 'Frontend build watcher running. Press Ctrl+C to stop.' -ForegroundColor Yellow
Write-Host "Debounce: ${DebounceMs}ms - saves are batched before building." -ForegroundColor DarkGray
Write-Host ''

# -- Main poll loop ---------------------------------------------------------------------
try {
    while ($true) {
        foreach ($appEntry in $apps) {
            $name = $appEntry.Name
            $last = $script:LastChange[$name]

            if ($last -eq [datetime]::MinValue) { continue }

            $elapsed = ([datetime]::UtcNow - $last).TotalMilliseconds
            if ($elapsed -ge $DebounceMs -and -not $script:Building[$name]) {
                # Reset so we don't re-trigger until next change
                $script:LastChange[$name] = [datetime]::MinValue
                Invoke-Build $appEntry
            }
        }
        Start-Sleep -Milliseconds 250
    }
} finally {
    foreach ($w in $watchers) {
        $w.EnableRaisingEvents = $false
        $w.Dispose()
    }
    Get-EventSubscriber | Unregister-Event -ErrorAction SilentlyContinue
    Write-Host 'Watchers stopped.' -ForegroundColor Yellow
}
