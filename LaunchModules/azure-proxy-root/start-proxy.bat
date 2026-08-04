@echo off
REM Start the Azure Proxy Server
REM This script starts the Node.js reverse proxy on port 8097

cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════════════════╗
echo ║    Starting Strat-IQ Azure Reverse Proxy Server    ║
echo ╚════════════════════════════════════════════════════╝
echo.

node proxy-server.js

pause
