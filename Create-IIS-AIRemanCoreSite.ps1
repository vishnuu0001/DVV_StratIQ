# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: Create-IIS-AIRemanCoreSite.ps1 — Create-IIS-AIRemanCoreSite (Create-IIS-AIRemanCoreSite.ps1)
# Date: 2026-04-06
# ---------------------------------------------------------------------------
[CmdletBinding()]
param(
    [string]$SiteName = 'StratIQ-AIRemanCore',
    [int]$Port = 8090,
    [string]$HostHeader = '',
    [string]$AppPoolName = 'StratIQ-AIRemanCore',
    [string]$PortalPath = '',
    [string]$RemanPath = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSCommandPath
if (-not $PortalPath) {
    $PortalPath = Join-Path $repoRoot 'AppRationalization\frontend\build'
}
if (-not $RemanPath) {
    $RemanPath = Join-Path $repoRoot 'AI_Reman_Core\build'
}

foreach ($path in @($PortalPath, $RemanPath)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Build output not found: $path. Run npm run build first."
    }
}

Import-Module WebAdministration

if (-not (Test-Path "IIS:\AppPools\$AppPoolName")) {
    New-WebAppPool -Name $AppPoolName | Out-Null
}

Set-ItemProperty -Path "IIS:\AppPools\$AppPoolName" -Name managedRuntimeVersion -Value ''
Set-ItemProperty -Path "IIS:\AppPools\$AppPoolName" -Name startMode -Value AlwaysRunning

$bindingInfo = if ($HostHeader) { "*:${Port}:${HostHeader}" } else { "*:${Port}:" }

if (-not (Test-Path "IIS:\Sites\$SiteName")) {
    New-Website -Name $SiteName `
        -Port $Port `
        -HostHeader $HostHeader `
        -PhysicalPath $PortalPath `
        -ApplicationPool $AppPoolName | Out-Null
} else {
    Set-ItemProperty -Path "IIS:\Sites\$SiteName" -Name physicalPath -Value $PortalPath
    Set-ItemProperty -Path "IIS:\Sites\$SiteName" -Name applicationPool -Value $AppPoolName
    $site = Get-Website -Name $SiteName
    $hasBinding = $site.bindings.Collection | Where-Object { $_.bindingInformation -eq $bindingInfo -and $_.protocol -eq 'http' }
    if (-not $hasBinding) {
        New-WebBinding -Name $SiteName -Protocol http -Port $Port -HostHeader $HostHeader | Out-Null
    }
}

$remanAppPath = "IIS:\Sites\$SiteName\reman"
if (Test-Path $remanAppPath) {
    Set-ItemProperty -Path $remanAppPath -Name physicalPath -Value $RemanPath
    Set-ItemProperty -Path $remanAppPath -Name applicationPool -Value $AppPoolName
} else {
    New-WebApplication -Site $SiteName -Name 'reman' -PhysicalPath $RemanPath -ApplicationPool $AppPoolName | Out-Null
}

Start-WebAppPool -Name $AppPoolName -ErrorAction SilentlyContinue
Start-Website -Name $SiteName

Write-Host "IIS site ready: http://localhost:$Port/" -ForegroundColor Green
Write-Host "AI Reman Core: http://localhost:$Port/reman/" -ForegroundColor Green
