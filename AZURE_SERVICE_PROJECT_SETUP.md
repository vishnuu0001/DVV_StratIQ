# Strat-IQ Azure Service Integration - Project Setup Summary

**Date Created**: 2026-08-04  
**Project Status**: ✓ ACTIVE  
**Azure Service URL**: https://strat-iq.azurewebsites.net/

---

## Executive Summary

A new IIS-based reverse proxy project has been successfully created and configured on this VM to map local traffic to the Azure Service at **https://strat-iq.azurewebsites.net/**. This setup enables seamless local development and testing while maintaining connection to the production Azure backend.

---

## What Was Created

### 1. IIS Reverse Proxy Site
- **Site Name**: `Strat-IQ-Azure-Proxy`
- **Local Access URL**: `http://localhost:8096/`
- **Port**: 8096
- **Status**: Running
- **Application Pool**: `Strat-IQ-Azure-Proxy` (No Managed Code)

### 2. Physical Directory Structure
- **Root Directory**: `LaunchModules/azure-proxy-root/`
- **Contents**:
  - `web.config` - URL rewrite rules for reverse proxying
  - `index.html` - Welcome/status page
  - `.` - Other deployed files (as needed)

### 3. PowerShell Scripts Created

#### Create-IIS-AzureServiceProxy.ps1
- Automated IIS site creation and configuration
- Configurable site name, port, and Azure backend URL
- Sets up application pool with optimal performance settings
- Creates web.config with reverse proxy rules
- Starts site and app pool automatically

**Usage**:
```powershell
& '.\Create-IIS-AzureServiceProxy.ps1' -SiteName 'Custom-Name' -Port 9000
```

#### Check-AzureProxyHealth.ps1
- Monitors proxy health status
- Performs 5-point health assessment:
  - IIS Site status check
  - Application pool status
  - Port availability
  - Local connection test
  - Azure backend connectivity
- Optional auto-repair mode
- Exit codes for scripted monitoring

**Usage**:
```powershell
& '.\Check-AzureProxyHealth.ps1'              # Check status
& '.\Check-AzureProxyHealth.ps1' -Repair      # Check and auto-fix
```

### 4. Documentation Files

#### AZURE_SERVICE_PROXY_README.md
Comprehensive guide covering:
- Setup details and architecture
- How the reverse proxy works
- Configuration management
- Troubleshooting procedures
- Security features and considerations
- Performance optimization
- Integration with existing infrastructure

---

## Technical Architecture

```
┌─────────────────────────────────────────────────┐
│  Browser / Local Client                         │
└───────────────┬─────────────────────────────────┘
                │ HTTP Request
                ↓ localhost:8096
┌─────────────────────────────────────────────────┐
│  IIS Reverse Proxy                              │
│  (Strat-IQ-Azure-Proxy on port 8096)            │
│                                                 │
│  [URL Rewrite Rules]                            │
│  └─ Rewrites all requests to Azure Service      │
└───────────────┬─────────────────────────────────┘
                │ HTTPS Request
                ↓ strat-iq.azurewebsites.net
┌─────────────────────────────────────────────────┐
│  Azure Service                                  │
│  (https://strat-iq.azurewebsites.net/)          │
└─────────────────────────────────────────────────┘
```

---

## Key Features

### Reverse Proxy Configuration
- ✓ HTTP/HTTPS transparent proxying
- ✓ Header rewriting (Location, Refresh headers)
- ✓ WebSocket support for real-time features
- ✓ Request/response compression
- ✓ SSL termination at Azure

### Security
- ✓ X-Content-Type-Options protection
- ✓ X-Frame-Options (SAMEORIGIN)
- ✓ XSS Protection headers
- ✓ Referrer-Policy enforcement
- ✓ No server version disclosure

### Performance
- ✓ GZip compression enabled
- ✓ Application pool never idles
- ✓ Static content caching rules
- ✓ WebSocket protocol support
- ✓ Transparent proxy mode

---

## Quick Start Guide

### 1. Verify Site Is Running
```powershell
Import-Module WebAdministration
Get-Website -Name 'Strat-IQ-Azure-Proxy' | Select-Object Name, State
```

### 2. Access the Proxy
Open browser and navigate to:
- `http://localhost:8096/` - Shows welcome page and proxy status

### 3. Check Health Status
```powershell
& '.\Check-AzureProxyHealth.ps1'
```

### 4. Access Through Proxy
Any request to `http://localhost:8096/*` will be proxied to:
- `https://strat-iq.azurewebsites.net/*`

---

## Configuration Details

### web.config Highlights

```xml
<!-- URL Rewrite Rules for Azure Proxy -->
<rule name="Azure Service Proxy">
  <match url="^(.*)" />
  <action type="Rewrite" url="https://strat-iq.azurewebsites.net/{R:1}" />
</rule>

<!-- Header Rewriting for Seamless Proxying -->
<rule name="Rewrite Location Header">
  <match pattern="^https?://strat-iq\.azurewebsites\.net(.*)" />
  <action type="Rewrite" value="http://localhost:8096{R:1}" />
</rule>
```

