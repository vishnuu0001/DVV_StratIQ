# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Maintenance — Publish-Production (Publish-Production.ps1)
# Date: 2025-12-10
# ---------------------------------------------------------------------------
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string[]]$ChangedFiles
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
$LogFile = Join-Path $PSScriptRoot 'production-publish.log'

# Function: Write-PublishLog
function Write-PublishLog {
    param([string]$Message)
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | $Message"
    Add-Content -LiteralPath $LogFile -Value $line
    Write-Host $line
}

# Function: Test-ChangedPath
function Test-ChangedPath {
    param([string]$Prefix)
    return [bool]($ChangedFiles | Where-Object {
        $_.Replace('\', '/').StartsWith($Prefix, [StringComparison]::OrdinalIgnoreCase)
    } | Select-Object -First 1)
}

# Function: Sync-NovastraPortalAuthSecret
function Sync-NovastraPortalAuthSecret {
    $portalEnvPath = Join-Path $RepoRoot 'AppRationalization\backend\.env'
    $novastraEnvPath = Join-Path $RepoRoot 'Novastra-ITSM\.env'
    if (-not (Test-Path -LiteralPath $portalEnvPath)) {
        Write-PublishLog "Portal .env not present; retaining the watchdog/service-managed Novastra SSO secret."
        return
    }
    if (-not (Test-Path -LiteralPath $novastraEnvPath)) {
        Write-PublishLog "Novastra .env not present; retaining the watchdog/service-managed SSO secret."
        return
    }

    $portalSecretLine = Get-Content -LiteralPath $portalEnvPath |
        Where-Object { $_ -match '^AUTH_TOKEN_SECRET=' } |
        Select-Object -First 1
    if (-not $portalSecretLine) {
        throw 'AUTH_TOKEN_SECRET is missing from the portal environment.'
    }

    $portalSecret = $portalSecretLine.Substring('AUTH_TOKEN_SECRET='.Length)
    if ([string]::IsNullOrWhiteSpace($portalSecret)) {
        throw 'AUTH_TOKEN_SECRET is empty in the portal environment.'
    }

    $novastraLines = @(Get-Content -LiteralPath $novastraEnvPath)
    $setting = "PORTAL_AUTH_TOKEN_SECRET=$portalSecret"
    $found = $false
    for ($index = 0; $index -lt $novastraLines.Count; $index++) {
        if ($novastraLines[$index] -match '^PORTAL_AUTH_TOKEN_SECRET=') {
            $novastraLines[$index] = $setting
            $found = $true
        }
    }
    if (-not $found) {
        $novastraLines += $setting
    }
    Set-Content -LiteralPath $novastraEnvPath -Value $novastraLines -Encoding UTF8
    Write-PublishLog 'Synchronized the Novastra portal SSO verification secret.'
}

# Function: Wait-BackendPort
function Wait-BackendPort {
    param(
        [string]$Name,
        [int]$Port,
        # 50s was observed too tight under sustained load (six frontends rebuilding
        # + nine backends restarting every cycle during a large backlog catch-up on
        # 2026-07-24) - Dashboard alone needed ~80s several times, causing the whole
        # publish to fail and retry the same growing backlog every 5 minutes for ~2h.
        [int]$TimeoutSeconds = 120
    )
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do {
        $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
            Select-Object -First 1
        if ($listener) {
            Write-PublishLog "$Name is listening on port $Port after restart."
            return
        }
        Start-Sleep -Milliseconds 500
    } while ((Get-Date) -lt $deadline)
    throw "$Name did not resume listening on port $Port within $TimeoutSeconds seconds."
}

# Function: Invoke-TraceForgeMigrations
function Invoke-TraceForgeMigrations {
    $directory = Join-Path $RepoRoot 'TraceForge\api'
    $python = Join-Path $directory '.venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $python)) {
        throw "TraceForge Python was not found at $python"
    }

    Write-PublishLog 'Applying TraceForge database migrations.'
    Push-Location $directory
    $prevEap = $ErrorActionPreference
    try {
        # Native commands routinely write informational/warning text to stderr; under
        # ErrorActionPreference='Stop' PowerShell 5.1 treats each such line as a
        # terminating NativeCommandError before the real exit-code check below even
        # runs. Rely solely on $LASTEXITCODE for pass/fail, same as everywhere else
        # in this script.
        $ErrorActionPreference = 'Continue'
        & $python -m alembic upgrade head
        $ErrorActionPreference = $prevEap
        if ($LASTEXITCODE -ne 0) {
            throw "TraceForge database migration failed with exit code $LASTEXITCODE"
        }
    } finally {
        $ErrorActionPreference = $prevEap
        Pop-Location
    }
    Write-PublishLog 'TraceForge database migrations applied successfully.'
}

