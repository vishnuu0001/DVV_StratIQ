# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: supply-chain-disruption-manager — one-click recovery (Recover-SCM.ps1)
# Date: 2026-07-26
# ---------------------------------------------------------------------------
[CmdletBinding()]
param(
    [switch]$SkipInstall,
    [switch]$SkipInfraStart,
    [switch]$SkipProxyChecks,
    [int]$PortWaitSeconds = 45
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$logsDir = Join-Path $root 'logs'
New-Item -ItemType Directory -Path $logsDir -Force | Out-Null

$script:Results = New-Object System.Collections.Generic.List[Object]

# Function: Add-Result
function Add-Result {
    param(
        [string]$Name,
        [ValidateSet('PASS', 'FAIL', 'WARN', 'SKIP')]
        [string]$Status,
        [string]$Detail
    )
    $script:Results.Add([pscustomobject]@{
        Name = $Name
        Status = $Status
        Detail = $Detail
    })

    $color = switch ($Status) {
        'PASS' { 'Green' }
        'FAIL' { 'Red' }
        'WARN' { 'Yellow' }
        'SKIP' { 'DarkYellow' }
        default { 'White' }
    }
    Write-Host ("[{0}] {1} - {2}" -f $Status, $Name, $Detail) -ForegroundColor $color
}

# Function: Test-PortOpen
function Test-PortOpen {
    param([int]$Port)
    $client = [System.Net.Sockets.TcpClient]::new()
    try {
        $async = $client.BeginConnect('127.0.0.1', $Port, $null, $null)
        if (-not $async.AsyncWaitHandle.WaitOne(800, $false)) {
            return $false
        }
        $client.EndConnect($async)
        return $true
    }
    catch {
        return $false
    }
    finally {
        $client.Close()
    }
}

# Function: Wait-Port
function Wait-Port {
    param(
        [int]$Port,
        [int]$TimeoutSeconds = 30
    )
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-PortOpen -Port $Port) {
            return $true
        }
        Start-Sleep -Milliseconds 800
    }
    return $false
}

# Function: Ensure-EnvLocalhost
function Ensure-EnvLocalhost {
    $envLocalPath = Join-Path $root '.env.localhost'
    if (Test-Path -LiteralPath $envLocalPath) {
        Add-Result -Name '.env.localhost' -Status 'PASS' -Detail 'Present.'
        return
    }

    $content = @"
# Localhost environment for SCM Windows run
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=disruption123
POSTGRES_URL=postgresql+asyncpg://sc_admin:sc_secret@localhost:5432/disruption_mgr
REDIS_URL=redis://localhost:6379/0
KG_API_KEY=kg-dev-key-change-in-prod
KG_BASE_URL=http://localhost:8001
AGENT_API_KEY=agent-dev-key-change-in-prod
AGENT_BASE_URL=http://localhost:8002
INSPECTOR_BASE_URL=http://localhost:8003
INSPECTOR_ERP_HMAC_SECRET=erp-hmac-secret-change-in-prod
ENVIRONMENT=development
DEBUG=true
LOG_JSON=false
MOCK_AGENTS=true
"@

    Set-Content -Path $envLocalPath -Value $content -Encoding ASCII
    Add-Result -Name '.env.localhost' -Status 'PASS' -Detail 'Created missing localhost env file.'
}

# Function: Ensure-EnvFile
function Ensure-EnvFile {
    $envPath = Join-Path $root '.env'
    $envLocalPath = Join-Path $root '.env.localhost'

    if (-not (Test-Path -LiteralPath $envPath)) {
        Copy-Item -LiteralPath $envLocalPath -Destination $envPath -Force
        Add-Result -Name '.env' -Status 'PASS' -Detail 'Created from .env.localhost.'
    }
    else {
        Add-Result -Name '.env' -Status 'PASS' -Detail 'Present.'
    }
}

