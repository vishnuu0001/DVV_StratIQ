// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: LabRobot — frontend/src/components (FactoryOrchestration3D.jsx)
// Date: 2025-09-09
// ---------------------------------------------------------------------------
import { Suspense, useEffect, useMemo, useRef, useState } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { Html, OrbitControls } from '@react-three/drei'
import * as THREE from 'three'

// ─── Room dimensions — a long factory bay housing all six pipeline stages ──
const ROOM_WIDTH = 34
const ROOM_DEPTH = 9
const WALL_HEIGHT = 5.5

// ─── Six-stage pipeline definition ─────────────────────────────────────────
// Station names/taglines describe the *pattern* (simulate → inspect → build
// → move → validate → control) rather than naming specific third-party
// vendor products, since this is a generic training-simulator feature, not
// a claim of real integrations with those vendors.
// `topic` / `tag` name the simulated MQTT channel and PLC I/O block each
// stage's controller would own on a real line; `startAction`/`completeAction`
// describe the physical action the local controller reports back once the
// command is accepted — used to build the protocol log below.
const STAGES = [
  {
    key: 'simulate', n: 1, name: 'Simulate', tagline: 'Design before you build',
    system: 'Digital twin simulation', color: '#38bdf8',
    challenge: 'Ramp-up delays & commissioning inefficiencies',
    outcome: '60% faster virtual commissioning',
    x: -13.5, topic: 'factory/simulate', tag: 'PLC1',
    startAction: 'Digital twin simulation started',
    completeAction: 'Simulation results committed to twin',
    steps: [
      {
        n: 1, title: 'Import digital layout', anim: 'assemble',
        description: 'CAD and floor-plan data are pulled into the digital twin and aligned to the physical cell before any commissioning begins.',
        metric: 'Parts aligned: 128 / 128', signal: 'PLC1.X1 → 1',
      },
      {
        n: 2, title: 'Run physics & motion simulation', anim: 'pulseGrid',
        description: 'The twin runs cycle-time, reach, and collision simulations so problems surface in software, not on the floor.',
        metric: 'Simulated cycles: 240 · Collisions: 0', signal: 'PLC1.X2 → 1',
      },
      {
        n: 3, title: 'Validate & commit', anim: 'gauge',
        description: 'Predicted cycle time is checked against the target and, once inside tolerance, the plan is committed for real commissioning.',
        metric: 'Cycle time: 38.4s (target 40s)', signal: 'factory/simulate/status',
      },
    ],
  },
  {
    key: 'inspect', n: 2, name: 'Inspect', tagline: 'Quality at entry, not exit',
    system: 'Automated vision inspection', color: '#60a5fa',
    challenge: 'Quality escapes, FOD, rework & defects',
    outcome: 'Up to 99% defect detection accuracy',
    x: -8.1, topic: 'factory/inspect', tag: 'PLC2',
    startAction: 'Vision inspection scan started',
    completeAction: 'Inspection verdict recorded: PASS',
    steps: [
      {
        n: 1, title: 'Position & scan part', anim: 'scanBeam',
        description: 'The incoming part is indexed under the vision system and a structured-light scan captures its full surface in one pass.',
        metric: 'Scan resolution: 2560 × 2048 · Coverage: 100%', signal: 'PLC2.X1 → 1',
      },
      {
        n: 2, title: 'AI defect analysis', anim: 'defectGrid',
        description: 'A trained model compares the scan against the golden reference, flagging any region outside tolerance for review.',
        metric: 'Regions checked: 9 · Flagged: 1 → cleared', signal: 'PLC2.X2 → 1',
      },
      {
        n: 3, title: 'Verdict recorded', anim: 'stamp',
        description: 'The inspection verdict is stamped, logged, and released back to the line — quality is checked at entry, not after the fact.',
        metric: 'Verdict: PASS · Confidence 99.4%', signal: 'factory/inspect/status',
      },
    ],
  },
  {
    key: 'build', n: 3, name: 'Build', tagline: 'Adaptive manufacturing, redefined',
    system: 'Tightening · harnessing · finishing cell', color: '#f97316',
    challenge: 'Workforce gaps, complex assemblies, operator errors',
    outcome: '80% higher quality · 50% faster training',
    x: -2.7, topic: 'factory/build', tag: 'PLC3',
    startAction: 'Tightening / harnessing cycle started',
    completeAction: 'Assembly cycle completed',
    steps: [
      {
        n: 1, title: 'Position & clamp part', anim: 'waypoint',
        description: 'The part is indexed into the fixture and clamped before any tool touches it, so every cycle starts from the same reference.',
        metric: 'Clamp force: 420N · Position error: 0.03mm', signal: 'PLC3.X1 → 1',
      },
      {
        n: 2, title: 'Tighten / harness / finish', anim: 'tapArm',
        description: 'The adaptive tool executes the tightening, wire-harnessing, or finishing sequence for this part variant.',
        metric: 'Fasteners driven: 6 / 6', signal: 'PLC3.Y0 → 1',
      },
      {
        n: 3, title: 'Torque / quality verification', anim: 'gauge',
        description: 'Each fastener is verified against its torque spec in real time — an out-of-spec result halts the cell before the part moves on.',
        metric: 'Torque: 12.4 N·m (spec 12.0–13.0)', signal: 'PLC3.X3 → 1',
      },
    ],
  },
  {
    key: 'move', n: 4, name: 'Move', tagline: 'Material flows itself',
    system: 'Autonomous mobile robot', color: '#fbbf24',
    challenge: 'Material flow delays, logistics, missing components',
    outcome: '30–40% improvement in material flow efficiency',
    x: 2.7, topic: 'factory/move', tag: 'PLC4',
    startAction: 'AMR dispatched from bay',
    completeAction: 'AMR arrived, payload released',
    steps: [
      {
        n: 1, title: 'Dispatch AMR', anim: 'signal',
        description: 'The orchestrator assigns a pickup job to the nearest available AMR and reserves the destination slot.',
        metric: 'ETA: 4.5s · Battery: 92%', signal: 'factory/move/cmd',
      },
      {
        n: 2, title: 'Navigate to destination', anim: 'waypoint',
        description: 'The AMR follows its planned route, replanning live if the path ahead is blocked.',
        metric: 'Distance remaining: 3.6m', signal: 'PLC4.X1 → 1',
      },
      {
        n: 3, title: 'Dock & handoff payload', anim: 'stamp',
        description: 'The AMR docks at the destination station and releases the payload, confirmed by the station’s presence sensor.',
        metric: 'Handoff confirmed', signal: 'PLC4.X2 → 1',
      },
    ],
  },
  {
    key: 'validate', n: 5, name: 'Validate', tagline: 'Every part, fully traceable',
    system: 'Mobile validation robot', color: '#34d399',
    challenge: 'Lack of traceability, audit readiness compliance',
    outcome: '100% traceability, zero defect escape',
    x: 8.1, topic: 'factory/validate', tag: 'PLC5',
    startAction: 'Traceability scan started',
    completeAction: 'Validation record committed to ledger',
    steps: [
      {
        n: 1, title: 'Scan part ID / traceability tag', anim: 'scanBeam',
        description: 'The part’s serial tag is scanned and matched against its build record.',
        metric: 'Tag read: 1 / 1', signal: 'PLC5.X1 → 1',
      },
      {
        n: 2, title: 'Cross-check ledger', anim: 'dataRows',
        description: 'Every upstream process step — simulate, inspect, build, move — is checked off against the traceability ledger for this part.',
        metric: 'Steps verified: 4 / 4', signal: 'PLC5.X2 → 1',
      },
      {
        n: 3, title: 'Compliance sign-off', anim: 'stamp',
        description: 'A signed, timestamped record is committed — full genealogy from raw material to finished part, with zero gaps.',
        metric: 'Ledger entry committed', signal: 'factory/validate/status',
      },
    ],
  },
  {
    key: 'control', n: 6, name: 'Control', tagline: 'The factory that thinks',
    system: 'Factory command center', color: '#a78bfa',
    challenge: 'End-to-end factory visibility and control',
    outcome: 'Real-time decisions, better OEE, lower downtime',
    x: 13.5, topic: 'factory/control', tag: 'PLC6',
    startAction: 'Dashboard sync started',
    completeAction: 'KPIs published to command center',
    steps: [
      {
        n: 1, title: 'Aggregate live KPIs', anim: 'barChart',
        description: 'Throughput, quality, and downtime from every stage roll up into the command center in real time.',
        metric: 'OEE: 87.2%', signal: 'factory/control/kpi',
      },
      {
        n: 2, title: 'Anomaly detection', anim: 'barChart', variant: 'anomaly',
        description: 'The system flags stages trending outside their normal band before they become a line stoppage.',
        metric: 'Anomaly: Build cycle time +8%', signal: 'PLC6.X1 → 1',
      },
      {
        n: 3, title: 'Dispatch decision to line', anim: 'signal',
        description: 'A corrective action — reroute, re-balance, or alert — is sent back down to the affected stage, closing the AI feedback loop.',
        metric: 'Decision dispatched to: Build', signal: 'factory/control/cmd',
      },
    ],
  },
]

