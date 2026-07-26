# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: supply-chain-disruption-manager — scripts (Seed-Local.ps1)
# Date: 2025-11-12
# ---------------------------------------------------------------------------
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

# Function: Get-DotEnvValue
function Get-DotEnvValue($Name, $Default) {
    $envPath = Join-Path $root ".env"
    if (Test-Path $envPath) {
        $match = Select-String -Path $envPath -Pattern "^$Name=" -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($match) {
            return $match.Line.Split("=", 2)[1]
        }
    }
    return $Default
}

# Function: Wait-Http
function Wait-Http($Url, $Headers = @{}) {
    for ($i = 0; $i -lt 30; $i++) {
        try {
            Invoke-RestMethod -Uri $Url -Headers $Headers -TimeoutSec 3 | Out-Null
            return
        }
        catch {
            Start-Sleep -Seconds 2
        }
    }
    throw "Timed out waiting for $Url"
}

$kgKey = Get-DotEnvValue "KG_API_KEY" "kg-dev-key-change-in-prod"
$agentKey = Get-DotEnvValue "AGENT_API_KEY" "agent-dev-key-change-in-prod"

Write-Host "Waiting for local APIs..."
Wait-Http "http://localhost:8001/health" @{ "X-API-Key" = $kgKey }
Wait-Http "http://localhost:8003/health"
Wait-Http "http://localhost:8002/health" @{ "X-API-Key" = $agentKey }

Write-Host "Seeding Knowledge Graph..."
Invoke-RestMethod `
    -Method Post `
    -Uri "http://localhost:8001/seed" `
    -Headers @{ "X-API-Key" = $kgKey } | ConvertTo-Json -Depth 8

Write-Host "Seeding canonical events..."
Get-ChildItem (Join-Path $root "seed\events\*.json") | ForEach-Object {
    Write-Host "  Posting $($_.Name)..."
    Invoke-RestMethod `
        -Method Post `
        -Uri "http://localhost:8003/ingest/manual" `
        -ContentType "application/json" `
        -InFile $_.FullName | Out-Null
}

Write-Host "Triggering supplier delay demo incident..."
Invoke-RestMethod `
    -Method Post `
    -Uri "http://localhost:8002/disruption" `
    -Headers @{ "X-API-Key" = $agentKey } `
    -ContentType "application/json" `
    -InFile (Join-Path $root "seed\scenarios\supplier_delay_trigger.json") | ConvertTo-Json -Depth 8

Write-Host ""
Write-Host "Demo data loaded. Open http://localhost:5173 or your IIS site."