$frontends = @(
    @{ Prefix = 'AppRationalization/frontend/'; Directory = 'AppRationalization/frontend'; Name = 'AppRationalization' },
    @{ Prefix = 'CodeAnalysis/frontend/'; Directory = 'CodeAnalysis/frontend'; Name = 'CodeAnalysis' },
    @{ Prefix = 'InfraRationalization/frontend/'; Directory = 'InfraRationalization/frontend'; Name = 'InfraRationalization' },
    @{ Prefix = 'Novastra-ITSM/frontend/'; Directory = 'Novastra-ITSM/frontend'; Name = 'Novastra-ITSM' },
    @{ Prefix = 'Dashboard/frontend/'; Directory = 'Dashboard/frontend'; Name = 'Dashboard' },
    @{ Prefix = 'SSDLC_Process_Assessment/frontend/'; Directory = 'SSDLC_Process_Assessment/frontend'; Name = 'SSDLC' },
    @{ Prefix = 'Modernization/frontend/'; Directory = 'Modernization/frontend'; Name = 'Modernization' },
    @{ Prefix = 'LabRobot/frontend/'; Directory = 'LabRobot/frontend'; Name = 'LabRobot' },
    @{ Prefix = 'OpportunityTracker/frontend/'; Directory = 'OpportunityTracker/frontend'; Name = 'OpportunityTracker' },
    @{ Prefix = 'AI_Reman_Core/'; Directory = 'AI_Reman_Core'; Name = 'AI_Reman_Core' },
    @{ Prefix = 'AI_Vehicle_Loan/frontend/'; Directory = 'AI_Vehicle_Loan/frontend'; Name = 'AI_Vehicle_Loan' },
    @{ Prefix = 'Microsite_Data_Analysis/'; Directory = 'Microsite_Data_Analysis'; Name = 'MicrositeDataAnalysis' },
    @{ Prefix = 'supply-chain-disruption-manager/apps/web-ui/'; Directory = 'supply-chain-disruption-manager/apps/web-ui'; Name = 'SupplyChain' },
    @{ Prefix = 'TraceForge/ui/'; Directory = 'TraceForge/ui'; Name = 'TraceForge' }
)

$backends = @(
    @{ Prefix = 'AppRationalization/backend/'; Name = 'AppRationalization'; Port = 5001 },
    @{ Prefix = 'CodeAnalysis/'; Name = 'CodeAnalysis'; Port = 8082 },
    @{ Prefix = 'InfraRationalization/'; Name = 'InfraRationalization'; Port = 8083 },
    @{ Prefix = 'Modernization/'; Name = 'Modernization'; Port = 8084 },
    @{ Prefix = 'Novastra-ITSM/backend/'; Name = 'Novastra-ITSM'; Port = 8086 },
    @{ Prefix = 'Dashboard/backend/'; Name = 'Dashboard'; Port = 8087 },
    @{ Prefix = 'SSDLC_Process_Assessment/backend/'; Name = 'SSDLC'; Port = 8091 },
    @{ Prefix = 'OpportunityTracker/backend/'; Name = 'OpportunityTracker'; Port = 8092 },
    @{ Prefix = 'LabRobot/backend/'; Name = 'LabRobot'; Port = 8000 },
    @{ Prefix = 'AI_Reman_Core/backend/'; Name = 'AI_Reman_Core'; Port = 8093 },
    @{ Prefix = 'AI_Vehicle_Loan/'; Name = 'AI_Vehicle_Loan'; Port = 8094 },
    @{ Prefix = 'TraceForge/api/'; Name = 'TraceForge'; Port = 8095 }
)

if (Test-ChangedPath 'Novastra-ITSM/backend/') {
    Sync-NovastraPortalAuthSecret
}

$builtAny = $false
foreach ($frontend in $frontends) {
    if (-not (Test-ChangedPath $frontend.Prefix)) { continue }
    $directory = Join-Path $RepoRoot $frontend.Directory
    if (-not (Test-Path -LiteralPath (Join-Path $directory 'package.json'))) { continue }
    Write-PublishLog "Building $($frontend.Name)."
    Push-Location $directory
    $prevEap = $ErrorActionPreference
    try {
        # See Invoke-TraceForgeMigrations for why this must not run under 'Stop' —
        # Vite's own build warnings (e.g. chunk-size) go to stderr and would otherwise
        # abort the build before the real $LASTEXITCODE check below runs.
        $ErrorActionPreference = 'Continue'
        & npm run build
        $ErrorActionPreference = $prevEap
        if ($LASTEXITCODE -ne 0) { throw "$($frontend.Name) build failed with exit code $LASTEXITCODE" }
        $builtAny = $true
        Write-PublishLog "Built $($frontend.Name) successfully."
    } finally {
        $ErrorActionPreference = $prevEap
        Pop-Location
    }
}

