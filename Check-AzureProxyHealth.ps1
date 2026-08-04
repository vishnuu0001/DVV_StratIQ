# ---------------------------------------------------------------------------
# Azure Service Proxy Health Check Script
# Scope: Monitor and verify the Strat-IQ Azure Service Proxy status
# Date: 2026-08-04
# ---------------------------------------------------------------------------

[CmdletBinding()]
param(
    [string]$SiteName = 'Strat-IQ-Azure-Proxy',
    [int]$LocalPort = 8096,
    [string]$AzureServiceUrl = 'https://strat-iq.azurewebsites.net',
    [switch]$Repair,
    [switch]$Verbose
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Continue'

# Colors
$colors = @{
    Success = 'Green'
    Error = 'Red'
    Warning = 'Yellow'
    Info = 'Cyan'
}

function Write-Status {
    param(
        [string]$Message,
        [string]$Status = 'Info',
        [string]$Icon = '->'
    )
    $color = $colors[$Status]
    Write-Host "$Icon $Message" -ForegroundColor $color
}

function Check-IISSite {
    param([string]$Name)
    
    Write-Host "`n[IIS Site Check]" -ForegroundColor Cyan
    
    try {
        Import-Module WebAdministration -ErrorAction Stop
        $site = Get-Website -Name $Name -ErrorAction SilentlyContinue
        
        if (-not $site) {
            Write-Status "Site '$Name' not found" 'Error' '[X]'
            return $false
        }
        
        $status = $site.State
        if ($status -eq 'Started') {
            Write-Status "Site '$Name' is running" 'Success' '[OK]'
            return $true
        } else {
            Write-Status "Site '$Name' is in state: $status" 'Warning' '[!]'
            return $false
        }
    } catch {
        Write-Status "Error checking site: $_" 'Error' '✗'
        return $false
    }
}

function Check-AppPool {
    param([string]$PoolName)
    
    Write-Host "`n[Application Pool Check]" -ForegroundColor Cyan
    
    try {
        $pool = Get-WebAppPoolState -Name $PoolName -ErrorAction SilentlyContinue
        
        if (-not $pool) {
            Write-Status "App pool '$PoolName' not found" 'Error' '[X]'
            return $false
        }
        
        if ($pool.Value -eq 'Started') {
            Write-Status "App pool '$PoolName' is running" 'Success' '[OK]'
            return $true
        } else {
            Write-Status "App pool '$PoolName' is in state: $($pool.Value)" 'Warning' '[!]'
            return $false
        }
    } catch {
        Write-Status "Error checking app pool: $_" 'Error' '✗'
        return $false
    }
}

function Check-LocalConnection {
    param([int]$Port)
    
    Write-Host "`n[Local Connection Check]" -ForegroundColor Cyan
    
    try {
        $testUrl = "http://localhost:$Port/"
        $response = Invoke-WebRequest -Uri $testUrl -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue
        
        if ($response.StatusCode -eq 200) {
            Write-Status "Local proxy responding on port $Port" 'Success' '[OK]'
            return $true
        } else {
            Write-Status "Local proxy returned status $($response.StatusCode)" 'Warning' '[!]'
            return $false
        }
    } catch {
        Write-Status "Cannot connect to local proxy: $($_.Exception.Message)" 'Error' '[X]'
        return $false
    }
}

function Check-AzureConnectivity {
    param([string]$Url)
    
    Write-Host "`n[Azure Service Connectivity Check]" -ForegroundColor Cyan
    
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 10 -ErrorAction SilentlyContinue
        
        if ($response.StatusCode -eq 200) {
            Write-Status "Azure Service is accessible" 'Success' '[OK]'
            return $true
        } else {
            Write-Status "Azure Service returned status $($response.StatusCode)" 'Warning' '[!]'
            return $false
        }
    } catch {
        Write-Status "Cannot reach Azure Service: $($_.Exception.Message)" 'Error' '[X]'
        return $false
    }
}