const STATUS_COLOR = { idle: '#64748b', running: '#f59e0b', done: '#22c55e' }

const DIVIDER_XS = STAGES.slice(0, -1).map((s, i) => (s.x + STAGES[i + 1].x) / 2)

// ─── Simulated communication protocol log ──────────────────────────────
// Every stage transition is modeled as a real orchestration handshake would
// look: an MQTT command is published to the stage's topic, the stage's
// local controller subscribes and acknowledges it, and the actual physical
// action is reported back over the PLC's discrete I/O block. The same
// three-step shape (triggered → received/accepted → action performed) plays
// out again in reverse when the stage reports completion.
const EVENT_KIND = {
  pub: { label: 'MQTT · PUB', color: '#38bdf8' },
  sub: { label: 'MQTT · SUB', color: '#2dd4bf' },
  plc: { label: 'PLC · I/O', color: '#f59e0b' },
}

let eventSeq = 0
// Function: buildEvents
function buildEvents(stage, phase) {
  const base = Date.now()
  // Function: mk
  const mk = (offsetMs, kind, topic, payload, note) => ({
    id: `evt-${eventSeq++}`,
    stageKey: stage.key,
    stageName: stage.name,
    time: base + offsetMs,
    kind,
    topic,
    payload,
    note,
  })
  if (phase === 'start') {
    return [
      mk(0, 'pub', `${stage.topic}/cmd`, '{"cmd":"start"}', 'Command triggered'),
      mk(120, 'sub', `${stage.topic}/ack`, '{"status":"accepted"}', 'Command received & accepted'),
      mk(260, 'plc', `${stage.tag}.Y0`, '1', stage.startAction),
    ]
  }
  return [
    mk(0, 'plc', `${stage.tag}.X0`, '1', stage.completeAction),
    mk(120, 'pub', `${stage.topic}/status`, '{"status":"complete"}', 'Status published'),
    mk(260, 'sub', 'factory/orchestrator/ack', '{"received":true}', 'Orchestrator acknowledged'),
  ]
}

const OVERVIEW = { position: [0, 10, 24], target: [0, 1.6, 0] }

// ─── Per-stage inspection angles ────────────────────────────────────────
// Offsets are relative to the focused subject's (x, z) position, so every
// stage — and the moving AMR — gets the same four well-composed views.
// Z offsets are stored as deltas from the subject's own z (STATION_Z for
// the five fixed stations, FLOW_Z for the traveling cart), not as absolute
// world coordinates — otherwise a camera tuned for a station sitting at
// z=-1.4 aims at the wrong depth entirely for a subject sitting at the
// flow line's z=+1.3, and the subject never appears in frame even though
// the x-tracking is correct.
const STATION_Z = -1.4
const STAGE_ANGLES = {
  close: { label: 'Close-up', posOffset: [0, 1.75], posDeltaZ: 3.7, lookOffset: [0, 1.15], lookDeltaZ: 0.1 },
  front: { label: 'Front', posOffset: [0, 2.6], posDeltaZ: 6.2, lookOffset: [0, 1.3], lookDeltaZ: 0 },
  side: { label: 'Side', posOffset: [2.6, 2.0], posDeltaZ: 2.4, lookOffset: [-0.8, 1.1], lookDeltaZ: 0 },
  top: { label: 'Top', posOffset: [0, 6.5], posDeltaZ: 1.7, lookOffset: [0, 0.9], lookDeltaZ: 0 },
}
const STAGE_ANGLE_ORDER = ['close', 'front', 'side', 'top']

// Function: cameraPresetFor
function cameraPresetFor(subjectX, angleKey, subjectZ = STATION_Z) {
  if (subjectX == null) return OVERVIEW
  const angle = STAGE_ANGLES[angleKey] || STAGE_ANGLES.close
  return {
    position: [subjectX + angle.posOffset[0], angle.posOffset[1], subjectZ + angle.posDeltaZ],
    target: [subjectX + angle.lookOffset[0], angle.lookOffset[1], subjectZ + angle.lookDeltaZ],
  }
}

const FLOW_Z = 1.3
const FLOW_START_X = -15
const FLOW_END_X = 15

// ─── Floating stage label + status dot ─────────────────────────────────────
// Function: StationLabel
function StationLabel({ x, n, name, status }) {
  const color = STATUS_COLOR[status]
  return (
    <Html position={[x, 2.75, -1.35]} center distanceFactor={9}>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3, pointerEvents: 'none' }}>
        <div
          style={{
            fontFamily: 'ui-monospace, Consolas, monospace',
            fontSize: 10,
            letterSpacing: '0.08em',
            color: '#dbeafe',
            background: 'rgba(8, 12, 20, 0.88)',
            border: `1px solid ${color}`,
            borderRadius: 4,
            padding: '3px 8px',
            whiteSpace: 'nowrap',
          }}
        >
          {n}. {name.toUpperCase()}
        </div>
        <div style={{ width: 7, height: 7, borderRadius: '50%', background: color, boxShadow: `0 0 8px ${color}` }} />
      </div>
    </Html>
  )
}

// ─── Stage 1 — Simulate: desk + monitor + rotating "digital twin" wireframe ─
// Function: SimulateStation
function SimulateStation({ x, status }) {
  const cubeRef = useRef(null)
  const screenRef = useRef(null)

  useFrame((state, delta) => {
    const spin = status === 'running' ? 2.2 : 0.5
    if (cubeRef.current) {
      cubeRef.current.rotation.y += delta * spin
      cubeRef.current.rotation.x += delta * spin * 0.6
    }
    if (screenRef.current) {
      const t = state.clock.elapsedTime
      const pulse = status === 'running' ? 0.55 + Math.sin(t * 5) * 0.25 : status === 'done' ? 0.5 : 0.22
      screenRef.current.material.emissiveIntensity = pulse
    }
  })

  return (
    <group position={[x, 0, -1.4]}>
      <mesh castShadow receiveShadow position={[0, 0.42, 0]}>
        <boxGeometry args={[1.3, 0.06, 0.6]} />
        <meshStandardMaterial color="#334155" metalness={0.4} roughness={0.5} />
      </mesh>
      {[[-0.55, -0.22], [0.55, -0.22], [-0.55, 0.22], [0.55, 0.22]].map(([dx, dz], i) => (
        <mesh key={i} position={[dx, 0.21, dz]}>
          <boxGeometry args={[0.05, 0.42, 0.05]} />
          <meshStandardMaterial color="#1e293b" />
        </mesh>
      ))}
      <mesh position={[0, 1.35, -0.56]}>
        <planeGeometry args={[1.6, 1.0]} />
        <meshStandardMaterial color="#0f172a" />
      </mesh>
      <mesh ref={screenRef} position={[0, 1.35, -0.55]}>
        <planeGeometry args={[1.5, 0.9]} />
        <meshStandardMaterial color="#0ea5e9" emissive="#0ea5e9" emissiveIntensity={0.3} toneMapped={false} />
      </mesh>
      <mesh ref={cubeRef} position={[0, 0.95, 0.05]}>
        <boxGeometry args={[0.4, 0.4, 0.4]} />
        <meshStandardMaterial color="#38bdf8" wireframe />
      </mesh>
    </group>
  )
}

// ─── Stage 2 — Inspect: workbench + sliding scanner head + verdict monitor ──
// Function: InspectStation
function InspectStation({ x, status }) {
  const scanRef = useRef(null)
  const monitorColor = status === 'done' ? '#22c55e' : status === 'running' ? '#f59e0b' : '#334155'

  useFrame((state) => {
    if (scanRef.current) {
      const t = state.clock.elapsedTime
      scanRef.current.position.x = status === 'running' ? Math.sin(t * 3.2) * 0.42 : 0
    }
  })

  return (
    <group position={[x, 0, -1.4]}>
      <mesh castShadow receiveShadow position={[0, 0.4, 0]}>
        <boxGeometry args={[1.2, 0.06, 0.7]} />
        <meshStandardMaterial color="#475569" />
      </mesh>
      {[[-0.5, -0.28], [0.5, -0.28], [-0.5, 0.28], [0.5, 0.28]].map(([dx, dz], i) => (
        <mesh key={i} position={[dx, 0.2, dz]}>
          <boxGeometry args={[0.05, 0.4, 0.05]} />
          <meshStandardMaterial color="#1e293b" />
        </mesh>
      ))}
      <mesh position={[0, 0.46, 0]} castShadow>
        <boxGeometry args={[0.28, 0.14, 0.28]} />
        <meshStandardMaterial color="#94a3b8" metalness={0.5} roughness={0.4} />
      </mesh>
      <mesh position={[0, 1.15, 0]}>
        <boxGeometry args={[1.0, 0.06, 0.06]} />
        <meshStandardMaterial color="#1e293b" />
      </mesh>
      <mesh ref={scanRef} position={[0, 1.0, 0]}>
        <sphereGeometry args={[0.06, 12, 12]} />
        <meshStandardMaterial color="#f43f5e" emissive="#f43f5e" emissiveIntensity={status === 'running' ? 0.9 : 0.25} toneMapped={false} />
      </mesh>
      <mesh position={[-0.75, 1.0, -0.3]} rotation={[0, 0.5, 0]}>
        <planeGeometry args={[0.42, 0.3]} />
        <meshStandardMaterial color={monitorColor} emissive={monitorColor} emissiveIntensity={0.6} toneMapped={false} />
      </mesh>
    </group>
  )
}

