# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Maintenance — Shared-Auth (Shared-Auth.ps1)
# Date: 2026-01-29
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Scope: Resolve the single shared Strat-Aqorynth portal-token signing secret for
# service launchers without copying the credential into each launcher.
# ---------------------------------------------------------------------------

# Function: Get-Strat-AqorynthSharedAuthSecret
function Get-Strat-AqorynthSharedAuthSecret {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoRoot
    )

    if (-not [string]::IsNullOrWhiteSpace($env:STRATIQ_AUTH_TOKEN_SECRET)) {
        return $env:STRATIQ_AUTH_TOKEN_SECRET
    }
    if (-not [string]::IsNullOrWhiteSpace($env:AUTH_TOKEN_SECRET)) {
        return $env:AUTH_TOKEN_SECRET
    }

    # watchdog_all_backends.ps1 is the production process manifest and remains
    # the compatibility source until the installation moves this credential to
    # a machine secret store. Parse only the exact assignment and never log it.
    $watchdogPath = Join-Path $RepoRoot 'watchdog_all_backends.ps1'
    if (-not (Test-Path -LiteralPath $watchdogPath)) {
        throw "Shared authentication configuration was not found at $watchdogPath"
    }
    $line = Get-Content -LiteralPath $watchdogPath |
        Where-Object { $_ -match '^\$SharedSecret\s*=' } |
        Select-Object -First 1
    if (-not $line -or $line -notmatch "^\`$SharedSecret\s*=\s*'([^']+)'\s*$") {
        throw 'The shared authentication configuration is malformed.'
    }
    $secret = $Matches[1]
    if ($secret.Length -lt 32 -or $secret -match '^(change|replace|default|secret)') {
        throw 'The shared authentication configuration is insecure.'
    }
    return $secret
}
