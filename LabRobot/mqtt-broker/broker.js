// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: LabRobot — mqtt-broker (broker.js)
// Date: 2025-08-20
// ---------------------------------------------------------------------------
const Aedes = require('aedes')
const { createServer } = require('aedes-server-factory')

const aedes = Aedes()

const TCP_PORT = Number(process.env.MQTT_TCP_PORT || 1883)
const WS_PORT = Number(process.env.MQTT_WS_PORT || 9001)

const tcpServer = createServer(aedes)
const wsServer = createServer(aedes, { ws: true })

// Bind explicitly to 0.0.0.0 — the default listen() bound IPv6-only ("::")
// on this host, which silently drops IPv4 "localhost" clients (both the
// browser's ws:// client and the Python backend's paho-mqtt client).
tcpServer.listen(TCP_PORT, '0.0.0.0', () => {
  console.log(`[mqtt-broker] TCP listening on 0.0.0.0:${TCP_PORT}`)
})

wsServer.listen(WS_PORT, '0.0.0.0', () => {
  console.log(`[mqtt-broker] WebSocket listening on 0.0.0.0:${WS_PORT}`)
})

aedes.on('client', (client) => {
  console.log(`[mqtt-broker] client connected: ${client.id}`)
})

aedes.on('clientError', (client, err) => {
  console.log(`[mqtt-broker] clientError: ${client ? client.id : '?'} — ${err.message}`)
})

aedes.on('connectionError', (client, err) => {
  console.log(`[mqtt-broker] connectionError: ${client ? client.id : '?'} — ${err.message}`)
})

aedes.on('connackSent', (packet, client) => {
  console.log(`[mqtt-broker] connackSent to ${client ? client.id : '?'}`)
})

aedes.on('clientDisconnect', (client) => {
  console.log(`[mqtt-broker] client disconnected: ${client.id}`)
})

aedes.on('publish', (packet, client) => {
  if (client && !packet.topic.startsWith('$SYS')) {
    console.log(`[mqtt-broker] ${client.id} -> ${packet.topic}: ${packet.payload.toString().slice(0, 200)}`)
  }
})

process.on('SIGTERM', () => {
  tcpServer.close()
  wsServer.close()
  process.exit(0)
})