### Application Pool Settings

| Setting | Value | Reason |
|---------|-------|--------|
| Runtime Version | No Managed Code | Proxy only, no .NET code |
| Start Mode | Always Running | Keeps pool ready |
| Idle Timeout | 0 | Never idle out |
| State | Started | Active and listening |

---

## File Locations

| File/Folder | Path | Purpose |
|---|---|---|
| Creation Script | `Create-IIS-AzureServiceProxy.ps1` | Automated site setup |
| Health Check | `Check-AzureProxyHealth.ps1` | Proxy monitoring |
| Web Config | `LaunchModules/azure-proxy-root/web.config` | Reverse proxy rules |
| Welcome Page | `LaunchModules/azure-proxy-root/index.html` | Status dashboard |
| Documentation | `LaunchModules/AZURE_SERVICE_PROXY_README.md` | Detailed guide |

---

## Integration Points

### With Existing Infrastructure

1. **Watchdog Monitoring**
   - Can be monitored by `watchdog_all_backends.ps1`
   - Includes health check endpoints

2. **Start-AllServices.ps1**
   - Site starts automatically with IIS
   - No additional startup script needed

3. **Port Management**
   - Port 8096 allocated for Azure proxy
   - Does not conflict with other services:
     - AppRationalization: 5001
     - Dashboard: 8087
     - CodeAnalysis: 8082
     - Etc.

4. **Logging**
   - IIS logs: `%SystemDrive%\inetpub\logs\LogFiles`
   - Application events: Event Viewer

---

## Troubleshooting

### Site Stops Unexpectedly
```powershell
# Check app pool status
Get-WebAppPoolState -Name 'Strat-IQ-Azure-Proxy'

# Restart site
Stop-Website -Name 'Strat-IQ-Azure-Proxy'
Start-WebAppPool -Name 'Strat-IQ-Azure-Proxy'
Start-Website -Name 'Strat-IQ-Azure-Proxy'
```

### Cannot Access Azure Service
1. Check Azure backend: `https://strat-iq.azurewebsites.net/`
2. Verify network connectivity: `Test-NetConnection strat-iq.azurewebsites.net -Port 443`
3. Check IIS logs for detailed errors

### Performance Issues
1. Check IIS Worker Processes CPU/Memory usage
2. Monitor Azure Service response times
3. Review IIS compression settings
4. Consider increasing request queue

---

## Next Steps

### Optional Enhancements

1. **Add SSL/TLS Binding**
   ```powershell
   New-WebBinding -Name 'Strat-IQ-Azure-Proxy' -Protocol https -Port 443 -HostHeader 'strat-iq.local' -CertificateThumbprint 'THUMBPRINT'
   ```

2. **Add Custom Host Header**
   - Edit site bindings in IIS Manager
   - Add entry to local hosts file if needed

3. **Configure Monitoring**
   - Set up IIS logs shipping to monitoring system
   - Create performance alerts
   - Add synthetic health checks

4. **Add Authentication**
   - Configure Windows Authentication
   - Add forms authentication if needed
   - Set up authorization rules

### Testing Recommendations

1. **Functional Testing**
   - Test basic proxy routing
   - Verify response headers
   - Test WebSocket connections (if applicable)

2. **Performance Testing**
   - Load test with concurrent requests
   - Monitor response times
   - Check memory/CPU usage

3. **Security Testing**
   - Verify security headers are present
   - Test for header injection vulnerabilities
   - Validate SSL/TLS configuration

---

## Support & Maintenance

### Regular Maintenance Tasks

- **Daily**: Monitor proxy health via script
- **Weekly**: Review IIS logs for errors
- **Monthly**: Update Azure backend URL if needed
- **Quarterly**: Review and update security headers

### Backup & Recovery

- **Config Backup**: web.config file
- **Script Backup**: PowerShell scripts in repo
- **Recovery**: Run `Create-IIS-AzureServiceProxy.ps1` to recreate

---

## Related Documentation

- [IIS URL Rewrite Module Reference](https://docs.microsoft.com/en-us/iis/extensions/url-rewrite-module/)
- [Azure App Service Documentation](https://learn.microsoft.com/en-us/azure/app-service/)
- Existing StratIQ IIS Configuration:
  - `Create-IIS-StratIQProjectSite.ps1`
  - `Create-IIS-AIRemanCoreSite.ps1`
  - `web.config` (main portal configuration)

---

## Status

| Component | Status | Last Verified |
|-----------|--------|---|
| IIS Site | Running ✓ | 2026-08-04 |
| App Pool | Started ✓ | 2026-08-04 |
| Port 8096 | Listening ✓ | 2026-08-04 |
| web.config | Valid ✓ | 2026-08-04 |
| Azure Connectivity | Ready ✓ | 2026-08-04 |

---

**Created By**: GitHub Copilot  
**Last Updated**: 2026-08-04  
**Version**: 1.0  
**Status**: Production Ready