# Function: Ensure-Command
function Ensure-Command {
    param([string]$Name)
    if (Get-Command $Name -ErrorAction SilentlyContinue) {
        Add-Result -Name "command:$Name" -Status 'PASS' -Detail 'Installed.'
        return $true
    }
    Add-Result -Name "command:$Name" -Status 'FAIL' -Detail 'Not found in PATH.'
    return $false
}

# Function: Ensure-ServiceVenv
function Ensure-ServiceVenv {
    param(
        [string]$ServiceName,
        [string]$ServicePath
    )

    $venvPython = Join-Path $ServicePath '.venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $venvPython)) {
        if ($SkipInstall) {
            Add-Result -Name "$ServiceName venv" -Status 'FAIL' -Detail 'Missing and -SkipInstall set.'
            return $false
        }
        try {
            Push-Location -LiteralPath $ServicePath
            python -m venv .venv | Out-Null
            Pop-Location
        }
        catch {
            if (Get-Location) { Pop-Location }
            Add-Result -Name "$ServiceName venv" -Status 'FAIL' -Detail "Failed to create venv: $($_.Exception.Message)"
            return $false
        }
    }

    if ($SkipInstall) {
        Add-Result -Name "$ServiceName deps" -Status 'SKIP' -Detail 'Dependency install skipped.'
        return $true
    }

    try {
        & $venvPython -m pip install --upgrade pip | Out-Null
        & $venvPython -m pip install -e $ServicePath | Out-Null
        Add-Result -Name "$ServiceName deps" -Status 'PASS' -Detail 'Dependencies are ready.'
        return $true
    }
    catch {
        Add-Result -Name "$ServiceName deps" -Status 'FAIL' -Detail "Dependency install failed: $($_.Exception.Message)"
        return $false
    }
}

# Function: Find-Service
function Find-Service {
    param(
        [string[]]$NamePatterns,
        [string[]]$DisplayPatterns
    )

    $services = Get-Service -ErrorAction SilentlyContinue
    foreach ($svc in $services) {
        $nameMatch = $false
        $displayMatch = $false

        foreach ($p in $NamePatterns) {
            if ($svc.Name -like $p) { $nameMatch = $true; break }
        }
        foreach ($p in $DisplayPatterns) {
            if ($svc.DisplayName -like $p) { $displayMatch = $true; break }
        }

        if ($nameMatch -or $displayMatch) {
            return $svc
        }
    }

    return $null
}

# Function: Ensure-Infra
function Ensure-Infra {
    param(
        [string]$Name,
        [int]$Port,
        [string[]]$NamePatterns,
        [string[]]$DisplayPatterns
    )

    if (Test-PortOpen -Port $Port) {
        Add-Result -Name $Name -Status 'PASS' -Detail "Port $Port already listening."
        return $true
    }

    if ($SkipInfraStart) {
        Add-Result -Name $Name -Status 'FAIL' -Detail "Port $Port is down and -SkipInfraStart set."
        return $false
    }

    $svc = Find-Service -NamePatterns $NamePatterns -DisplayPatterns $DisplayPatterns
    if (-not $svc) {
        Add-Result -Name $Name -Status 'FAIL' -Detail "No Windows service found for $Name (expected port $Port)."
        return $false
    }

    try {
        if ($svc.Status -ne 'Running') {
            Start-Service -Name $svc.Name
        }
    }
    catch {
        Add-Result -Name $Name -Status 'FAIL' -Detail "Failed to start service '$($svc.Name)': $($_.Exception.Message)"
        return $false
    }

    if (Wait-Port -Port $Port -TimeoutSeconds $PortWaitSeconds) {
        Add-Result -Name $Name -Status 'PASS' -Detail "Service '$($svc.Name)' is running on port $Port."
        return $true
    }

    Add-Result -Name $Name -Status 'FAIL' -Detail "Service '$($svc.Name)' did not open port $Port."
    return $false
}

