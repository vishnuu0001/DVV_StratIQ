#!/bin/bash
# Start the Azure Proxy Server
# This script starts the Node.js reverse proxy on port 8097

cd "$(dirname "$0")"

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║    Starting Strat-IQ Azure Reverse Proxy Server    ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

node proxy-server.js