// ─── Stage 3 — Build: fixture table + pivoting pick arm ────────────────────
// Function: BuildStation
function BuildStation({ x, status }) {
  const armRef = useRef(null)
  const itemColor = status === 'done' ? '#22c55e' : '#f97316'

  useFrame((state, delta) => {
    if (!armRef.current) return
    const target = status === 'running' ? Math.sin(state.clock.elapsedTime * 3.5) * 0.4 + 0.55 : 0.15
    armRef.current.rotation.x += (target - armRef.current.rotation.x) * Math.min(delta * 4, 1)
  })

  return (
    <group position={[x, 0, -1.4]}>
      <mesh castShadow receiveShadow position={[0, 0.38, 0]}>
        <boxGeometry args={[1.1, 0.06, 0.9]} />
        <meshStandardMaterial color="#475569" />
      </mesh>
      {[[-0.45, -0.35], [0.45, -0.35], [-0.45, 0.35], [0.45, 0.35]].map(([dx, dz], i) => (
        <mesh key={i} position={[dx, 0.19, dz]}>
          <boxGeometry args={[0.05, 0.38, 0.05]} />
          <meshStandardMaterial color="#1e293b" />
        </mesh>
      ))}
      <mesh position={[-0.25, 0.62, 0.15]} castShadow>
        <cylinderGeometry args={[0.08, 0.09, 0.5, 12]} />
        <meshStandardMaterial color="#ea580c" metalness={0.4} roughness={0.4} />
      </mesh>
      <group position={[-0.25, 0.87, 0.15]} ref={armRef}>
        <mesh position={[0, 0.22, 0]} castShadow>
          <capsuleGeometry args={[0.06, 0.4, 4, 10]} />
          <meshStandardMaterial color="#e2e8f0" />
        </mesh>
        <mesh position={[0, 0.42, 0]}>
          <boxGeometry args={[0.1, 0.08, 0.1]} />
          <meshStandardMaterial color={itemColor} emissive={itemColor} emissiveIntensity={0.35} />
        </mesh>
      </group>
    </group>
  )
}

// ─── The AMR cart — carries the material through the WHOLE pipeline ───────
// This is a single object (not one abstract "item" plus a separately-
// confined Move-stage robot): the same cart departs Simulate the moment it
// completes, glides to Inspect, rests, glides to Build, rests, glides
// through its own Move bay, rests, glides to Validate, rests, glides to
// Control. Position is a pure function of `activeIndex`/`sequencerOn`,
// re-evaluated every frame at a fixed constant speed — no elapsed-time
// bookkeeping to fall out of sync with the stage cards.
const CART_SPEED = 2.4 // world units per second — a clearly visible, unhurried glide

// Function: TravelingCart
function TravelingCart({ activeIndex, sequencerOn, cartXRef }) {
  const cartRef = useRef(null)
  const wheelRefs = useRef([])
  const glowRef = useRef(null)
  const beaconRef = useRef(null)
  const xRef = useRef(STAGES[0].x)

  useFrame((_, delta) => {
    const running = sequencerOn && activeIndex >= 0
    if (cartRef.current) cartRef.current.visible = running
    if (glowRef.current) glowRef.current.visible = running
    if (!running) return

    const targetX = STAGES[activeIndex].x
    const step = CART_SPEED * delta
    if (xRef.current < targetX) xRef.current = Math.min(xRef.current + step, targetX)
    else if (xRef.current > targetX) xRef.current = Math.max(xRef.current - step, targetX)
    const moving = xRef.current !== targetX

    if (cartRef.current) cartRef.current.position.x = xRef.current
    if (glowRef.current) glowRef.current.position.x = xRef.current
    if (cartXRef) cartXRef.current = xRef.current
    if (beaconRef.current) {
      const c = moving ? STATUS_COLOR.running : STATUS_COLOR.done
      beaconRef.current.material.color.set(c)
      beaconRef.current.material.emissive.set(c)
    }
    const spin = moving ? 3.2 : 0.3
    wheelRefs.current.forEach((w) => { if (w) w.rotation.x += delta * spin })
  })

  return (
    <group>
      {/* soft floor glow trailing the cart so its position reads clearly from any angle */}
      <mesh ref={glowRef} position={[STAGES[0].x, 0.012, FLOW_Z]} rotation={[-Math.PI / 2, 0, 0]} visible={false}>
        <circleGeometry args={[0.55, 24]} />
        <meshBasicMaterial color="#fbbf24" transparent opacity={0.22} depthWrite={false} />
      </mesh>
      <group ref={cartRef} position={[STAGES[0].x, 0, FLOW_Z]} visible={false}>
        <mesh castShadow receiveShadow position={[0, 0.24, 0]}>
          <boxGeometry args={[0.62, 0.3, 0.46]} />
          <meshStandardMaterial color="#f59e0b" metalness={0.3} roughness={0.5} />
        </mesh>
        <mesh castShadow receiveShadow position={[0, 0.46, 0]}>
          <boxGeometry args={[0.36, 0.2, 0.36]} />
          <meshStandardMaterial color="#0ea5e9" emissive="#0ea5e9" emissiveIntensity={0.3} toneMapped={false} />
        </mesh>
        {[[-0.24, -0.19], [0.24, -0.19], [-0.24, 0.19], [0.24, 0.19]].map(([dx, dz], i) => (
          <mesh key={i} ref={(el) => { wheelRefs.current[i] = el }} position={[dx, 0.09, dz]} rotation={[0, 0, Math.PI / 2]}>
            <cylinderGeometry args={[0.09, 0.09, 0.07, 16]} />
            <meshStandardMaterial color="#111827" />
          </mesh>
        ))}
        <mesh ref={beaconRef} position={[0, 0.64, 0]}>
          <sphereGeometry args={[0.05, 10, 10]} />
          <meshStandardMaterial color={STATUS_COLOR.running} emissive={STATUS_COLOR.running} emissiveIntensity={0.8} toneMapped={false} />
        </mesh>
      </group>
    </group>
  )
}

// ─── Stage 5 — Validate: quadruped body + tablet-on-stand ──────────────────
// Function: ValidateStation
function ValidateStation({ x, status }) {
  const bodyRef = useRef(null)
  const tabletColor = status === 'done' ? '#22c55e' : status === 'running' ? '#f59e0b' : '#334155'
  const legX = 0.22
  const legZ = 0.32

  useFrame((state) => {
    if (bodyRef.current) {
      const bob = status === 'running' ? Math.sin(state.clock.elapsedTime * 8) * 0.02 : 0
      bodyRef.current.position.y = 0.5 + bob
    }
  })

  return (
    <group position={[x, 0, -1.4]}>
      <group ref={bodyRef} position={[0, 0.5, 0]}>
        <mesh castShadow receiveShadow>
          <boxGeometry args={[0.5, 0.22, 0.28]} />
          <meshStandardMaterial color="#1f2937" metalness={0.5} roughness={0.4} />
        </mesh>
        <mesh position={[0.2, 0.06, 0]}>
          <boxGeometry args={[0.08, 0.08, 0.1]} />
          <meshStandardMaterial color="#facc15" emissive="#facc15" emissiveIntensity={0.4} toneMapped={false} />
        </mesh>
      </group>
      {[[legX, legZ], [legX, -legZ], [-legX, legZ], [-legX, -legZ]].map(([dx, dz], i) => (
        <mesh key={i} position={[dx, 0.25, dz]} castShadow>
          <cylinderGeometry args={[0.03, 0.035, 0.5, 8]} />
          <meshStandardMaterial color="#374151" />
        </mesh>
      ))}
      <mesh position={[0.65, 0.75, -0.2]} rotation={[-0.3, 0, 0]}>
        <boxGeometry args={[0.32, 0.22, 0.02]} />
        <meshStandardMaterial color={tabletColor} emissive={tabletColor} emissiveIntensity={0.5} toneMapped={false} />
      </mesh>
      <mesh position={[0.65, 0.4, -0.2]}>
        <cylinderGeometry args={[0.02, 0.02, 0.7, 8]} />
        <meshStandardMaterial color="#1e293b" />
      </mesh>
    </group>
  )
}

