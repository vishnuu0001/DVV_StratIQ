#!/usr/bin/env powershell
<#
.SYNOPSIS
    Start Strat-IQ Azure Proxy Services (IIS + Node.js Proxy)

.DESCRIPTION
    Starts both the IIS site and Node.js reverse proxy server for accessing
    the Azure Strat-IQ service from localhost.

.PARAMETER ProxyOnly
    Only start the Node.js proxy, skip IIS

.PARAMETER IISOnly
    Only start the IIS site, skip Node.js proxy

.EXAMPLE
    .\Start-AzureProxy.ps1
    .\Start-AzureProxy.ps1 -ProxyOnly
    .\Start-AzureProxy.ps1 -IISOnly
#>

param(
    [switch]$ProxyOnly,
    [switch]$IISOnly
)

$ErrorActionPreference = 'Stop'

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║ $Message" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

# Configuration
$IISSiteName = "Strat-IQ-Azure-Proxy"
$IISPort = 8096
$ProxyPath = "C:\RD\DVV_StratIQ-Aqorynth\dsvstratiq\LaunchModules\azure-proxy-root"
$ProxyPort = 8097

Write-Header "Strat-IQ Azure Proxy Startup"

# Start IIS Site (if not -ProxyOnly)
if (-not $ProxyOnly) {
    Write-Info "Starting IIS Site..."
    
    try {
        # Check if site exists
        $site = Get-IISSite -Name $IISSiteName -ErrorAction SilentlyContinue
        
        if ($null -eq $site) {
            Write-Warning "IIS Site '$IISSiteName' not found"
            Write-Info "You may need to run Create-IIS-AzureServiceProxy.ps1 first"
        }
        else {
            # Start the site if it's stopped
            if ($site.State -ne "Started") {
                Start-IISSite -Name $IISSiteName -Confirm:$false
                Start-Sleep -Seconds 2
            }
            
            $site = Get-IISSite -Name $IISSiteName
            if ($site.State -eq "Started") {
                Write-Success "IIS Site is running on http://localhost:$IISPort/"
            }
            else {
                Write-Warning "IIS Site is not responding (Status: $($site.State))"
            }
        }
    }
    catch {
        Write-Warning "Could not start IIS Site: $($_.Exception.Message)"
    }
}

# Start Node.js Proxy (if not -IISOnly)
if (-not $IISOnly) {
    Write-Info "Starting Node.js Proxy Server..."
    
    if (-not (Test-Path "$ProxyPath\proxy-server.js")) {
        Write-Error "Proxy server not found at: $ProxyPath\proxy-server.js"
        exit 1
    }
    
    # Check if proxy is already running
    $proxyProcess = Get-Process node -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -match 'proxy-server.js'
    }
    
    if ($null -ne $proxyProcess) {
        Write-Info "Proxy server is already running (PID: $($proxyProcess.Id))"
    }
    else {
        # Start proxy in new window
        try {
            Start-Process -FilePath "node" -ArgumentList "`"$ProxyPath\proxy-server.js`"" `
                -WorkingDirectory $ProxyPath `
                -WindowStyle Minimized `
                -PassThru | Out-Null
            
            Start-Sleep -Seconds 2
            Write-Success "Node.js Proxy started on http://localhost:$ProxyPort/"
        }
        catch {
            Write-Error "Failed to start proxy: $($_.Exception.Message)"
            exit 1
        }
    }
}

# Display summary
Write-Host ""
Write-Header "Services Configuration"

if (-not $ProxyOnly) {
    Write-Info "IIS Site Configuration:"
    Write-Host "  Site Name:     $IISSiteName" -ForegroundColor Gray
    Write-Host "  Local Address: http://localhost:$IISPort/" -ForegroundColor Gray
    Write-Host "  Purpose:       Static content server (without reverse proxy)" -ForegroundColor Gray
    Write-Host ""
}

if (-not $IISOnly) {
    Write-Info "Node.js Proxy Configuration:"
    Write-Host "  Port:          $ProxyPort" -ForegroundColor Gray
    Write-Host "  Local Address: http://localhost:$ProxyPort/" -ForegroundColor Gray
    Write-Host "  Azure Backend: https://strat-iq.azurewebsites.net/" -ForegroundColor Gray
    Write-Host "  Purpose:       Reverse proxy to Azure (with fallback status page)" -ForegroundColor Gray
    Write-Host ""
}

Write-Host ""
Write-Header "Next Steps"

Write-Host "1. Access the reverse proxy:" -ForegroundColor Cyan
Write-Host "   https://localhost:$ProxyPort/" -ForegroundColor Yellow
Write-Host ""

Write-Host "2. Monitor proxy activity:" -ForegroundColor Cyan
Write-Host "   Look for Node.js window for request logs" -ForegroundColor Yellow
Write-Host ""

Write-Host "3. To stop services:" -ForegroundColor Cyan
Write-Host "   - Close the Node.js window (Ctrl+C)" -ForegroundColor Yellow
Write-Host "   - Or use: Stop-IISSite -Name '$IISSiteName'" -ForegroundColor Yellow
Write-Host ""

Write-Host "Note: Services are running. You can close this window." -ForegroundColor Green
