#!/usr/bin/env powershell
<#
.SYNOPSIS
    Strat-IQ Azure Proxy Service Status Check

.DESCRIPTION
    Displays the status of all Strat-IQ Azure Proxy services
#>

$ErrorActionPreference = 'SilentlyContinue'

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║ $Message" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Test-ServicePort {
    param([string]$HostName, [int]$Port, [int]$TimeoutMs = 1000)
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $asyncResult = $tcpClient.BeginConnect($HostName, $Port, $null, $null)
        if ($asyncResult.AsyncWaitHandle.WaitOne($TimeoutMs)) {
            $tcpClient.EndConnect($asyncResult)
            $tcpClient.Close()
            return $true
        }
        return $false
    }
    catch { return $false }
}

Write-Header "Strat-IQ Azure Proxy Services Status"

# IIS Site Status
Write-Host "IIS Site Status:" -ForegroundColor Yellow
$site = Get-IISSite -Name "Strat-IQ-Azure-Proxy" -ErrorAction SilentlyContinue

if ($null -ne $site) {
    Write-Host "  Status: $($site.State)" -ForegroundColor $(if ($site.State -eq 'Started') { 'Green' } else { 'Red' })
    Write-Host "  URL: http://localhost:8096/" -ForegroundColor Gray
} else {
    Write-Host "  Status: Not found" -ForegroundColor Red
}

Write-Host ""

# Node.js Proxy Status
Write-Host "Node.js Proxy Status:" -ForegroundColor Yellow
$proxyProcess = Get-Process node -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match 'proxy-server.js' }

if ($null -ne $proxyProcess) {
    Write-Host "  Process: Running (PID: $($proxyProcess.Id))" -ForegroundColor Green
} else {
    Write-Host "  Process: Not running" -ForegroundColor Red
}

if (Test-ServicePort "localhost" 8097) {
    Write-Host "  Port 8097: Responding" -ForegroundColor Green
    Write-Host "  URL: http://localhost:8097/" -ForegroundColor Gray
} else {
    Write-Host "  Port 8097: Not responding" -ForegroundColor Red
}

Write-Host ""

# Azure Backend Status
Write-Host "Azure Backend Status:" -ForegroundColor Yellow
if (Test-ServicePort "strat-iq.azurewebsites.net" 443) {
    Write-Host "  Azure: Reachable" -ForegroundColor Green
    try {
        $response = Invoke-WebRequest -Uri "https://strat-iq.azurewebsites.net/" -UseBasicParsing -TimeoutSec 3 -ErrorAction SilentlyContinue
        Write-Host "  HTTP Status: $($response.StatusCode)" -ForegroundColor $(if ($response.StatusCode -lt 400) { 'Green' } else { 'Yellow' })
    }
    catch {
        Write-Host "  HTTP Status: Unavailable" -ForegroundColor Yellow
    }
} else {
    Write-Host "  Azure: Not reachable" -ForegroundColor Red
}

Write-Host ""
Write-Header "Quick Access URLs"

Write-Host "IIS (Static Content):" -ForegroundColor Yellow
Write-Host "  http://localhost:8096/" -ForegroundColor Gray
Write-Host ""

Write-Host "Reverse Proxy (Recommended):" -ForegroundColor Yellow
Write-Host "  http://localhost:8097/" -ForegroundColor Gray
Write-Host ""

Write-Host "Azure Direct:" -ForegroundColor Yellow
Write-Host "  https://strat-iq.azurewebsites.net/" -ForegroundColor Gray
Write-Host ""

Write-Header "Commands"

Write-Host "Start Services:" -ForegroundColor Yellow
Write-Host "  .\Start-AzureProxy.ps1" -ForegroundColor Gray
Write-Host ""

Write-Host "Stop IIS:" -ForegroundColor Yellow
Write-Host "  Stop-IISSite -Name 'Strat-IQ-Azure-Proxy'" -ForegroundColor Gray
Write-Host ""

Write-Host "Stop Proxy:" -ForegroundColor Yellow
Write-Host "  Get-Process node | Where-Object {`$_.CommandLine -match 'proxy-server'} | Stop-Process" -ForegroundColor Gray
Write-Host ""