// ─── Stage 6 — Control: desk + dashboard monitors with a live bar chart ────
// Function: ControlStation
function ControlStation({ x, status }) {
  const barRefs = useRef([])
  const barColor = status === 'done' ? '#22c55e' : '#38bdf8'

  useFrame((state) => {
    const t = state.clock.elapsedTime
    const active = status !== 'idle'
    barRefs.current.forEach((b, i) => {
      if (!b) return
      const h = active ? 0.15 + Math.abs(Math.sin(t * 2 + i)) * 0.35 : 0.1
      b.scale.y = h / 0.4
      b.position.y = 0.8 + h / 2
    })
  })

  return (
    <group position={[x, 0, -1.4]}>
      <mesh castShadow receiveShadow position={[0, 0.42, 0]}>
        <boxGeometry args={[1.4, 0.06, 0.6]} />
        <meshStandardMaterial color="#334155" />
      </mesh>
      {[[-0.6, -0.22], [0.6, -0.22], [-0.6, 0.22], [0.6, 0.22]].map(([dx, dz], i) => (
        <mesh key={i} position={[dx, 0.21, dz]}>
          <boxGeometry args={[0.05, 0.42, 0.05]} />
          <meshStandardMaterial color="#1e293b" />
        </mesh>
      ))}
      {[-0.42, 0.42].map((dx, i) => (
        <mesh key={i} position={[dx, 1.15, -0.5]}>
          <planeGeometry args={[0.7, 0.5]} />
          <meshStandardMaterial color="#0f172a" />
        </mesh>
      ))}
      {[0, 1, 2, 3, 4].map((i) => (
        <mesh key={i} ref={(el) => { barRefs.current[i] = el }} position={[-0.68 + i * 0.11, 1.0, -0.49]}>
          <boxGeometry args={[0.07, 0.4, 0.01]} />
          <meshStandardMaterial color={barColor} emissive={barColor} emissiveIntensity={0.6} toneMapped={false} />
        </mesh>
      ))}
      <mesh position={[0.42, 1.15, -0.495]}>
        <planeGeometry args={[0.6, 0.4]} />
        <meshStandardMaterial
          color={status === 'done' ? '#134e2a' : '#0c1a2e'}
          emissive={status === 'done' ? '#22c55e' : '#0ea5e9'}
          emissiveIntensity={status === 'done' ? 0.5 : 0.2}
          toneMapped={false}
        />
      </mesh>
    </group>
  )
}

// ─── Flow line along the floor with traveling "data packet" tiles ─────────
// Function: FlowLine
function FlowLine({ active }) {
  const packetRefs = useRef([])
  const count = 5

  useFrame((state) => {
    const t = state.clock.elapsedTime
    const speed = active ? 3.2 : 0
    const len = FLOW_END_X - FLOW_START_X
    packetRefs.current.forEach((p, i) => {
      if (!p) return
      const offset = (i / count) * len
      const wrapped = ((t * speed + offset) % len + len) % len
      p.position.x = FLOW_START_X + wrapped
      p.material.opacity = active ? 0.9 : 0.22
    })
  })

  return (
    <group>
      <mesh position={[0, 0.015, FLOW_Z]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[FLOW_END_X - FLOW_START_X + 2, 0.12]} />
        <meshStandardMaterial color="#164e63" emissive="#0ea5e9" emissiveIntensity={0.35} transparent opacity={0.6} toneMapped={false} />
      </mesh>
      {Array.from({ length: count }).map((_, i) => (
        <mesh key={i} ref={(el) => { packetRefs.current[i] = el }} position={[FLOW_START_X, 0.03, FLOW_Z]}>
          <boxGeometry args={[0.3, 0.03, 0.14]} />
          <meshStandardMaterial color="#38bdf8" emissive="#38bdf8" emissiveIntensity={1} transparent opacity={0.4} toneMapped={false} />
        </mesh>
      ))}
    </group>
  )
}

// ─── AI feedback-loop indicator strung along the back wall ─────────────────
// Function: FeedbackLoopArc
function FeedbackLoopArc({ pulse, x1, x2 }) {
  const dashCount = 14
  const dashRefs = useRef([])
  const y = WALL_HEIGHT - 0.6
  const dashXs = Array.from({ length: dashCount }, (_, i) => x1 + ((x2 - x1) * i) / (dashCount - 1))

  useFrame((state) => {
    const t = state.clock.elapsedTime
    dashRefs.current.forEach((d, i) => {
      if (!d) return
      if (pulse) {
        const phase = ((t * 2.4 - i * 0.18) % 1 + 1) % 1
        d.material.emissiveIntensity = 0.3 + Math.max(0, 1 - Math.abs(phase - 0.5) * 2.2) * 1.4
      } else {
        d.material.emissiveIntensity = 0.18
      }
    })
  })

  return (
    <group>
      {dashXs.map((dx, i) => (
        <mesh key={i} ref={(el) => { dashRefs.current[i] = el }} position={[dx, y, -ROOM_DEPTH / 2 + 0.02]}>
          <boxGeometry args={[0.5, 0.06, 0.02]} />
          <meshStandardMaterial color="#a78bfa" emissive="#a78bfa" emissiveIntensity={0.18} toneMapped={false} />
        </mesh>
      ))}
    </group>
  )
}

// ─── Soft highlight column over whichever stage the sequencer is running ───
// Function: ActiveHighlight
function ActiveHighlight({ x }) {
  if (x == null) return null
  return (
    <mesh position={[x, 1.4, -1.4]}>
      <cylinderGeometry args={[1.3, 1.3, 2.8, 24, 1, true]} />
      <meshBasicMaterial color="#fbbf24" transparent opacity={0.07} side={THREE.DoubleSide} depthWrite={false} />
    </mesh>
  )
}

