# ---------------------------------------------------------------------------
# Author: GitHub Copilot
# Scope: Create-IIS-AzureServiceProxy.ps1 — Create IIS reverse proxy to Azure Service
# Date: 2026-08-04
# Description: Creates a new IIS site that proxies all requests to 
#              https://strat-iq.azurewebsites.net/
# ---------------------------------------------------------------------------
[CmdletBinding()]
param(
    [string]$SiteName = 'Strat-IQ-Azure-Proxy',
    [int]$Port = 8096,
    [string]$HostHeader = '',
    [string]$AppPoolName = 'Strat-IQ-Azure-Proxy',
    [string]$AzureServiceUrl = 'https://strat-iq.azurewebsites.net',
    [string]$PhysicalPath = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Get repository root
$repoRoot = Split-Path -Parent $PSCommandPath

# Create physical path if not specified
if (-not $PhysicalPath) {
    $PhysicalPath = Join-Path $repoRoot 'LaunchModules\azure-proxy-root'
}

# Ensure physical path exists
if (-not (Test-Path -LiteralPath $PhysicalPath)) {
    Write-Host "Creating physical path: $PhysicalPath" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $PhysicalPath -Force | Out-Null
}

# Import IIS administration module
try {
    Import-Module WebAdministration -ErrorAction Stop
} catch {
    Write-Host "Error: WebAdministration module not available. Ensure IIS is installed." -ForegroundColor Red
    exit 1
}

# ============================================================================
# Create or Update Application Pool
# ============================================================================
Write-Host "Setting up application pool: $AppPoolName" -ForegroundColor Cyan

if (-not (Test-Path "IIS:\AppPools\$AppPoolName")) {
    Write-Host "  Creating new application pool..." -ForegroundColor Green
    New-WebAppPool -Name $AppPoolName | Out-Null
} else {
    Write-Host "  Application pool already exists" -ForegroundColor Yellow
}

# Configure application pool
Set-ItemProperty -Path "IIS:\AppPools\$AppPoolName" -Name managedRuntimeVersion -Value ''
Set-ItemProperty -Path "IIS:\AppPools\$AppPoolName" -Name startMode -Value AlwaysRunning
Set-ItemProperty -Path "IIS:\AppPools\$AppPoolName" -Name processModel.idleTimeout -Value '00:00:00'

Write-Host "  Application pool configured" -ForegroundColor Green

# ============================================================================
# Create or Update IIS Site
# ============================================================================
Write-Host "Setting up IIS site: $SiteName" -ForegroundColor Cyan

$bindingInfo = if ($HostHeader) { "*:${Port}:${HostHeader}" } else { "*:${Port}:" }

if (-not (Test-Path "IIS:\Sites\$SiteName")) {
    Write-Host "  Creating new site on port $Port..." -ForegroundColor Green
    New-Website -Name $SiteName `
        -Port $Port `
        -HostHeader $HostHeader `
        -PhysicalPath $PhysicalPath `
        -ApplicationPool $AppPoolName | Out-Null
} else {
    Write-Host "  Site already exists, updating configuration..." -ForegroundColor Yellow
    Set-ItemProperty -Path "IIS:\Sites\$SiteName" -Name physicalPath -Value $PhysicalPath
    Set-ItemProperty -Path "IIS:\Sites\$SiteName" -Name applicationPool -Value $AppPoolName
    
    # Check if binding exists
    $site = Get-Website -Name $SiteName
    $hasBinding = $site.bindings.Collection | Where-Object { $_.bindingInformation -eq $bindingInfo -and $_.protocol -eq 'http' }
    if (-not $hasBinding) {
        Write-Host "  Adding binding..." -ForegroundColor Green
        New-WebBinding -Name $SiteName -Protocol http -Port $Port -HostHeader $HostHeader | Out-Null
    }
}

Write-Host "  IIS site configured" -ForegroundColor Green

# ============================================================================
# Create web.config with reverse proxy rules
# ============================================================================
Write-Host "Creating reverse proxy configuration..." -ForegroundColor Cyan

$webConfigPath = Join-Path $PhysicalPath 'web.config'
$webConfigContent = @"
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <!-- URL Rewrite Module - Reverse proxy to Azure Service -->
    <rewrite>
      <outboundRules>
        <!-- Rewrite Location headers to use local proxy URL -->
        <rule name="Rewrite Location Header" preCondition="IsRedirect">
          <match filterByTags="Anchor, Form, Img" pattern="^https?://strat-iq\.azurewebsites\.net(.*)" />
          <action type="Rewrite" value="http://localhost:$Port{R:1}" />
        </rule>
        <rule name="Rewrite Refresh Header" preCondition="IsRefresh">
          <match filterByTags="Anchor, Form, Img" pattern="^https?://strat-iq\.azurewebsites\.net(.*)" />
          <action type="Rewrite" value="http://localhost:$Port{R:1}" />
        </rule>
        <preConditions>
          <preCondition name="IsRedirect">
            <add input="{RESPONSE_STATUS}" pattern="^3\d\d" />
          </preCondition>
          <preCondition name="IsRefresh">
            <add input="{RESPONSE_HEADER:Refresh}" pattern=".*" />
          </preCondition>
        </preConditions>
      </outboundRules>
      <rules>
        <!-- Proxy all requests to Azure Service -->
        <rule name="Azure Service Proxy" stopProcessing="true">
          <match url="^(.*)" />
          <conditions logicalGrouping="MatchAll">
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
          </conditions>
          <action type="Rewrite" url="$AzureServiceUrl/{R:1}" />
        </rule>
      </rules>
    </rewrite>

    <!-- Enable WebSocket for real-time features -->
    <webSocket enabled="true" />

    <!-- Security headers -->
    <httpProtocol>
      <customHeaders>
        <remove name="X-Powered-By" />
        <add name="X-Content-Type-Options" value="nosniff" />
        <add name="X-Frame-Options" value="SAMEORIGIN" />
        <add name="X-XSS-Protection" value="1; mode=block" />
        <add name="Referrer-Policy" value="strict-origin-when-cross-origin" />
      </customHeaders>
    </httpProtocol>

    <!-- Compression for better performance -->
    <httpCompression directory="%SystemDrive%\inetpub\temp\IIS Temporary Compressed Files">
      <scheme name="gzip" dll="%Windir%\system32\inetsrv\gzip.dll" staticCompressionLevel="9" />
      <dynamicTypes>
        <add mimeType="text/*" enabled="true" />
        <add mimeType="application/json" enabled="true" />
        <add mimeType="application/javascript" enabled="true" />
      </dynamicTypes>
    </httpCompression>

    <!-- Proxy settings -->
    <proxy enabled="true" reverseRewriteHostInResponseHeaders="true" />
  </system.webServer>
</configuration>
"@

try {
    Set-Content -Path $webConfigPath -Value $webConfigContent -Encoding UTF8 -Force
    Write-Host "  web.config created at: $webConfigPath" -ForegroundColor Green
} catch {
    Write-Host "  Error creating web.config: $_" -ForegroundColor Red
    exit 1
}

# ============================================================================
# Start Site and AppPool
# ============================================================================
Write-Host "Starting services..." -ForegroundColor Cyan

try {
    Start-WebAppPool -Name $AppPoolName -ErrorAction SilentlyContinue
    Write-Host "  Application pool started" -ForegroundColor Green
} catch {
    Write-Host "  Warning: Could not start application pool: $_" -ForegroundColor Yellow
}

try {
    Start-Website -Name $SiteName
    Write-Host "  Website started" -ForegroundColor Green
} catch {
    Write-Host "  Warning: Could not start website: $_" -ForegroundColor Yellow
}

# ============================================================================
# Summary
# ============================================================================
Write-Host ""
Write-Host "===================================================================" -ForegroundColor Green
Write-Host "IIS Reverse Proxy to Azure Service Created Successfully!" -ForegroundColor Green
Write-Host "===================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Site Details:" -ForegroundColor Cyan
Write-Host "  Site Name:        $SiteName"
Write-Host "  Local URL:        http://localhost:$Port/"
Write-Host "  App Pool:         $AppPoolName"
Write-Host "  Physical Path:    $PhysicalPath"
Write-Host "  Azure Backend:    $AzureServiceUrl"
Write-Host ""
Write-Host "Configuration File:" -ForegroundColor Cyan
Write-Host "  web.config:       $webConfigPath"
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Verify the site is running: http://localhost:$Port/"
Write-Host "  2. Check IIS Manager for any errors"
Write-Host "  3. Review web.config for custom proxy rules"
Write-Host "  4. To add host header, edit the site bindings in IIS Manager"
Write-Host ""
