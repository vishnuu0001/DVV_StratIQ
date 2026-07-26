# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Maintenance — Test-ModuleAuthentication (Test-ModuleAuthentication.ps1)
# Date: 2025-10-08
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Scope: End-to-end launch-route and shared-auth contract checks through IIS.
# No credential or token value is written to output.
# ---------------------------------------------------------------------------
[CmdletBinding()]
param(
    [string]$BaseUrl = 'http://127.0.0.1:8090'
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
. (Join-Path $PSScriptRoot 'Shared-Auth.ps1')
$SharedSecret = Get-Strat-AqorynthSharedAuthSecret -RepoRoot $RepoRoot

# Function: ConvertTo-Base64Url
function ConvertTo-Base64Url {
    param([byte[]]$Bytes)
    return [Convert]::ToBase64String($Bytes).TrimEnd('=').Replace('+', '-').Replace('/', '_')
}

# Function: New-PortalProbeToken
function New-PortalProbeToken {
    param(
        [string]$Role,
        [string[]]$Apps
    )
    $now = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
    $payload = @{
        uid = 0
        username = 'module-auth-probe'
        role = $Role
        apps = $Apps
        typ = 'access'
        iat = $now
        exp = $now + 180
    } | ConvertTo-Json -Compress
    $encodedPayload = ConvertTo-Base64Url ([Text.Encoding]::UTF8.GetBytes($payload))
    $hmac = [Security.Cryptography.HMACSHA256]::new(
        [Text.Encoding]::UTF8.GetBytes($SharedSecret)
    )
    try {
        $signature = ConvertTo-Base64Url (
            $hmac.ComputeHash([Text.Encoding]::UTF8.GetBytes($encodedPayload))
        )
    } finally {
        $hmac.Dispose()
    }
    return "v1.$encodedPayload.$signature"
}

# Function: Get-HttpStatus
function Get-HttpStatus {
    param(
        [string]$Uri,
        [string]$Token
    )
    $headers = @{}
    if ($Token) {
        $headers.Authorization = "Bearer $Token"
    }
    try {
        return [int](Invoke-WebRequest -UseBasicParsing -Uri $Uri -Headers $headers -TimeoutSec 20).StatusCode
    } catch {
        if ($_.Exception.Response) {
            return [int]$_.Exception.Response.StatusCode
        }
        return 0
    }
}

# Function: Assert-Status
function Assert-Status {
    param(
        [string]$Name,
        [string]$Phase,
        [int]$Actual,
        [int]$Expected
    )
    if ($Actual -ne $Expected) {
        throw "$Name $Phase returned HTTP $Actual; expected $Expected."
    }
    Write-Host "$Name $Phase`: HTTP $Actual"
}

$launchRoutes = @(
    '/ca/', '/infra/', '/mod/', '/novastra-itsm/ticket-analysis',
    '/dash', '/ssdlc/', '/lab/', '/ot/', '/reman/', '/vl/',
    '/mda/', '/scm/', '/tf/'
)
foreach ($route in $launchRoutes) {
    Assert-Status -Name $route -Phase 'launch' `
        -Actual (Get-HttpStatus "$($BaseUrl.TrimEnd('/'))$route" '') -Expected 200
}

$protectedApis = @(
    @{ Name = 'CodeAnalysis'; Path = '/api/codeanalysis/auth/session' },
    @{ Name = 'InfraRationalization'; Path = '/api/infra/auth/session' },
    @{ Name = 'Modernization'; Path = '/api/mod/auth/session' },
    @{ Name = 'Dashboard'; Path = '/api/dashboard/status' },
    @{ Name = 'SSDLC'; Path = '/api/ssdlc/auth/session' },
    @{ Name = 'LabRobot'; Path = '/api/lab/scientists' },
    @{ Name = 'OpportunityTracker'; Path = '/api/ot/opportunities' },
    @{ Name = 'AIRemanCore'; Path = '/api/reman/core-types' },
    @{ Name = 'AIVehicleLoan'; Path = '/api/vehicle-loan/vehicles' },
    @{ Name = 'TraceForge'; Path = '/api/tf/v1/projects' }
)
$adminToken = New-PortalProbeToken -Role 'admin' -Apps @()
$deniedToken = New-PortalProbeToken -Role 'user' -Apps @()
foreach ($api in $protectedApis) {
    $uri = "$($BaseUrl.TrimEnd('/'))$($api.Path)"
    Assert-Status -Name $api.Name -Phase 'without token' `
        -Actual (Get-HttpStatus $uri '') -Expected 401
    Assert-Status -Name $api.Name -Phase 'with shared token' `
        -Actual (Get-HttpStatus $uri $adminToken) -Expected 200
    Assert-Status -Name $api.Name -Phase 'without module permission' `
        -Actual (Get-HttpStatus $uri $deniedToken) -Expected 403
}

Write-Host 'All module launch and authentication checks passed.'
