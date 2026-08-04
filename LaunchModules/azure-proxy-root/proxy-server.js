#!/usr/bin/env node
/**
 * Reverse Proxy Server for Strat-IQ Azure Service
 * Forwards requests to https://strat-iq.azurewebsites.net/
 * Falls back to status page if Azure is unavailable
 */

const http = require('http');
const https = require('https');
const url = require('url');

const AZURE_HOST = 'strat-iq.azurewebsites.net';
const AZURE_URL = `https://${AZURE_HOST}`;
const LISTEN_PORT = 8097;

// Status page HTML
const statusPageHTML = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Strat-IQ Proxy Status</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 600px;
            text-align: center;
        }
        h1 { color: #333; margin-bottom: 10px; font-size: 28px; }
        .status { font-size: 18px; margin-bottom: 20px; font-weight: 500; }
        .warning { color: #e74c3c; }
        .success { color: #27ae60; }
        .info { background: #f8f9fa; border-left: 4px solid #667eea; padding: 15px; margin: 20px 0; border-radius: 4px; text-align: left; }
        .info dt { font-weight: 600; color: #333; margin-top: 10px; }
        .info dd { color: #666; margin-left: 0; }
        code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
        .timestamp { color: #999; font-size: 12px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔄 Strat-IQ Reverse Proxy</h1>
        <div class="status warning">⚠ Azure Service Unavailable</div>
        
        <div class="info">
            <dl>
                <dt>Backend Service:</dt>
                <dd><code>https://strat-iq.azurewebsites.net/</code></dd>
                
                <dt>Local Proxy:</dt>
                <dd><code>http://localhost:8097/</code></dd>
                
                <dt>Status:</dt>
                <dd>Azure service is currently disabled or unreachable (HTTP 403)</dd>
                
                <dt>What to do:</dt>
                <dd>
                    1. Check if Azure App Service is enabled<br>
                    2. Verify Azure credentials and permissions<br>
                    3. Check Azure portal for service status<br>
                    4. The proxy will automatically work when Azure comes online
                </dd>
            </dl>
        </div>
        
        <p style="color: #666; margin-top: 20px;">This proxy server forwards all requests to the Azure backend when available.</p>
        
        <div class="timestamp">Proxy Time: <span id="timestamp"></span></div>
    </div>
    
    <script>
        document.getElementById('timestamp').textContent = new Date().toISOString();
    </script>
</body>
</html>`;

/**
 * Test Azure connectivity
 */
function testAzureConnectivity(callback) {
    const options = {
        hostname: AZURE_HOST,
        port: 443,
        path: '/',
        method: 'HEAD',
        timeout: 5000
    };

    const req = https.request(options, (res) => {
        // Only consider 2xx and 3xx as "available"
        // 4xx and 5xx indicate service issues or disabled state
        const isAvailable = res.statusCode < 400;
        callback(isAvailable, res.statusCode);
    });

    req.on('timeout', () => {
        req.destroy();
        callback(false, null);
    });

    req.on('error', () => {
        callback(false, null);
    });

    req.end();
}

/**
 * Proxy request to Azure
 */
function proxyRequest(req, res, azureUrl) {
    const parsedUrl = new URL(req.url, AZURE_URL);
    
    const options = {
        hostname: AZURE_HOST,
        port: 443,
        path: parsedUrl.pathname + parsedUrl.search,
        method: req.method,
        headers: {
            ...req.headers,
            'host': AZURE_HOST,
            'x-forwarded-for': req.socket.remoteAddress,
            'x-forwarded-proto': 'https',
            'x-forwarded-host': req.headers.host
        },
        timeout: 10000
    };

    // Remove unsupported headers
    delete options.headers['connection'];
    delete options.headers['content-length'];

    const proxyReq = https.request(options, (azureRes) => {
        res.writeHead(azureRes.statusCode, azureRes.headers);
        azureRes.pipe(res);
    });

    proxyReq.on('error', (error) => {
        console.error(`[ERROR] Proxy request failed: ${error.message}`);
        res.writeHead(503, { 'Content-Type': 'text/html' });
        res.end(statusPageHTML);
    });

    proxyReq.on('timeout', () => {
        proxyReq.destroy();
        res.writeHead(504, { 'Content-Type': 'text/html' });
        res.end('<h1>504 Gateway Timeout</h1><p>Azure service did not respond in time.</p>');
    });

    if (req.method !== 'GET' && req.method !== 'HEAD') {
        req.pipe(proxyReq);
    } else {
        proxyReq.end();
    }
}

/**
 * Main server
 */
const server = http.createServer((req, res) => {
    // Log request
    console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);

    // Handle favicon
    if (req.url === '/favicon.ico') {
        res.writeHead(404);
        res.end();
        return;
    }

    // Test Azure connectivity
    testAzureConnectivity((isConnected, statusCode) => {
        if (isConnected) {
            // Forward to Azure
            console.log(`[PROXY] Forwarding to Azure (status: ${statusCode})`);
            proxyRequest(req, res, AZURE_URL);
        } else {
            // Show status page
            console.log('[PROXY] Azure unreachable, showing status page');
            res.writeHead(503, { 'Content-Type': 'text/html' });
            res.end(statusPageHTML);
        }
    });
});

server.listen(LISTEN_PORT, () => {
    console.log(`
╔════════════════════════════════════════════════════╗
║    Strat-IQ Azure Reverse Proxy Server             ║
╚════════════════════════════════════════════════════╝

Proxy Server started:
  Local Address:  http://localhost:${LISTEN_PORT}/
  Azure Backend:  ${AZURE_URL}/
  
All requests to localhost:${LISTEN_PORT} will be forwarded to:
  ${AZURE_URL}/

Status:
  - Testing Azure connectivity on each request
  - Falls back to status page if Azure is unavailable
  - Logs all activity to console

Ctrl+C to stop the server
`);
});

server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
        console.error(`[ERROR] Port ${LISTEN_PORT} is already in use!`);
        console.error(`Try killing the process using: netstat -ano | findstr :${LISTEN_PORT}`);
    } else {
        console.error(`[ERROR] Server error: ${err.message}`);
    }
    process.exit(1);
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n[INFO] Shutting down proxy server...');
    server.close(() => {
        console.log('[INFO] Proxy server stopped');
        process.exit(0);
    });
});
