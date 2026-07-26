# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Modernization — Sync-ProductionBuild (Sync-ProductionBuild.ps1)
# Date: 2025-10-07
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Modernization frontend production-build synchronizer.
# Performs an initial build and then keeps frontend/dist synchronized with
# changes under src/, public/, index.html and vite.config.js.
# ---------------------------------------------------------------------------
[CmdletBinding()]
param(
    [switch]$Once,
    [int]$DebounceMs = 1500
)

$ErrorActionPreference = 'Stop'
$frontendDir = Join-Path $PSScriptRoot 'frontend'
$distIndex = Join-Path $frontendDir 'dist\index.html'
$logDir = Join-Path $PSScriptRoot 'data\logs'
$logFile = Join-Path $logDir 'frontend-production-sync.log'
$watchPaths = @(
    (Join-Path $frontendDir 'src'),
    (Join-Path $frontendDir 'public'),
    $frontendDir
)

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

# Function: Write-SyncLog
function Write-SyncLog {
    param([string]$Message)
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message"
    Write-Host $line
    Add-Content -LiteralPath $logFile -Value $line
}

# Function: Ensure-Dependencies
function Ensure-Dependencies {
    if (Test-Path -LiteralPath (Join-Path $frontendDir 'node_modules\.bin\vite.cmd')) { return }
    Write-SyncLog 'Frontend dependencies are missing; running npm ci.'
    Push-Location -LiteralPath $frontendDir
    try {
        & npm.cmd ci --include=dev
        if ($LASTEXITCODE -ne 0) { throw "npm ci failed with exit code $LASTEXITCODE" }
    } finally { Pop-Location }
}

# Function: Invoke-ProductionBuild
function Invoke-ProductionBuild {
    Ensure-Dependencies
    Write-SyncLog 'Synchronizing Modernization production build.'
    Push-Location -LiteralPath $frontendDir
    try {
        & npm.cmd run build:production
        if ($LASTEXITCODE -ne 0) { throw "Production build failed with exit code $LASTEXITCODE" }
        if (-not (Test-Path -LiteralPath $distIndex)) { throw 'Build completed without producing dist/index.html' }
        Write-SyncLog 'Production build synchronized successfully.'
    } finally { Pop-Location }
}

Invoke-ProductionBuild
if ($Once) { exit 0 }

$state = [hashtable]::Synchronized(@{ LastChange = [datetime]::MinValue })
$watchers = @()
$eventAction = {
    param($sender, $eventArgs)
    $fullPath = $eventArgs.FullPath
    if ($fullPath -match '[\\/](dist|node_modules)[\\/]') { return }
    $name = [System.IO.Path]::GetFileName($fullPath)
    $extension = [System.IO.Path]::GetExtension($fullPath).ToLowerInvariant()
    if ($extension -notin @('.jsx', '.js', '.ts', '.tsx', '.css', '.scss', '.json', '.html', '.svg', '.png') -and
        $name -notin @('vite.config.js', 'package.json', 'package-lock.json')) { return }
    $event.MessageData.LastChange = [datetime]::UtcNow
}

foreach ($path in $watchPaths) {
    if (-not (Test-Path -LiteralPath $path)) { continue }
    $watcher = New-Object System.IO.FileSystemWatcher
    $watcher.Path = $path
    $watcher.IncludeSubdirectories = $true
    $watcher.Filter = '*.*'
    $watcher.NotifyFilter = [System.IO.NotifyFilters]::LastWrite -bor [System.IO.NotifyFilters]::FileName
    Register-ObjectEvent $watcher Changed -MessageData $state -Action $eventAction | Out-Null
    Register-ObjectEvent $watcher Created -MessageData $state -Action $eventAction | Out-Null
    Register-ObjectEvent $watcher Deleted -MessageData $state -Action $eventAction | Out-Null
    Register-ObjectEvent $watcher Renamed -MessageData $state -Action $eventAction | Out-Null
    $watcher.EnableRaisingEvents = $true
    $watchers += $watcher
}

Write-SyncLog 'Watching frontend source and public assets for production synchronization.'
try {
    while ($true) {
        if ($state.LastChange -ne [datetime]::MinValue -and
            ([datetime]::UtcNow - $state.LastChange).TotalMilliseconds -ge $DebounceMs) {
            $state.LastChange = [datetime]::MinValue
            try { Invoke-ProductionBuild } catch { Write-SyncLog "ERROR: $($_.Exception.Message)" }
        }
        Start-Sleep -Milliseconds 250
    }
} finally {
    foreach ($watcher in $watchers) { $watcher.EnableRaisingEvents = $false; $watcher.Dispose() }
    Get-EventSubscriber | Unregister-Event -ErrorAction SilentlyContinue
}