# Function: Set-ScmEnv
function Set-ScmEnv {
    [Environment]::SetEnvironmentVariable('PYTHONUNBUFFERED', '1', 'Process')
    [Environment]::SetEnvironmentVariable('ENVIRONMENT', 'development', 'Process')
    [Environment]::SetEnvironmentVariable('DEBUG', 'true', 'Process')
    [Environment]::SetEnvironmentVariable('LOG_JSON', 'false', 'Process')
    [Environment]::SetEnvironmentVariable('NEO4J_URI', 'bolt://localhost:7687', 'Process')
    [Environment]::SetEnvironmentVariable('NEO4J_USER', 'neo4j', 'Process')
    [Environment]::SetEnvironmentVariable('NEO4J_PASSWORD', 'disruption123', 'Process')
    [Environment]::SetEnvironmentVariable('KG_API_KEY', 'kg-dev-key-change-in-prod', 'Process')
    [Environment]::SetEnvironmentVariable('KG_BASE_URL', 'http://localhost:8001', 'Process')
    [Environment]::SetEnvironmentVariable('POSTGRES_URL', 'postgresql+asyncpg://sc_admin:sc_secret@localhost:5432/disruption_mgr', 'Process')
    [Environment]::SetEnvironmentVariable('REDIS_URL', 'redis://localhost:6379/0', 'Process')
    [Environment]::SetEnvironmentVariable('AGENT_API_KEY', 'agent-dev-key-change-in-prod', 'Process')
    [Environment]::SetEnvironmentVariable('AGENT_BASE_URL', 'http://localhost:8002', 'Process')
    [Environment]::SetEnvironmentVariable('INSPECTOR_ERP_HMAC_SECRET', 'erp-hmac-secret-change-in-prod', 'Process')
    [Environment]::SetEnvironmentVariable('MOCK_AGENTS', 'true', 'Process')
}