function Check-Ports {
    param([int]$Port)
    
    Write-Host "`n[Port Availability Check]" -ForegroundColor Cyan
    
    try {
        $listeners = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        
        if ($listeners) {
            Write-Status "Port $Port is in use by IIS" 'Success' '[OK]'
            return $true
        } else {
            Write-Status "Port $Port is not listening" 'Warning' '[!]'
            return $false
        }
    } catch {
        Write-Status "Error checking port: $_" 'Error' '[X]'
        return $false
    }
}

function Repair-Site {
    param(
        [string]$SiteName,
        [string]$AppPoolName
    )
    
    Write-Host "`n[Repair Mode]" -ForegroundColor Yellow
    
    try {
        Write-Status "Stopping website..." 'Info'
        Stop-Website -Name $SiteName -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        
        Write-Status "Stopping app pool..." 'Info'
        Stop-WebAppPool -Name $AppPoolName -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        
        Write-Status "Starting app pool..." 'Info'
        Start-WebAppPool -Name $AppPoolName
        Start-Sleep -Seconds 2
        
        Write-Status "Starting website..." 'Info'
        Start-Website -Name $SiteName
        Start-Sleep -Seconds 2
        
        Write-Status "Repair completed successfully" 'Success' '[OK]'
    } catch {
        Write-Status "Error during repair: $_" 'Error' '[X]'
    }
}

# ============================================================================
# Main Execution
# ============================================================================

Write-Host "`n╔════════════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║  Azure Service Proxy Health Check              ║" -ForegroundColor Blue
Write-Host "╚════════════════════════════════════════════════╝" -ForegroundColor Blue

Write-Host "`nConfiguration:" -ForegroundColor Cyan
Write-Host "  Site Name:        $SiteName"
Write-Host "  Local Port:       $LocalPort"
Write-Host "  Azure Backend:    $AzureServiceUrl"
Write-Host "  Timestamp:        $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

$healthyChecks = 0
$totalChecks = 0

# Run health checks
$checks = @(
    @{ Name = 'IIS Site'; Script = { Check-IISSite -Name $SiteName } },
    @{ Name = 'App Pool'; Script = { Check-AppPool -PoolName $AppPoolName } },
    @{ Name = 'Local Port'; Script = { Check-Ports -Port $LocalPort } },
    @{ Name = 'Local Connection'; Script = { Check-LocalConnection -Port $LocalPort } },
    @{ Name = 'Azure Connectivity'; Script = { Check-AzureConnectivity -Url $AzureServiceUrl } }
)

$AppPoolName = "$SiteName"

foreach ($check in $checks) {
    $totalChecks++
    $result = & $check.Script
    if ($result) { $healthyChecks++ }
}

# Summary
Write-Host "`n====================================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

$healthPercent = [math]::Round(($healthyChecks / $totalChecks) * 100)
$statusIcon = if ($healthyChecks -eq $totalChecks) { '[OK]' } else { '[!]' }
$statusColor = if ($healthyChecks -eq $totalChecks) { 'Green' } else { 'Yellow' }

Write-Host "`nStatus: $healthPercent% ($healthyChecks/$totalChecks checks passed)" -ForegroundColor $statusColor

if ($Repair -and $healthyChecks -lt $totalChecks) {
    Write-Host "`nAttempting automatic repair..." -ForegroundColor Yellow
    Repair-Site -SiteName $SiteName -AppPoolName $AppPoolName
    
    Write-Host "`nRe-running health checks..." -ForegroundColor Cyan
    Start-Sleep -Seconds 3
    $healthyChecks = 0
    foreach ($check in $checks) {
        $result = & $check.Script
        if ($result) { $healthyChecks++ }
    }
    
    $healthPercent = [math]::Round(($healthyChecks / $totalChecks) * 100)
    $statusColor = if ($healthyChecks -eq $totalChecks) { 'Green' } else { 'Yellow' }
    Write-Host "`nRepair Complete: $healthPercent% ($healthyChecks/$totalChecks checks passed)" -ForegroundColor $statusColor
}

# Exit code based on health status
if ($healthyChecks -eq $totalChecks) {
    Write-Host "All systems operational" -ForegroundColor Green
    exit 0
} else {
    Write-Host "Some systems require attention" -ForegroundColor Yellow
    exit 1
}