$restartTargets = @()
foreach ($backend in $backends) {
    if (-not (Test-ChangedPath $backend.Prefix)) { continue }
    $restartTargets += $backend

    # waitress-serve on Windows is a launcher -> venv Python -> system Python
    # process tree. Killing only the deepest listener can leave the stale launchers
    # alive, so AppRationalization must replace every member of that tree.
    if ($backend.Name -eq 'AppRationalization') {
        try {
            $waitressProcesses = Get-CimInstance Win32_Process -ErrorAction Stop | Where-Object {
                $_.CommandLine -like '*--port=5001*run:app*'
            }
            foreach ($process in $waitressProcesses) {
                Write-PublishLog "Restarting AppRationalization process PID $($process.ProcessId); watchdog will restore it."
                Stop-Process -Id $process.ProcessId -Force -ErrorAction SilentlyContinue
            }
            if (-not $waitressProcesses) {
                Write-PublishLog 'AppRationalization is not running; watchdog will start it.'
            }
        } catch {
            Write-PublishLog "WARNING: Could not restart AppRationalization process tree: $($_.Exception.Message)"
        }
        continue
    }

    $listener = Get-NetTCPConnection -LocalPort $backend.Port -State Listen -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($listener) {
        Write-PublishLog "Restarting $($backend.Name) on port $($backend.Port)."
        Stop-Process -Id $listener.OwningProcess -Force
    } else {
        Write-PublishLog "$($backend.Name) is not listening on port $($backend.Port); watchdog will start it."
    }

    if ($backend.Name -eq 'TraceForge') {
        Invoke-TraceForgeMigrations
        # The master watchdog is the single production process owner and injects
        # the same AUTH_TOKEN_SECRET used by the portal. Starting uvicorn here
        # would load TraceForge/api/.env instead and reject valid SSO tokens.
        Write-PublishLog 'TraceForge stopped; watchdog will restore it with the shared portal authentication environment.'
    }
}

foreach ($backend in $restartTargets) {
    Wait-BackendPort -Name $backend.Name -Port $backend.Port
}

# TraceForge's Arq worker has no listening port. Restart it only for code imported
# by the worker; router/schema-only changes need an API restart but must not abort a
# long extraction that is already running.
$traceForgeWorkerPrefixes = @(
    'TraceForge/api/traceforge/workers/',
    'TraceForge/api/traceforge/agents/',
    'TraceForge/api/traceforge/llm/',
    'TraceForge/api/traceforge/indexing/',
    'TraceForge/api/traceforge/parsing/',
    'TraceForge/api/traceforge/connectors/',
    'TraceForge/api/traceforge/db/'
)
$restartTraceForgeWorker = (Test-ChangedPath 'TraceForge/api/traceforge/config.py') -or
    (Test-ChangedPath 'TraceForge/api/traceforge/orchestration/gates.py') -or
    [bool]($traceForgeWorkerPrefixes | Where-Object { Test-ChangedPath $_ } | Select-Object -First 1)
if ($restartTraceForgeWorker) {
    try {
        $workers = Get-CimInstance Win32_Process -ErrorAction Stop | Where-Object {
            $_.CommandLine -like '*traceforge.workers.arq_worker.WorkerSettings*'
        }
        foreach ($worker in $workers) {
            Write-PublishLog "Restarting TraceForge worker PID $($worker.ProcessId); watchdog will restore it."
            Stop-Process -Id $worker.ProcessId -Force -ErrorAction Stop
        }
        if (-not $workers) {
            Write-PublishLog 'TraceForge worker is not running; watchdog will start it.'
        }
    } catch {
        Write-PublishLog "WARNING: Could not restart TraceForge worker: $($_.Exception.Message)"
    }
}

if ($builtAny) {
    # Every frontend is served as static files. Recycling the shared application
    # pool after a build is unnecessary and causes Azure Relay requests to see a
    # transient 502 while IIS spins the pool back up. Vite writes hashed assets
    # and then replaces index.html, so the new build is visible without a recycle.
    Write-PublishLog 'Frontend assets published without recycling the shared IIS application pool.'
}

Write-PublishLog 'Production publish completed.'