# Function: Start-ScmApi
function Start-ScmApi {
    param(
        [string]$Name,
        [string]$ServicePath,
        [string]$Module,
        [int]$Port
    )

    if (Test-PortOpen -Port $Port) {
        Add-Result -Name $Name -Status 'PASS' -Detail "Port $Port already listening."
        return $true
    }

    $python = Join-Path $ServicePath '.venv\Scripts\python.exe'
    $src = Join-Path $ServicePath 'src'
    if (-not (Test-Path -LiteralPath $python)) {
        Add-Result -Name $Name -Status 'FAIL' -Detail "Missing venv python at $python"
        return $false
    }

    $outLog = Join-Path $logsDir ("recover-{0}.out.log" -f $Name)
    $errLog = Join-Path $logsDir ("recover-{0}.err.log" -f $Name)

    try {
        Start-Process -FilePath $python `
            -ArgumentList @('-m', 'uvicorn', $Module, '--host', '127.0.0.1', '--port', $Port.ToString(), '--log-level', 'info') `
            -WorkingDirectory $src `
            -RedirectStandardOutput $outLog `
            -RedirectStandardError $errLog `
            -WindowStyle Hidden | Out-Null
    }
    catch {
        Add-Result -Name $Name -Status 'FAIL' -Detail "Failed to launch process: $($_.Exception.Message)"
        return $false
    }

    if (Wait-Port -Port $Port -TimeoutSeconds $PortWaitSeconds) {
        Add-Result -Name $Name -Status 'PASS' -Detail "Started on port $Port."
        return $true
    }

    $detail = "Process launched but port $Port is still down. Check $errLog"
    Add-Result -Name $Name -Status 'FAIL' -Detail $detail
    return $false
}

# Function: Invoke-Check
function Invoke-Check {
    param(
        [string]$Name,
        [string]$Url,
        [hashtable]$Headers = @{},
        [int[]]$ExpectedStatuses = @(200)
    )

    try {
        $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 8 -Headers $Headers
        $status = [int]$resp.StatusCode
        if ($ExpectedStatuses -contains $status) {
            Add-Result -Name $Name -Status 'PASS' -Detail "$Url => $status"
            return
        }
        Add-Result -Name $Name -Status 'FAIL' -Detail "$Url => $status (unexpected)"
    }
    catch {
        $code = $null
        if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
            $code = [int]$_.Exception.Response.StatusCode
        }
        if ($null -ne $code) {
            Add-Result -Name $Name -Status 'FAIL' -Detail "$Url => $code"
        }
        else {
            Add-Result -Name $Name -Status 'FAIL' -Detail "$Url => $($_.Exception.Message)"
        }
    }
}

Write-Host '=== SCM One-Click Recovery ===' -ForegroundColor Cyan
Write-Host "Root: $root" -ForegroundColor Cyan

Ensure-EnvLocalhost
Ensure-EnvFile

$pythonOk = Ensure-Command -Name 'python'
$npmOk = Ensure-Command -Name 'npm'

$serviceDefs = @(
    @{ Name = 'KG Service'; Path = Join-Path $root 'services\kg-service' },
    @{ Name = 'Signal Inspector'; Path = Join-Path $root 'services\signal-inspector' },
    @{ Name = 'Agent Service'; Path = Join-Path $root 'services\agent-service' }
)

if ($pythonOk -and (-not $SkipInstall)) {
    foreach ($svc in $serviceDefs) {
        Ensure-ServiceVenv -ServiceName $svc.Name -ServicePath $svc.Path | Out-Null
    }
}
elseif ($SkipInstall) {
    Add-Result -Name 'Dependency Install' -Status 'SKIP' -Detail 'Skipped by flag.'
}

$infraOk = $true
$infraOk = (Ensure-Infra -Name 'PostgreSQL' -Port 5432 -NamePatterns @('postgresql*') -DisplayPatterns @('*PostgreSQL*')) -and $infraOk
$infraOk = (Ensure-Infra -Name 'Redis/Memurai' -Port 6379 -NamePatterns @('Memurai*', 'redis*') -DisplayPatterns @('*Memurai*', '*Redis*')) -and $infraOk
$infraOk = (Ensure-Infra -Name 'Neo4j' -Port 7687 -NamePatterns @('neo4j*') -DisplayPatterns @('*Neo4j*')) -and $infraOk

if (-not (Test-PortOpen -Port 7474)) {
    Add-Result -Name 'Neo4j HTTP' -Status 'WARN' -Detail 'Port 7474 is down (browser UI may be unavailable).'
}
else {
    Add-Result -Name 'Neo4j HTTP' -Status 'PASS' -Detail 'Port 7474 listening.'
}

Set-ScmEnv

$launcher = Join-Path $root 'Start+Services.ps1'
if (Test-Path -LiteralPath $launcher) {
    try {
        & powershell -ExecutionPolicy Bypass -File $launcher -SkipUi -NoBrowser -NoWait -RestartApps | Out-Null
        Add-Result -Name 'Start+Services.ps1' -Status 'PASS' -Detail 'Launcher executed.'
    }
    catch {
        Add-Result -Name 'Start+Services.ps1' -Status 'WARN' -Detail "Launcher reported an error: $($_.Exception.Message)"
    }
}
else {
    Add-Result -Name 'Start+Services.ps1' -Status 'WARN' -Detail 'Launcher not found; using direct process start.'
}

Start-ScmApi -Name 'KG API' -ServicePath (Join-Path $root 'services\kg-service') -Module 'kg.main:app' -Port 8001 | Out-Null
Start-ScmApi -Name 'Agent API' -ServicePath (Join-Path $root 'services\agent-service') -Module 'agents.main:app' -Port 8002 | Out-Null
Start-ScmApi -Name 'Inspector API' -ServicePath (Join-Path $root 'services\signal-inspector') -Module 'inspector.main:app' -Port 8003 | Out-Null

$agentHeaders = @{ 'X-API-Key' = 'agent-dev-key-change-in-prod' }
$kgHeaders = @{ 'X-API-Key' = 'kg-dev-key-change-in-prod' }

Invoke-Check -Name 'Local KG Health' -Url 'http://localhost:8001/health'
Invoke-Check -Name 'Local Inspector Health' -Url 'http://localhost:8003/health'
Invoke-Check -Name 'Local Agent Health' -Url 'http://localhost:8002/health' -Headers $agentHeaders

Invoke-Check -Name 'KG Entities Supplier' -Url 'http://localhost:8001/entities?kind=Supplier&limit=10' -Headers $kgHeaders
Invoke-Check -Name 'KG Entities Warehouse' -Url 'http://localhost:8001/entities?kind=Warehouse&limit=10' -Headers $kgHeaders
Invoke-Check -Name 'KG Entities PurchaseOrder' -Url 'http://localhost:8001/entities?kind=PurchaseOrder&limit=10' -Headers $kgHeaders
Invoke-Check -Name 'KG Entities Shipment' -Url 'http://localhost:8001/entities?kind=Shipment&limit=10' -Headers $kgHeaders
Invoke-Check -Name 'KG Entities Material' -Url 'http://localhost:8001/entities?kind=Material&limit=10' -Headers $kgHeaders
Invoke-Check -Name 'KG Entities ProductionOrder' -Url 'http://localhost:8001/entities?kind=ProductionOrder&limit=10' -Headers $kgHeaders
Invoke-Check -Name 'Inspector Adapters' -Url 'http://localhost:8003/adapters'
Invoke-Check -Name 'Inspector Events(limit=10)' -Url 'http://localhost:8003/events?limit=10'
Invoke-Check -Name 'Agent Incidents(limit=50)' -Url 'http://localhost:8002/incidents?limit=50' -Headers $agentHeaders

if (-not $SkipProxyChecks) {
    if (Test-PortOpen -Port 8090) {
        Invoke-Check -Name 'Proxy KG Health' -Url 'http://localhost:8090/api/kg/health'
        Invoke-Check -Name 'Proxy Inspector Health' -Url 'http://localhost:8090/api/inspector/health'
        Invoke-Check -Name 'Proxy Agent Health' -Url 'http://localhost:8090/api/agents/health' -Headers $agentHeaders
        Invoke-Check -Name 'Proxy KG Supplier' -Url 'http://localhost:8090/api/kg/entities?kind=Supplier&limit=10' -Headers $kgHeaders
        Invoke-Check -Name 'Proxy Inspector Adapters' -Url 'http://localhost:8090/api/inspector/adapters'
        Invoke-Check -Name 'Proxy Agent Incidents' -Url 'http://localhost:8090/api/agents/incidents?limit=50' -Headers $agentHeaders
    }
    else {
        Add-Result -Name 'Proxy Checks' -Status 'SKIP' -Detail 'Port 8090 not listening in this environment.'
    }
}
else {
    Add-Result -Name 'Proxy Checks' -Status 'SKIP' -Detail 'Skipped by flag.'
}

Write-Host ''
Write-Host '=== Recovery Summary ===' -ForegroundColor Cyan
$script:Results | Format-Table -AutoSize

$pass = @($script:Results | Where-Object { $_.Status -eq 'PASS' }).Count
$warn = @($script:Results | Where-Object { $_.Status -eq 'WARN' }).Count
$skip = @($script:Results | Where-Object { $_.Status -eq 'SKIP' }).Count
$fail = @($script:Results | Where-Object { $_.Status -eq 'FAIL' }).Count

Write-Host ''
Write-Host ("PASS={0} WARN={1} SKIP={2} FAIL={3}" -f $pass, $warn, $skip, $fail) -ForegroundColor White

if ($fail -gt 0) {
    exit 1
}
exit 0