// ─── Long factory shell ──────────────────────────────────────────────────
// Function: Room
function Room() {
  const wallColor = '#c9cdd4'
  return (
    <group>
      <mesh receiveShadow position={[0, -0.01, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[ROOM_WIDTH, ROOM_DEPTH]} />
        <meshStandardMaterial color="#7d828c" roughness={0.95} />
      </mesh>

      <mesh position={[0, WALL_HEIGHT / 2, -ROOM_DEPTH / 2]} receiveShadow>
        <planeGeometry args={[ROOM_WIDTH, WALL_HEIGHT]} />
        <meshStandardMaterial color={wallColor} roughness={0.9} />
      </mesh>
      <mesh position={[-ROOM_WIDTH / 2, WALL_HEIGHT / 2, 0]} rotation={[0, Math.PI / 2, 0]} receiveShadow>
        <planeGeometry args={[ROOM_DEPTH, WALL_HEIGHT]} />
        <meshStandardMaterial color={wallColor} roughness={0.9} />
      </mesh>
      <mesh position={[ROOM_WIDTH / 2, WALL_HEIGHT / 2, 0]} rotation={[0, -Math.PI / 2, 0]} receiveShadow>
        <planeGeometry args={[ROOM_DEPTH, WALL_HEIGHT]} />
        <meshStandardMaterial color={wallColor} roughness={0.9} />
      </mesh>

      {STAGES.map((s, i) => (
        <mesh key={i} position={[s.x, WALL_HEIGHT - 0.03, 0]} rotation={[Math.PI / 2, 0, 0]}>
          <planeGeometry args={[2.6, 1.0]} />
          <meshStandardMaterial color="#ffffff" emissive="#ffffff" emissiveIntensity={0.5} toneMapped={false} />
        </mesh>
      ))}

      {DIVIDER_XS.map((dx, i) => (
        <mesh key={i} position={[dx, 0.006, 0]} rotation={[-Math.PI / 2, 0, 0]}>
          <planeGeometry args={[0.03, ROOM_DEPTH - 0.6]} />
          <meshStandardMaterial color="#4b5563" />
        </mesh>
      ))}
    </group>
  )
}

// Function: Scene
function Scene({ stageStatus, sequencerOn, activeIndex, feedbackPulse, moveCartXRef }) {
  const activeX = sequencerOn && activeIndex >= 0 ? STAGES[activeIndex].x : null

  return (
    <group>
      <ambientLight intensity={0.55} />
      <hemisphereLight skyColor="#dbeafe" groundColor="#334155" intensity={0.5} />
      <directionalLight position={[6, 10, 8]} intensity={1.1} castShadow shadow-mapSize={[1024, 1024]} />
      <directionalLight position={[-6, 8, 4]} intensity={0.5} />

      <Room />
      <FlowLine active={sequencerOn} />
      <FeedbackLoopArc pulse={feedbackPulse} x1={STAGES[5].x} x2={STAGES[0].x} />
      <ActiveHighlight x={activeX} />
      <TravelingCart activeIndex={activeIndex} sequencerOn={sequencerOn} cartXRef={moveCartXRef} />

      <SimulateStation x={STAGES[0].x} status={stageStatus.simulate} />
      <InspectStation x={STAGES[1].x} status={stageStatus.inspect} />
      <BuildStation x={STAGES[2].x} status={stageStatus.build} />
      <ValidateStation x={STAGES[4].x} status={stageStatus.validate} />
      <ControlStation x={STAGES[5].x} status={stageStatus.control} />

      {STAGES.map((s) => (
        <StationLabel key={s.key} x={s.x} n={s.n} name={s.name} status={stageStatus[s.key]} />
      ))}
    </group>
  )
}

// Recomputes the camera target every frame from primitives (not a pre-baked
// preset object) so that when the Move stage is focused, it can substitute
// the AMR's live, continuously-updated x position in place of the station's
// fixed bay marker — otherwise a "detailed analysis" close-up of Move shows
// an empty bay for the cart's entire transit, since the cart itself departs
// from that fixed point while running.
// Function: CameraFollow
function CameraFollow({ focusKey, angle, moveCartXRef, controlsRef }) {
  const { camera } = useThree()
  const targetPos = useRef(new THREE.Vector3(...OVERVIEW.position))
  const targetLook = useRef(new THREE.Vector3(...OVERVIEW.target))

  useFrame((_, delta) => {
    let subjectX = null
    let subjectZ = STATION_Z
    if (focusKey) {
      if (focusKey === 'move' && moveCartXRef) {
        subjectX = moveCartXRef.current
        subjectZ = FLOW_Z
      } else {
        subjectX = STAGES.find((s) => s.key === focusKey)?.x ?? null
      }
    }
    const preset = cameraPresetFor(subjectX, angle, subjectZ)
    targetPos.current.set(...preset.position)
    targetLook.current.set(...preset.target)

    // Fast enough to fully settle on a new stage well within its shortest
    // dwell time, so the "detailed analysis" view never lags behind the
    // sequencer onto the previous station.
    const t = Math.min(delta * 5.5, 1)
    camera.position.lerp(targetPos.current, t)
    if (controlsRef.current) {
      controlsRef.current.target.lerp(targetLook.current, t)
      controlsRef.current.update()
    }
  })

  return null
}

// ─── Control-bar stage card ─────────────────────────────────────────────
// Function: StageCard
function StageCard({ stage, status, isSequencerActive, focused, onFocus, onRun, disabled, lastEvent, onOpenDetail }) {
  const statusLabel = { idle: 'IDLE', running: 'RUNNING', done: 'COMPLETE' }[status]
  const statusClass = {
    idle: 'text-slate-400 bg-slate-800/70',
    running: 'text-amber-300 bg-amber-500/15',
    done: 'text-emerald-300 bg-emerald-500/15',
  }[status]
  const eventKind = lastEvent ? EVENT_KIND[lastEvent.kind] : null

  return (
    <div
      className={`w-64 shrink-0 rounded-lg border p-3 flex flex-col gap-2 cursor-pointer transition-colors ${
        focused
          ? 'border-cyan-400 bg-slate-800/80'
          : isSequencerActive
            ? 'border-amber-400 bg-slate-800/60'
            : 'border-slate-700 bg-slate-900/60 hover:border-slate-500'
      }`}
      onClick={onFocus}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span
            className="w-6 h-6 rounded-full flex items-center justify-center text-[11px] font-bold text-slate-950"
            style={{ background: stage.color }}
          >
            {stage.n}
          </span>
          <span className="text-sm font-semibold text-white">{stage.name}</span>
        </div>
        <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold tracking-wide ${statusClass}`}>
          {statusLabel}
        </span>
      </div>
      <p className="text-[11px] text-slate-400 leading-snug">
        {stage.tagline} · <span className="text-slate-300">{stage.system}</span>
      </p>
      <p className="text-[11px] text-slate-500 leading-snug">{stage.challenge}</p>
      <p className="text-[11px] font-medium text-cyan-300 leading-snug">{stage.outcome}</p>
      {eventKind && (
        <div className="flex items-center gap-1.5 -mt-0.5 px-1.5 py-1 rounded bg-black/30 border border-slate-800">
          <span className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: eventKind.color }} />
          <span className="text-[9.5px] font-mono truncate" style={{ color: eventKind.color }}>
            {eventKind.label}
          </span>
          <span className="text-[9.5px] font-mono text-slate-400 truncate">{lastEvent.topic}</span>
        </div>
      )}
      <div className="mt-1 flex items-center gap-2">
        <button
          onClick={(e) => { e.stopPropagation(); onRun() }}
          disabled={disabled}
          className="px-2.5 py-1 rounded text-[11px] font-semibold bg-slate-700 hover:bg-slate-600 disabled:opacity-40 disabled:cursor-not-allowed text-white transition-colors"
        >
          {status === 'running' ? 'Running…' : 'Run stage'}
        </button>
        <button
          onClick={(e) => { e.stopPropagation(); onOpenDetail() }}
          className="px-2.5 py-1 rounded text-[11px] font-semibold bg-cyan-600 hover:bg-cyan-500 text-white transition-colors"
        >
          View simulation
        </button>
      </div>
    </div>
  )
}

// ─── Protocol Monitor: live MQTT/PLC event console ─────────────────────
// Shows the full triggered → received/accepted → action-performed chain
// for every stage, newest at the bottom, auto-scrolling as events arrive —
// the same three-step handshake a real MES/PLC integration log would show.
// Function: ProtocolMonitor
function ProtocolMonitor({ log }) {
  const scrollRef = useRef(null)

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight
  }, [log])

  return (
    <div className="absolute top-3 right-3 bottom-3 w-[360px] bg-slate-950/95 border border-slate-700 rounded-lg flex flex-col overflow-hidden">
      <div className="px-3 py-2 border-b border-slate-800 flex items-center justify-between shrink-0">
        <p className="text-[11px] font-semibold text-white">Protocol Monitor</p>
        <p className="text-[10px] font-mono text-slate-500">MQTT · PLC I/O</p>
      </div>
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-3 py-2 flex flex-col gap-1.5">
        {log.length === 0 && (
          <p className="text-[11px] text-slate-500 font-mono">
            No traffic yet — run a stage to see MQTT commands, acknowledgements, and PLC I/O events.
          </p>
        )}
        {log.map((e) => {
          const kind = EVENT_KIND[e.kind]
          const time = new Date(e.time)
          const hh = String(time.getHours()).padStart(2, '0')
          const mm = String(time.getMinutes()).padStart(2, '0')
          const ss = String(time.getSeconds()).padStart(2, '0')
          const ms = String(time.getMilliseconds()).padStart(3, '0')
          return (
            <div key={e.id} className="text-[10.5px] font-mono leading-snug border-b border-slate-900 pb-1.5">
              <div className="flex items-center gap-1.5">
                <span className="text-slate-600">{hh}:{mm}:{ss}.{ms}</span>
                <span className="font-semibold" style={{ color: kind.color }}>{kind.label}</span>
                <span className="text-slate-500 truncate">{e.stageName}</span>
              </div>
              <div className="text-slate-300 truncate">
                <span style={{ color: kind.color }}>{e.topic}</span>
                <span className="text-slate-600"> → </span>
                <span className="text-slate-400">{e.payload}</span>
              </div>
              <div className="text-slate-500">{e.note}</div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ─── L2/L3 detail-view animation primitives ────────────────────────────
// A small, reusable set of close-up mini-animations that every stage's
// sub-steps are built from, rather than 18 fully bespoke scenes — keeps the
// detail views visually consistent while still giving each step a distinct,
// legible motion that matches what it's meant to represent.

// Function: AssembleAnim
function AssembleAnim({ color }) {
  const partRefs = useRef([])
  const count = 9
  const targets = useMemo(() => {
    const arr = []
    for (let i = 0; i < count; i += 1) {
      const gx = (i % 3) - 1
      const gy = Math.floor(i / 3) - 1
      arr.push([gx * 0.32, gy * 0.32 + 0.9, 0])
    }
    return arr
  }, [])
  const scatter = useMemo(
    () => targets.map(() => [(Math.random() - 0.5) * 1.8, 0.35 + Math.random() * 1.2, (Math.random() - 0.5) * 1.2]),
    [targets],
  )

  useFrame((state) => {
    const t = (Math.sin(state.clock.elapsedTime * 0.6 - Math.PI / 2) + 1) / 2
    partRefs.current.forEach((g, i) => {
      if (!g) return
      const [sx, sy, sz] = scatter[i]
      const [tx, ty, tz] = targets[i]
      g.position.set(sx + (tx - sx) * t, sy + (ty - sy) * t, sz + (tz - sz) * t)
      g.rotation.y = (1 - t) * 3
    })
  })

  return (
    <group>
      {targets.map((_, i) => (
        <mesh key={i} ref={(el) => { partRefs.current[i] = el }} castShadow>
          <boxGeometry args={[0.22, 0.22, 0.22]} />
          <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.4} wireframe={i % 2 === 0} />
        </mesh>
      ))}
    </group>
  )
}

// Function: PulseGridAnim
function PulseGridAnim({ color }) {
  const planeRef = useRef(null)
  const barRefs = useRef([])

  useFrame((state) => {
    const t = state.clock.elapsedTime
    if (planeRef.current) planeRef.current.material.emissiveIntensity = 0.3 + Math.sin(t * 2) * 0.25
    barRefs.current.forEach((b, i) => {
      if (!b) return
      b.material.opacity = 0.3 + Math.abs(Math.sin(t * 1.5 + i * 0.4)) * 0.6
    })
  })

  return (
    <group position={[0, 0.9, 0]}>
      <mesh ref={planeRef}>
        <planeGeometry args={[2.2, 1.4]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.4} wireframe transparent opacity={0.8} />
      </mesh>
      {[-0.8, -0.4, 0, 0.4, 0.8].map((x, i) => (
        <mesh key={i} ref={(el) => { barRefs.current[i] = el }} position={[x, 0, 0.01]}>
          <planeGeometry args={[0.02, 1.4]} />
          <meshBasicMaterial color={color} transparent opacity={0.5} toneMapped={false} />
        </mesh>
      ))}
    </group>
  )
}

// Function: GaugeAnim
function GaugeAnim({ color }) {
  const needleRef = useRef(null)

  useFrame((state) => {
    const t = (state.clock.elapsedTime % 3) / 3
    const angle = -Math.PI * 0.75 + Math.min(t * 1.4, 1) * Math.PI * 1.5
    if (needleRef.current) needleRef.current.rotation.z = angle
  })

  return (
    <group position={[0, 0.9, 0]}>
      <mesh rotation={[0, 0, Math.PI * 0.75]}>
        <torusGeometry args={[0.55, 0.04, 12, 32, Math.PI * 1.5]} />
        <meshStandardMaterial color="#334155" />
      </mesh>
      <group ref={needleRef} position={[0, 0, 0.02]}>
        <mesh position={[0.22, 0, 0]}>
          <boxGeometry args={[0.44, 0.03, 0.03]} />
          <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.7} toneMapped={false} />
        </mesh>
      </group>
      <mesh position={[0, 0, 0.03]}>
        <sphereGeometry args={[0.05, 12, 12]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.7} toneMapped={false} />
      </mesh>
    </group>
  )
}

// Function: ScanBeamAnim
function ScanBeamAnim({ color }) {
  const beamRef = useRef(null)

  useFrame((state) => {
    const t = state.clock.elapsedTime
    if (beamRef.current) beamRef.current.position.y = 0.15 + (Math.sin(t * 2) * 0.5 + 0.5) * 0.7
  })

  return (
    <group position={[0, 0.5, 0]}>
      <mesh castShadow>
        <boxGeometry args={[0.7, 0.4, 0.7]} />
        <meshStandardMaterial color="#94a3b8" metalness={0.5} roughness={0.4} />
      </mesh>
      <mesh ref={beamRef} position={[0, 0.35, 0]}>
        <boxGeometry args={[0.9, 0.02, 0.9]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={1} transparent opacity={0.75} toneMapped={false} />
      </mesh>
    </group>
  )
}

// Function: DefectGridAnim
function DefectGridAnim({ color }) {
  const cellRefs = useRef([])
  const cells = 9

  useFrame((state) => {
    const t = state.clock.elapsedTime
    cellRefs.current.forEach((c, i) => {
      if (!c) return
      const flagged = i === 4
      const cyc = (t + i * 0.3) % 4
      const col = flagged && cyc < 1.2 ? '#f43f5e' : color
      c.material.color.set(col)
      c.material.emissive.set(col)
    })
  })

  return (
    <group position={[0, 0.9, 0.36]}>
      {Array.from({ length: cells }).map((_, i) => {
        const gx = (i % 3) - 1
        const gy = Math.floor(i / 3) - 1
        return (
          <mesh key={i} ref={(el) => { cellRefs.current[i] = el }} position={[gx * 0.3, gy * 0.3, 0]}>
            <planeGeometry args={[0.26, 0.26]} />
            <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.5} transparent opacity={0.5} toneMapped={false} />
          </mesh>
        )
      })}
    </group>
  )
}

// Function: StampAnim
function StampAnim({ color }) {
  const stampRef = useRef(null)

  useFrame((state) => {
    const t = state.clock.elapsedTime % 2.4
    const s = t < 0.3 ? THREE.MathUtils.lerp(1.5, 1, t / 0.3) : 1
    if (stampRef.current) stampRef.current.scale.setScalar(Math.max(s, 0.001))
  })

  return (
    <group position={[0, 0.9, 0]} ref={stampRef}>
      <mesh>
        <circleGeometry args={[0.5, 32]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.5} transparent opacity={0.25} toneMapped={false} />
      </mesh>
      <mesh position={[-0.08, 0, 0.01]} rotation={[0, 0, Math.PI / 4]}>
        <boxGeometry args={[0.3, 0.06, 0.02]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.8} toneMapped={false} />
      </mesh>
      <mesh position={[0.08, 0.08, 0.01]} rotation={[0, 0, -Math.PI / 4]}>
        <boxGeometry args={[0.5, 0.06, 0.02]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.8} toneMapped={false} />
      </mesh>
    </group>
  )
}

// Function: TapArmAnim
function TapArmAnim({ color }) {
  const armRef = useRef(null)

  useFrame((state, delta) => {
    const target = Math.sin(state.clock.elapsedTime * 3) * 0.4 + 0.5
    if (armRef.current) armRef.current.rotation.x += (target - armRef.current.rotation.x) * Math.min(delta * 5, 1)
  })

  return (
    <group position={[0, 0.5, 0]}>
      <mesh castShadow>
        <boxGeometry args={[0.7, 0.15, 0.7]} />
        <meshStandardMaterial color="#475569" />
      </mesh>
      <mesh position={[-0.2, 0.2, 0]}>
        <cylinderGeometry args={[0.06, 0.07, 0.4, 12]} />
        <meshStandardMaterial color={color} metalness={0.4} roughness={0.4} />
      </mesh>
      <group position={[-0.2, 0.42, 0]} ref={armRef}>
        <mesh position={[0, 0.2, 0]} castShadow>
          <capsuleGeometry args={[0.05, 0.36, 4, 10]} />
          <meshStandardMaterial color="#e2e8f0" />
        </mesh>
      </group>
    </group>
  )
}

// Function: WaypointPathAnim
function WaypointPathAnim({ color }) {
  const cartRef = useRef(null)

  useFrame((state) => {
    const t = (Math.sin(state.clock.elapsedTime * 1.2) + 1) / 2
    if (cartRef.current) cartRef.current.position.x = -0.9 + t * 1.8
  })

  return (
    <group position={[0, 0.5, 0]}>
      {[-0.9, -0.45, 0, 0.45, 0.9].map((x, i) => (
        <mesh key={i} position={[x, -0.3, 0]}>
          <circleGeometry args={[0.04, 12]} />
          <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.6} toneMapped={false} />
        </mesh>
      ))}
      <mesh ref={cartRef} position={[-0.9, 0, 0]} castShadow>
        <boxGeometry args={[0.3, 0.2, 0.24]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.3} />
      </mesh>
    </group>
  )
}

// Function: DataRowsAnim
function DataRowsAnim({ color }) {
  const rowRefs = useRef([])

  useFrame((state) => {
    const t = state.clock.elapsedTime
    rowRefs.current.forEach((r, i) => {
      if (!r) return
      const active = Math.floor(t * 1.5) % 5 === i
      const col = active ? color : '#334155'
      r.material.color.set(col)
      r.material.emissive.set(col)
      r.material.emissiveIntensity = active ? 0.6 : 0.15
    })
  })

  return (
    <group position={[0, 0.9, 0]}>
      {[0.3, 0.1, -0.1, -0.3, -0.5].map((y, i) => (
        <mesh key={i} ref={(el) => { rowRefs.current[i] = el }} position={[0, y, 0]}>
          <boxGeometry args={[1.2, 0.12, 0.04]} />
          <meshStandardMaterial color="#334155" emissive="#334155" emissiveIntensity={0.15} toneMapped={false} />
        </mesh>
      ))}
    </group>
  )
}

// Function: BarChartAnim
function BarChartAnim({ color, variant }) {
  const barRefs = useRef([])

  useFrame((state) => {
    const t = state.clock.elapsedTime
    barRefs.current.forEach((b, i) => {
      if (!b) return
      const spike = variant === 'anomaly' && i === 3
      const h = spike ? 0.9 + Math.sin(t * 6) * 0.15 : 0.2 + Math.abs(Math.sin(t * 1.6 + i)) * 0.55
      b.scale.y = h / 0.5
      b.position.y = h / 2
      const col = spike ? '#f43f5e' : color
      b.material.color.set(col)
      b.material.emissive.set(col)
    })
  })

  return (
    <group position={[-0.5, 0.55, 0]}>
      {[0, 1, 2, 3, 4, 5].map((i) => (
        <mesh key={i} ref={(el) => { barRefs.current[i] = el }} position={[i * 0.2, 0.1, 0]}>
          <boxGeometry args={[0.13, 0.5, 0.13]} />
          <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.5} toneMapped={false} />
        </mesh>
      ))}
    </group>
  )
}

// Function: SignalPulseAnim
function SignalPulseAnim({ color }) {
  const ringRefs = useRef([])

  useFrame((state) => {
    const t = state.clock.elapsedTime
    ringRefs.current.forEach((r, i) => {
      if (!r) return
      const cyc = (t + i * 0.5) % 1.5
      r.scale.setScalar(0.2 + cyc * 1.2)
      r.material.opacity = Math.max(0, 1 - cyc / 1.5) * 0.7
    })
  })

  return (
    <group position={[0, 0.9, 0]}>
      <mesh>
        <sphereGeometry args={[0.12, 16, 16]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.9} toneMapped={false} />
      </mesh>
      {[0, 1, 2].map((i) => (
        <mesh key={i} ref={(el) => { ringRefs.current[i] = el }} rotation={[Math.PI / 2, 0, 0]}>
          <ringGeometry args={[0.3, 0.34, 32]} />
          <meshBasicMaterial color={color} transparent opacity={0.5} toneMapped={false} side={THREE.DoubleSide} />
        </mesh>
      ))}
    </group>
  )
}

// Function: StepAnim
function StepAnim({ anim, color, variant }) {
  switch (anim) {
    case 'assemble': return <AssembleAnim color={color} />
    case 'pulseGrid': return <PulseGridAnim color={color} />
    case 'gauge': return <GaugeAnim color={color} />
    case 'scanBeam': return <ScanBeamAnim color={color} />
    case 'defectGrid': return <DefectGridAnim color={color} />
    case 'stamp': return <StampAnim color={color} />
    case 'tapArm': return <TapArmAnim color={color} />
    case 'waypoint': return <WaypointPathAnim color={color} />
    case 'dataRows': return <DataRowsAnim color={color} />
    case 'barChart': return <BarChartAnim color={color} variant={variant} />
    case 'signal': return <SignalPulseAnim color={color} />
    default: return null
  }
}

// ─── L2/L3 detail modal: full-screen per-stage simulation walkthrough ─────
// The plain `camera={{ position }}` shorthand leaves the camera pointed
// straight down -Z with no tilt, so it never actually aims at the
// animation's centroid — content taller than the camera's own height (the
// tap arm mid-swing, the stamp's scale-in overshoot) crops off the top of
// frame while the floor sits in a lot of dead space below. This explicitly
// aims the camera once at mount so every step's content is centered and
// fully in frame regardless of its own vertical extent.
// Function: DetailCameraRig
function DetailCameraRig() {
  const { camera } = useThree()
  useEffect(() => {
    camera.lookAt(0, 0.72, 0)
    camera.updateProjectionMatrix()
  }, [camera])
  return null
}

// Function: StageDetailModal
function StageDetailModal({ stage, stepIndex, setStepIndex, onClose }) {
  const step = stage.steps[stepIndex]

  return (
    <div className="fixed inset-0 z-50 bg-slate-950 flex flex-col">
      <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <span
            className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold text-slate-950 shrink-0"
            style={{ background: stage.color }}
          >
            {stage.n}
          </span>
          <div>
            <p className="text-[11px] uppercase tracking-[0.15em] text-slate-400">Stage simulation</p>
            <h2 className="text-white font-semibold text-lg leading-tight">{stage.name} · {stage.system}</h2>
          </div>
        </div>
        <button
          onClick={onClose}
          className="px-3 py-2 rounded-lg text-sm font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
        >
          Close
        </button>
      </div>

      <div className="px-6 py-3 border-b border-slate-800 flex gap-2 flex-wrap shrink-0">
        {stage.steps.map((s, i) => (
          <button
            key={s.n}
            onClick={() => setStepIndex(i)}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium border transition-colors ${
              i === stepIndex ? 'border-cyan-400 bg-cyan-500/10 text-cyan-300' : 'border-slate-700 bg-slate-900 text-slate-400 hover:border-slate-500'
            }`}
          >
            <span
              className="w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0"
              style={{ background: i === stepIndex ? stage.color : '#334155', color: i === stepIndex ? '#0f172a' : '#94a3b8' }}
            >
              {s.n}
            </span>
            {s.title}
          </button>
        ))}
      </div>

      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 relative">
          <Canvas camera={{ position: [0, 1.3, 3.8], fov: 34 }} gl={{ antialias: true, alpha: false }}>
            <color attach="background" args={['#0b1220']} />
            <ambientLight intensity={0.6} />
            <directionalLight position={[2, 3, 3]} intensity={1.1} />
            <directionalLight position={[-2, 2, -2]} intensity={0.4} />
            <DetailCameraRig />
            <StepAnim anim={step.anim} color={stage.color} variant={step.variant} />
          </Canvas>
        </div>

        <div className="w-96 border-l border-slate-800 p-5 flex flex-col gap-4 overflow-y-auto shrink-0">
          <div>
            <p className="text-[10px] uppercase tracking-wider text-slate-500 mb-1">Step {step.n} of {stage.steps.length}</p>
            <h3 className="text-white font-semibold text-base mb-2 leading-snug">{step.title}</h3>
            <p className="text-sm text-slate-400 leading-relaxed">{step.description}</p>
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
            <p className="text-[10px] uppercase tracking-wider text-slate-500 mb-1">Live readout</p>
            <p className="text-sm font-mono text-cyan-300">{step.metric}</p>
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
            <p className="text-[10px] uppercase tracking-wider text-slate-500 mb-1">Signal</p>
            <p className="text-[11px] font-mono text-amber-300">{step.signal}</p>
          </div>
          <div className="flex gap-2 mt-auto pt-2">
            <button
              disabled={stepIndex === 0}
              onClick={() => setStepIndex((i) => Math.max(0, i - 1))}
              className="flex-1 px-3 py-2 rounded-lg text-sm font-medium bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-slate-200 border border-slate-700 transition-colors"
            >
              ← Previous
            </button>
            <button
              disabled={stepIndex === stage.steps.length - 1}
              onClick={() => setStepIndex((i) => Math.min(stage.steps.length - 1, i + 1))}
              className="flex-1 px-3 py-2 rounded-lg text-sm font-semibold bg-cyan-600 hover:bg-cyan-500 disabled:opacity-40 disabled:cursor-not-allowed text-white transition-colors"
            >
              Next →
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// Each stage holds for a full 30s "processing" window before the pipeline
// advances, so there's time to actually watch what a stage is doing (and
// watch the pipeline item travel into it) instead of it flashing past.
const STAGE_MS = 30000
const GAP_MS = 260
const FEEDBACK_MS = 1500
const MANUAL_RUN_MS = 2200

