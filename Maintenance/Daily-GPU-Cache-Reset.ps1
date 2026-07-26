# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Maintenance — Daily-GPU-Cache-Reset (Daily-GPU-Cache-Reset.ps1)
# Date: 2026-01-16
# ---------------------------------------------------------------------------
<#
.SYNOPSIS
  Daily maintenance: resets Ollama/GPU state and trims old rotated log files.

.DESCRIPTION
  Root cause this addresses: Ollama's inference subprocess (llama-server.exe) can
  detach from its parent "ollama"/"ollama app" processes and get stuck holding GPU
  memory after long uptime, silently hanging every LLM call platform-wide until a
  request times out. Killing only the visible ollama/ollama app processes does NOT
  reliably clear this — the orphaned llama-server.exe must be killed explicitly.
  See D:\StartIQ\supply-chain-disruption-manager\deployment.md for the incident this
  was diagnosed from.

  Also trims old timestamped log-rotation files under D:\StartIQ\logs (the ones with
  a -YYYYMMDDTHHMMSS suffix from the watchdog/service launchers) older than 7 days.
  Current/active logs (no timestamp suffix) are never touched.
#>

$ErrorActionPreference = 'Continue'
$RepoRoot = Split-Path -Parent $PSScriptRoot
$logFile = Join-Path $PSScriptRoot 'daily-maintenance.log'
$ollamaAppExe = "C:\Users\stratdev\AppData\Local\Programs\Ollama\ollama app.exe"
$logRetentionDays = 7
$rotatedLogDirs = @((Join-Path $RepoRoot 'Data\logs'))

# Function: Write-Log
function Write-Log {
    param([string]$Message)
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | $Message"
    Add-Content -Path $logFile -Value $line
    Write-Host $line
}

Write-Log "=== Daily maintenance starting ==="

# ── 1. Reset Ollama / GPU ──────────────────────────────────────────────────
try {
    $before = (Get-Process -Name "ollama*", "llama-server" -ErrorAction SilentlyContinue)
    if ($before) {
        Write-Log "Stopping $($before.Count) Ollama-related process(es): $($before.ProcessName -join ', ')"
        $before | Stop-Process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 5
    } else {
        Write-Log "No Ollama processes running before reset."
    }

    $stillRunning = Get-Process -Name "ollama*", "llama-server" -ErrorAction SilentlyContinue
    if ($stillRunning) {
        Write-Log "WARNING: $($stillRunning.Count) process(es) survived Stop-Process: $($stillRunning.ProcessName -join ', ')"
    }

    Start-Process -FilePath $ollamaAppExe
    Start-Sleep -Seconds 10

    try {
        $tags = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 15
        Write-Log "Ollama responded after restart. Models loaded: $($tags.models.Count)"
    } catch {
        Write-Log "WARNING: Ollama did not respond to /api/tags after restart: $($_.Exception.Message)"
    }
} catch {
    Write-Log "ERROR during Ollama reset: $($_.Exception.Message)"
}

# ── 2. Trim old rotated log files ──────────────────────────────────────────
$cutoff = (Get-Date).AddDays(-$logRetentionDays)
foreach ($dir in $rotatedLogDirs) {
    if (-not (Test-Path $dir)) { continue }
    $old = Get-ChildItem -Path $dir -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match '-\d{8}T\d{6}' -and $_.LastWriteTime -lt $cutoff }
    if ($old) {
        $totalSize = ($old | Measure-Object -Property Length -Sum).Sum
        Write-Log "Removing $($old.Count) rotated log file(s) older than $logRetentionDays days from $dir ($([math]::Round($totalSize/1KB,1)) KB)"
        $old | Remove-Item -Force -ErrorAction SilentlyContinue
    } else {
        Write-Log "No rotated log files older than $logRetentionDays days in $dir"
    }
}

# Keep this script's own log from growing unbounded too
if (Test-Path $logFile) {
    $lines = Get-Content $logFile
    if ($lines.Count -gt 2000) {
        $lines[-2000..-1] | Set-Content $logFile
    }
}

Write-Log "=== Daily maintenance complete ==="
