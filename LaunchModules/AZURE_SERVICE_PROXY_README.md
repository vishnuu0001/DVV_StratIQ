# Strat-IQ Azure Service Proxy - IIS Configuration

## Overview

This document describes the IIS reverse proxy configuration that maps local traffic on port 8096 to the Azure Service at **https://strat-iq.azurewebsites.net/**.

## Setup Details

### Site Configuration
- **Site Name**: Strat-IQ-Azure-Proxy
- **Local URL**: http://localhost:8096/
- **Port**: 8096 (HTTP)
- **Application Pool**: Strat-IQ-Azure-Proxy
- **Physical Path**: `LaunchModules/azure-proxy-root`

### Azure Service
- **Backend URL**: https://strat-iq.azurewebsites.net/
- **Protocol**: HTTPS

### Configuration Files
- **Creation Script**: `Create-IIS-AzureServiceProxy.ps1`
- **Web Configuration**: `LaunchModules/azure-proxy-root/web.config`
- **Welcome Page**: `LaunchModules/azure-proxy-root/index.html`

## How It Works

The IIS reverse proxy works as follows:

1. **Browser Request**: Client sends HTTP request to `http://localhost:8096/path`
2. **IIS Proxy Layer**: IIS intercepts the request and applies URL rewrite rules
3. **Backend Request**: IIS forwards the request to `https://strat-iq.azurewebsites.net/path`
4. **Response Processing**: Azure Service response headers are rewritten to point back through the proxy
5. **Client Response**: Client receives the proxied response

## Configuration Details

### URL Rewrite Rules

The `web.config` includes the following rules:

1. **Azure Service Proxy Rule**: Rewrites all non-file/non-directory requests to the Azure backend
2. **Location Header Rewrite**: Converts redirect responses from Azure back to local proxy URLs
3. **Refresh Header Rewrite**: Updates refresh headers to use the local proxy

### Security Features

- ✓ X-Content-Type-Options: nosniff (prevents MIME type sniffing)
- ✓ X-Frame-Options: SAMEORIGIN (clickjacking protection)
- ✓ X-XSS-Protection: 1; mode=block (XSS protection)
- ✓ Referrer-Policy: strict-origin-when-cross-origin
- ✓ WebSocket support enabled

### Performance Features

- ✓ GZip compression for text/JSON responses
- ✓ Application pool set to AlwaysRunning (no idle timeout)
- ✓ Response header rewriting for transparent proxying

## Managing the Site

### Start the Site
```powershell
Start-Website -Name 'Strat-IQ-Azure-Proxy'
```

### Stop the Site
```powershell
Stop-Website -Name 'Strat-IQ-Azure-Proxy'
```

### Check Site Status
In IIS Manager, locate "Strat-IQ-Azure-Proxy" and verify the status is "Started" (green).

### View Application Pool
- **Name**: Strat-IQ-Azure-Proxy
- **Status**: Should be "Started" (green)
- **Runtime Version**: No Managed Code (empty string)
- **Idle Timeout**: 0 (never idle out)

## Troubleshooting

### Site Returns 500 Error
1. Check IIS Application Pool status
2. Review Event Viewer for IIS errors: Event Viewer → Windows Logs → System
3. Check proxy connectivity: `Test-NetConnection strat-iq.azurewebsites.net -Port 443`

### Blank Page or Missing Content
1. Verify Azure Service is accessible: `https://strat-iq.azurewebsites.net/`
2. Check web.config syntax errors in IIS Manager
3. Review IIS logs: `%SystemDrive%\inetpub\logs\LogFiles`

### WebSocket Connection Issues
- Ensure WebSocket Protocol feature is enabled in IIS
- Check that the Azure Service accepts WebSocket connections
- Review IIS configuration: `<webSocket enabled="true" />`

## Adding Host Headers

To add a custom host header (e.g., `strat-iq.local`):

1. Open IIS Manager
2. Select "Strat-IQ-Azure-Proxy" site
3. In the right panel, click "Bindings..."
4. Click "Add..." and configure:
   - Type: http
   - Port: 8096
   - Host name: `strat-iq.local`
5. Click OK and update your hosts file if needed

## Modifying Proxy Rules

To add custom proxy rules:

1. Edit `LaunchModules/azure-proxy-root/web.config`
2. Add new `<rule>` entries in the `<rewrite>` section
3. Save the file
4. Restart IIS: `iisreset`

Example: Proxy specific path to different backend
```xml
<rule name="Custom Route" stopProcessing="true">
  <match url="^special/(.*)" />
  <action type="Rewrite" url="https://other-service.azurewebsites.net/api/{R:1}" />
</rule>
```

## Scripted Management

### Recreate Site with Custom Port
```powershell
& '.\Create-IIS-AzureServiceProxy.ps1' -SiteName 'MyProxy' -Port 9000
```

### Recreate Site with Host Header
```powershell
& '.\Create-IIS-AzureServiceProxy.ps1' -HostHeader 'strat-iq.local'
```

### Use Different Azure Backend
```powershell
& '.\Create-IIS-AzureServiceProxy.ps1' -AzureServiceUrl 'https://other-service.azurewebsites.net'
```

## Performance Monitoring

Monitor site performance through IIS Manager:

1. Open IIS Manager
2. Select "Strat-IQ-Azure-Proxy"
3. Double-click "Worker Processes"
4. View CPU and Memory usage

## Security Considerations

- ⚠️ **Certificates**: For production, configure HTTPS bindings
- ⚠️ **Authentication**: Configure Windows/Forms auth if needed
- ⚠️ **Rate Limiting**: Consider adding rate limiting rules
- ⚠️ **WAF Rules**: If using Azure WAF, ensure it's configured properly

## Integration with SCM Infrastructure

This proxy can be integrated with the existing infrastructure:

- **Watchdog**: Can be monitored by `watchdog_all_backends.ps1`
- **Health Checks**: Add to `Start-AllServices.ps1`
- **Logging**: Logs appear in `%SystemDrive%\inetpub\logs\LogFiles`

## Related Files

- Main Web Configuration: `web.config`
- Other IIS Scripts:
  - `Create-IIS-StratIQProjectSite.ps1`
  - `Create-IIS-AIRemanCoreSite.ps1`
  - `IIS-Deployment-Automation.ps1`
- Startup Scripts: `Start-AllServices.ps1`

## Maintenance

### Regular Checks
- ✓ Verify site status weekly
- ✓ Review IIS logs monthly for errors
- ✓ Test Azure backend connectivity monthly
- ✓ Monitor application pool restarts

### Updates
- If Azure Service URL changes, re-run the script with new URL
- If port conflicts occur, update the `-Port` parameter
- If additional proxy rules needed, update web.config

---

**Last Updated**: 2026-08-04  
**Created By**: GitHub Copilot  
**Status**: Active ✓