// Function: FactoryOrchestration3D
export default function FactoryOrchestration3D() {
  const [stageStatus, setStageStatus] = useState(() => Object.fromEntries(STAGES.map((s) => [s.key, 'idle'])))
  const [sequencerOn, setSequencerOn] = useState(false)
  const [activeIndex, setActiveIndex] = useState(-1)
  const [feedbackPulse, setFeedbackPulse] = useState(false)
  const [focusStage, setFocusStage] = useState(null)
  const [focusAngle, setFocusAngle] = useState('close')
  const [log, setLog] = useState([])
  const [showLog, setShowLog] = useState(true)
  const [detailKey, setDetailKey] = useState(null)
  const [detailStep, setDetailStep] = useState(0)

  const controlsRef = useRef(null)
  const seqCancelRef = useRef(false)
  const manualTimeoutsRef = useRef({})
  const moveCartXRef = useRef(STAGES[0].x)

  // Function: pushEvents
  function pushEvents(key, phase) {
    const stage = STAGES.find((s) => s.key === key)
    if (!stage) return
    const events = buildEvents(stage, phase)
    setLog((prev) => {
      const next = [...prev, ...events]
      return next.length > 150 ? next.slice(next.length - 150) : next
    })
  }

  useEffect(() => {
    if (!sequencerOn) return undefined
    seqCancelRef.current = false
    let idx = 0

    // Function: stepStage
    function stepStage() {
      if (seqCancelRef.current) return
      setActiveIndex(idx)
      const key = STAGES[idx].key
      setStageStatus((prev) => ({ ...prev, [key]: 'running' }))
      pushEvents(key, 'start')
      setTimeout(() => {
        if (seqCancelRef.current) return
        setStageStatus((prev) => ({ ...prev, [key]: 'done' }))
        pushEvents(key, 'complete')
        idx += 1
        if (idx < STAGES.length) {
          setTimeout(stepStage, GAP_MS)
        } else {
          setFeedbackPulse(true)
          setTimeout(() => {
            if (seqCancelRef.current) return
            setFeedbackPulse(false)
            setStageStatus(Object.fromEntries(STAGES.map((s) => [s.key, 'idle'])))
            idx = 0
            setTimeout(stepStage, GAP_MS)
          }, FEEDBACK_MS)
        }
      }, STAGE_MS)
    }

    stepStage()
    return () => { seqCancelRef.current = true }
  }, [sequencerOn])

  useEffect(() => () => {
    Object.values(manualTimeoutsRef.current).forEach(clearTimeout)
  }, [])

  // Function: toggleSequencer
  function toggleSequencer() {
    if (sequencerOn) {
      seqCancelRef.current = true
      setSequencerOn(false)
      setActiveIndex(-1)
      return
    }
    setSequencerOn(true)
  }

  // Function: runStageManually
  function runStageManually(key) {
    if (sequencerOn) return
    clearTimeout(manualTimeoutsRef.current[key])
    setStageStatus((prev) => ({ ...prev, [key]: 'running' }))
    pushEvents(key, 'start')
    manualTimeoutsRef.current[key] = setTimeout(() => {
      setStageStatus((prev) => ({ ...prev, [key]: 'done' }))
      pushEvents(key, 'complete')
    }, MANUAL_RUN_MS)
  }

  // Function: resetAll
  function resetAll() {
    seqCancelRef.current = true
    setSequencerOn(false)
    setActiveIndex(-1)
    setFeedbackPulse(false)
    setFocusStage(null)
    setFocusAngle('close')
    Object.values(manualTimeoutsRef.current).forEach(clearTimeout)
    manualTimeoutsRef.current = {}
    setStageStatus(Object.fromEntries(STAGES.map((s) => [s.key, 'idle'])))
    setLog([])
  }

  // Deliberately does NOT auto-follow the sequencer's active stage — running
  // the full flow should keep the whole line in view so the pipeline item
  // and AMR are both visible traveling across stages. Camera only zooms in
  // when a stage card is clicked by hand.
  const focusKey = focusStage
  const isFocused = focusKey != null

  const lastEventByStage = {}
  for (let i = log.length - 1; i >= 0; i -= 1) {
    const e = log[i]
    if (!lastEventByStage[e.stageKey]) lastEventByStage[e.stageKey] = e
  }

  // Function: focusOnStage
  function focusOnStage(key) {
    setFocusStage((f) => {
      if (f === key) return null
      setFocusAngle('close')
      return key
    })
  }

  // Function: openDetail
  function openDetail(key) {
    setDetailKey(key)
    setDetailStep(0)
  }

  const detailStage = detailKey ? STAGES.find((s) => s.key === detailKey) : null

  return (
    <div className="flex flex-col h-screen bg-slate-950">
      <div className="px-5 py-3 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-[11px] uppercase tracking-[0.2em] text-cyan-400">Factory Orchestration</p>
          <h2 className="text-white font-semibold text-lg leading-tight">Autonomous, Adaptive, Zero-Defect Manufacturing Flow</h2>
        </div>
        <div className="flex items-center gap-2">
          <div
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-mono transition-colors ${
              feedbackPulse ? 'border-violet-400 text-violet-300 bg-violet-500/10' : 'border-slate-700 text-slate-500 bg-slate-900'
            }`}
          >
            <span className={`w-2 h-2 rounded-full ${feedbackPulse ? 'bg-violet-400 animate-pulse' : 'bg-slate-600'}`} />
            AI Feedback Loop
          </div>
          <button
            onClick={() => setShowLog((v) => !v)}
            className={`px-3 py-2 rounded-lg text-sm font-medium border transition-colors ${
              showLog ? 'border-cyan-400 text-cyan-300 bg-cyan-500/10' : 'border-slate-700 text-slate-300 bg-slate-800 hover:bg-slate-700'
            }`}
          >
            Protocol Monitor
          </button>
          <button
            onClick={toggleSequencer}
            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-colors ${
              sequencerOn ? 'bg-red-600 hover:bg-red-700 text-white' : 'bg-emerald-600 hover:bg-emerald-700 text-white'
            }`}
          >
            {sequencerOn ? 'Stop Factory Flow' : 'Run Full Factory Flow'}
          </button>
          <button
            onClick={resetAll}
            className="px-3 py-2 rounded-lg text-sm font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
          >
            Reset
          </button>
        </div>
      </div>

      <div className="px-5 py-3 border-b border-slate-800 overflow-x-auto">
        <div className="flex gap-3 min-w-max">
          {STAGES.map((s, i) => (
            <StageCard
              key={s.key}
              stage={s}
              status={stageStatus[s.key]}
              isSequencerActive={sequencerOn && activeIndex === i}
              focused={focusStage === s.key}
              onFocus={() => focusOnStage(s.key)}
              onRun={() => runStageManually(s.key)}
              disabled={sequencerOn}
              lastEvent={lastEventByStage[s.key]}
              onOpenDetail={() => openDetail(s.key)}
            />
          ))}
        </div>
      </div>

      <div className="flex-1 relative">
        <Canvas
          shadows={{ type: THREE.PCFShadowMap }}
          camera={{ position: OVERVIEW.position, fov: 46, near: 0.1, far: 100 }}
          gl={{ antialias: true, alpha: false }}
        >
          <Suspense fallback={null}>
            <fog attach="fog" args={['#0b1220', 22, 46]} />
            <color attach="background" args={['#0b1220']} />

            <Scene stageStatus={stageStatus} sequencerOn={sequencerOn} activeIndex={activeIndex} feedbackPulse={feedbackPulse} moveCartXRef={moveCartXRef} />
            <CameraFollow focusKey={focusKey} angle={focusAngle} moveCartXRef={moveCartXRef} controlsRef={controlsRef} />

            <OrbitControls
              ref={controlsRef}
              makeDefault
              enableRotate
              enableZoom
              enablePan
              minPolarAngle={0.2}
              maxPolarAngle={Math.PI / 2.1}
              target={OVERVIEW.target}
              minDistance={3}
              maxDistance={40}
            />
          </Suspense>
        </Canvas>

        <div className="absolute bottom-3 left-3 bg-slate-900/90 border border-slate-700 rounded-lg p-2.5 flex flex-col gap-2">
          {isFocused ? (
            <>
              <p className="text-[10px] uppercase tracking-wider text-slate-400 px-0.5">
                Inspecting: <span className="text-cyan-300">{STAGES.find((s) => s.key === focusKey)?.name}</span>
              </p>
              <div className="grid grid-cols-4 gap-1">
                {STAGE_ANGLE_ORDER.map((k) => (
                  <button
                    key={k}
                    onClick={() => setFocusAngle(k)}
                    className={`px-2 py-1 rounded text-[11px] font-semibold transition-colors ${
                      focusAngle === k ? 'bg-cyan-500 text-slate-950' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                    }`}
                  >
                    {STAGE_ANGLES[k].label}
                  </button>
                ))}
              </div>
              <button
                onClick={() => setFocusStage(null)}
                className="px-2 py-1.5 rounded text-[11px] font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-colors"
              >
                Back to full-line overview
              </button>
            </>
          ) : (
            <p className="text-[11px] text-slate-300 font-mono px-0.5">
              Click a stage card for close-up, front, side, and top inspection views
            </p>
          )}
        </div>

        {showLog && <ProtocolMonitor log={log} />}
      </div>

      {detailStage && (
        <StageDetailModal
          stage={detailStage}
          stepIndex={detailStep}
          setStepIndex={setDetailStep}
          onClose={() => setDetailKey(null)}
        />
      )}
    </div>
  )
}
