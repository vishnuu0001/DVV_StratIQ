// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: LabRobot — frontend/src/components (RackViewer3D.jsx)
// Date: 2025-07-17
// ---------------------------------------------------------------------------
import { Suspense, useEffect, useMemo, useRef, useState } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { Html, OrbitControls } from '@react-three/drei'
import * as THREE from 'three'

// ─── Room dimensions ──────────────────────────────────────────────────────
const ROOM_WIDTH = 16
const ROOM_DEPTH = 12
const WALL_HEIGHT = 5

// ─── Camera framing ───────────────────────────────────────────────────────
const CAMERA_PRESETS = {
  overview: { position: [8.5, 6, 10], target: [0, 1.2, 0] },
  front: { position: [0, 3.5, 9.5], target: [0, 1.2, 0] },
  side: { position: [10.5, 3.5, 0], target: [0, 1.2, 0] },
  top: { position: [0.1, 12, 0.1], target: [0, 0.9, 0] },
}

// Function: CameraRig
function CameraRig({ view, controlsRef }) {
  const { camera } = useThree()

  useEffect(() => {
    const preset = CAMERA_PRESETS[view] || CAMERA_PRESETS.overview
    camera.position.set(...preset.position)
    if (controlsRef.current) {
      controlsRef.current.target.set(...preset.target)
      controlsRef.current.update()
    }
    camera.updateProjectionMatrix()
  }, [view, camera, controlsRef])

  return null
}

// Function: ProximityLabel
function ProximityLabel({ position, text, color = '#dbeafe', nearDistance = 14 }) {
  const { camera } = useThree()
  const [visible, setVisible] = useState(false)
  const labelPosRef = useRef(new THREE.Vector3(...position))
  const visibleRef = useRef(false)

  useEffect(() => {
    labelPosRef.current.fromArray(position)
  }, [position])

  useFrame(() => {
    const dist = camera.position.distanceTo(labelPosRef.current)
    const threshold = visibleRef.current ? nearDistance + 2 : nearDistance
    const nextVisible = dist <= threshold
    if (nextVisible !== visibleRef.current) {
      visibleRef.current = nextVisible
      setVisible(nextVisible)
    }
  })

  if (!visible) return null

  return (
    <Html position={position} center distanceFactor={1}>
      <div
        style={{
          color,
          fontFamily: 'Inter, sans-serif',
          fontSize: '10px',
          fontWeight: 'bold',
          background: 'rgba(15, 20, 30, 0.88)',
          border: `1px solid ${color}`,
          borderRadius: '4px',
          padding: '3px 6px',
          whiteSpace: 'nowrap',
          pointerEvents: 'none',
          textShadow: '0 0 4px rgba(0,0,0,0.8)',
        }}
      >
        {text}
      </div>
    </Html>
  )
}

// ─── Room: walls, carpet floor, window/curtains, door, AC unit, posters ───
// Function: Room
function Room() {
  const wallColor = '#eceae4'
  const trimColor = '#1c1f26'

  return (
    <group>
      {/* carpet floor */}
      <mesh receiveShadow position={[0, -0.01, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[ROOM_WIDTH, ROOM_DEPTH]} />
        <meshStandardMaterial color="#b7b9c0" roughness={0.98} metalness={0} />
      </mesh>
      <mesh position={[0, 0, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[ROOM_WIDTH - 0.4, ROOM_DEPTH - 0.4]} />
        <meshStandardMaterial color="#aeb0b8" roughness={1} metalness={0} transparent opacity={0.4} />
      </mesh>

      {/* base trim */}
      {[
        [[0, 0.06, -ROOM_DEPTH / 2 + 0.02], [ROOM_WIDTH, 0.12, 0.04]],
        [[-ROOM_WIDTH / 2 + 0.02, 0.06, 0], [0.04, 0.12, ROOM_DEPTH]],
        [[ROOM_WIDTH / 2 - 0.02, 0.06, 0], [0.04, 0.12, ROOM_DEPTH]],
      ].map(([pos, size], i) => (
        <mesh key={i} position={pos}>
          <boxGeometry args={size} />
          <meshStandardMaterial color={trimColor} roughness={0.6} />
        </mesh>
      ))}

      {/* back wall */}
      <mesh position={[0, WALL_HEIGHT / 2, -ROOM_DEPTH / 2]} receiveShadow>
        <planeGeometry args={[ROOM_WIDTH, WALL_HEIGHT]} />
        <meshStandardMaterial color={wallColor} roughness={0.92} />
      </mesh>
      {/* left wall (with window) */}
      <mesh position={[-ROOM_WIDTH / 2, WALL_HEIGHT / 2, 0]} rotation={[0, Math.PI / 2, 0]} receiveShadow>
        <planeGeometry args={[ROOM_DEPTH, WALL_HEIGHT]} />
        <meshStandardMaterial color={wallColor} roughness={0.92} />
      </mesh>
      {/* right wall (with door) */}
      <mesh position={[ROOM_WIDTH / 2, WALL_HEIGHT / 2, 0]} rotation={[0, -Math.PI / 2, 0]} receiveShadow>
        <planeGeometry args={[ROOM_DEPTH, WALL_HEIGHT]} />
        <meshStandardMaterial color={wallColor} roughness={0.92} />
      </mesh>

      {/* window + blue curtains on the left wall */}
      <group position={[-ROOM_WIDTH / 2 + 0.015, WALL_HEIGHT * 0.56, -1.5]}>
        <mesh rotation={[0, Math.PI / 2, 0]}>
          <planeGeometry args={[4.2, 1.9]} />
          <meshStandardMaterial color="#bfe0f5" emissive="#bfe0f5" emissiveIntensity={0.3} />
        </mesh>
        <mesh position={[0.01, 0, 0]} rotation={[0, Math.PI / 2, 0]}>
          <planeGeometry args={[4.3, 2.0]} />
          <meshStandardMaterial color="#8f97a3" wireframe />
        </mesh>
        {[-1.9, -1.3, -0.7, -0.1, 0.5, 1.1, 1.7].map((z, i) => (
          <mesh key={i} position={[0.05, -0.05, z]} rotation={[0, Math.PI / 2, 0]}>
            <planeGeometry args={[0.34, 2.15]} />
            <meshStandardMaterial color="#3f6ea6" roughness={0.85} side={THREE.DoubleSide} />
          </mesh>
        ))}
      </group>

      {/* door on the right wall */}
      <group position={[ROOM_WIDTH / 2 - 0.015, 1.15, 3.6]}>
        <mesh rotation={[0, -Math.PI / 2, 0]}>
          <planeGeometry args={[1.15, 2.3]} />
          <meshStandardMaterial color="#8a5a34" roughness={0.65} />
        </mesh>
        <mesh position={[0, 0, 0.42]} rotation={[0, -Math.PI / 2, 0]}>
          <sphereGeometry args={[0.035, 8, 8]} />
          <meshStandardMaterial color="#d4af37" metalness={0.8} roughness={0.3} />
        </mesh>
      </group>

      {/* floor-standing AC unit */}
      <mesh position={[-1.4, 0.95, -ROOM_DEPTH / 2 + 0.25]} castShadow>
        <boxGeometry args={[0.55, 1.9, 0.32]} />
        <meshStandardMaterial color="#f4f4f4" roughness={0.45} />
      </mesh>
      <mesh position={[-1.4, 1.65, -ROOM_DEPTH / 2 + 0.42]}>
        <boxGeometry args={[0.45, 0.08, 0.02]} />
        <meshStandardMaterial color="#2563eb" emissive="#2563eb" emissiveIntensity={0.4} toneMapped={false} />
      </mesh>

      {/* wall posters (simple color-blocked placeholders) */}
      {[
        [-5.6, WALL_HEIGHT * 0.58, '#8fd3c4'],
        [5.4, WALL_HEIGHT * 0.6, '#f4c17a'],
        [1.2, WALL_HEIGHT * 0.55, '#93a7d8'],
      ].map(([x, y, color], i) => (
        <group key={i} position={[x, y, -ROOM_DEPTH / 2 + 0.012]}>
          <mesh>
            <planeGeometry args={[1.05, 1.5]} />
            <meshStandardMaterial color="#ffffff" roughness={0.9} />
          </mesh>
          <mesh position={[0, 0, 0.002]}>
            <planeGeometry args={[0.9, 1.3]} />
            <meshStandardMaterial color={color} roughness={0.85} />
          </mesh>
        </group>
      ))}

      {/* ceiling light panels */}
      {[-4, 0, 4].map((x, i) => (
        <mesh key={i} position={[x, WALL_HEIGHT - 0.03, 0]} rotation={[Math.PI / 2, 0, 0]}>
          <planeGeometry args={[2.4, 1.1]} />
          <meshStandardMaterial color="#ffffff" emissive="#ffffff" emissiveIntensity={0.55} toneMapped={false} />
        </mesh>
      ))}

      {/* small red fire-extinguisher cluster, by the door */}
      {[0, 0.28, 0.56].map((z, i) => (
        <mesh key={i} castShadow receiveShadow position={[ROOM_WIDTH / 2 - 0.45, 0.4, 2.4 + z]}>
          <cylinderGeometry args={[0.08, 0.09, 0.55, 12]} />
          <meshStandardMaterial color="#dc2626" metalness={0.4} roughness={0.4} />
        </mesh>
      ))}
    </group>
  )
}

// ─── PLC I/O signal set (simulated) ────────────────────────────────────────
const IO_INPUTS = [
  { key: 'X0', label: 'Item On Belt' },
  { key: 'X1', label: 'Gripper Closed FB' },
  { key: 'X2', label: 'Both Arms Home' },
  { key: 'X3', label: 'Conveyor Motor Run' },
  { key: 'X4', label: 'Source Rack Has Stock' },
  { key: 'X5', label: 'Dest Rack Has Space' },
  { key: 'X6', label: 'E-Stop Clear' },
  { key: 'X7', label: 'Cycle Start' },
]

const IO_OUTPUTS = [
  { key: 'Y0', label: 'Gripper Close Cmd' },
  { key: 'Y1', label: 'Arm 1 In Motion' },
  { key: 'Y2', label: 'Arm 2 In Motion' },
  { key: 'Y3', label: 'Conveyor Run Cmd' },
  { key: 'Y4', label: 'Belt Load Present' },
  { key: 'Y5', label: 'Dest Rack Full' },
  { key: 'Y6', label: 'Cycle Complete' },
  { key: 'Y7', label: 'Fault Lamp' },
]

// ─── Robot arm joint pose keyframes ─────────────────────────────────────────
// The robot is now a genuinely mobile gantry: it physically slides along a
// rail between a "source" station (parked at the rack) and a "dest" station
// (parked at the belt), carrying the held item with it while it travels.
// Because the carriage itself does the repositioning, the arm only ever
// needs one consistent reach-down gesture at either end — no more separate
// inward/outward joint angles per robot.
const ARM_PHASES = ['idle', 'reach_source', 'grip_close', 'lift', 'travel_to_dest', 'lower_dest', 'grip_open', 'travel_to_source']
const PHASE_HOLD_MS = {
  reach_source: 800,
  grip_close: 450,
  lift: 550,
  travel_to_dest: 1500,
  lower_dest: 700,
  grip_open: 400,
  travel_to_source: 1500,
}

const POSE_DOWN = { shoulder: 0.55, elbow: 1.65, wrist: -0.95 }
const POSE_CARRY = { shoulder: -0.3, elbow: 1.0, wrist: -0.55 }
const POSE_IDLE = { shoulder: -0.35, elbow: 0.9, wrist: -0.55 }

// Function: poseFor
function poseFor(phase) {
  switch (phase) {
    case 'reach_source': return { ...POSE_DOWN, grip: 0 }
    case 'grip_close': return { ...POSE_DOWN, grip: 1 }
    case 'lift': return { ...POSE_CARRY, grip: 1 }
    case 'travel_to_dest': return { ...POSE_CARRY, grip: 1 }
    case 'lower_dest': return { ...POSE_DOWN, grip: 1 }
    case 'grip_open': return { ...POSE_DOWN, grip: 0 }
    case 'travel_to_source': return { ...POSE_CARRY, grip: 0 }
    default: return { ...POSE_IDLE, grip: 0 }
  }
}

// Carriage rail position: 0 = parked at the source station (rack), 1 = at
// the destination station (belt).
// Function: railTargetFor
function railTargetFor(phase) {
  return phase === 'travel_to_dest' || phase === 'lower_dest' || phase === 'grip_open' ? 1 : 0
}

// ─── Rail track: a fixed bar the carriage rides along ──────────────────────
// Function: RailTrack
function RailTrack({ stationSource, stationDest }) {
  const midX = (stationSource[0] + stationDest[0]) / 2
  const midZ = (stationSource[2] + stationDest[2]) / 2
  const len = Math.hypot(stationDest[0] - stationSource[0], stationDest[2] - stationSource[2]) + 0.5
  const angle = Math.atan2(stationDest[2] - stationSource[2], stationDest[0] - stationSource[0])
  const y = stationSource[1]

  return (
    <group position={[midX, y, midZ]} rotation={[0, angle, 0]}>
      <mesh castShadow receiveShadow>
        <boxGeometry args={[len, 0.07, 0.1]} />
        <meshStandardMaterial color="#1f2937" metalness={0.6} roughness={0.35} />
      </mesh>
      {[-len / 2 + 0.15, len / 2 - 0.15].map((x, i) => (
        <mesh key={i} castShadow receiveShadow position={[x, -y / 2, 0]}>
          <boxGeometry args={[0.08, y, 0.08]} />
          <meshStandardMaterial color="#374151" metalness={0.55} roughness={0.4} />
        </mesh>
      ))}
    </group>
  )
}

// ─── 6-axis articulated (UR-style) robot arm, mounted on a sliding carriage
// Function: IndustrialRobotArm
function IndustrialRobotArm({ stationSource, stationDest, mirrored, phase, heldColor }) {
  const carriageRef = useRef(null)
  const shoulderRef = useRef(null)
  const elbowRef = useRef(null)
  const wristRef = useRef(null)
  const gripLRef = useRef(null)
  const gripRRef = useRef(null)
  const heldRef = useRef(null)
  const anglesRef = useRef({ shoulder: -0.35, elbow: 0.9, wrist: -0.55, grip: 0 })
  const railProgressRef = useRef(0)

  useFrame((_, delta) => {
    const target = poseFor(phase)
    const a = anglesRef.current
    const lerpSpeed = Math.min(delta * 3.2, 1)
    a.shoulder += (target.shoulder - a.shoulder) * lerpSpeed
    a.elbow += (target.elbow - a.elbow) * lerpSpeed
    a.wrist += (target.wrist - a.wrist) * lerpSpeed
    a.grip += (target.grip - a.grip) * lerpSpeed

    const railTarget = railTargetFor(phase)
    railProgressRef.current += (railTarget - railProgressRef.current) * Math.min(delta * 1.6, 1)
    const p = railProgressRef.current

    if (carriageRef.current) {
      carriageRef.current.position.set(
        stationSource[0] + (stationDest[0] - stationSource[0]) * p,
        stationSource[1] + (stationDest[1] - stationSource[1]) * p,
        stationSource[2] + (stationDest[2] - stationSource[2]) * p,
      )
    }
    if (shoulderRef.current) shoulderRef.current.rotation.x = a.shoulder
    if (elbowRef.current) elbowRef.current.rotation.x = a.elbow
    if (wristRef.current) wristRef.current.rotation.x = a.wrist
    if (gripLRef.current) gripLRef.current.position.x = -0.025 - a.grip * 0.055
    if (gripRRef.current) gripRRef.current.position.x = 0.025 + a.grip * 0.055
    if (heldRef.current) heldRef.current.visible = Boolean(heldColor) && a.grip > 0.5
  })

  const armColor = '#e8eaed'
  const jointColor = '#14b8a6'
  const isActive = phase !== 'idle'

  return (
    <>
      <RailTrack stationSource={stationSource} stationDest={stationDest} />

      <group ref={carriageRef} position={stationSource} rotation={[0, mirrored ? Math.PI : 0, 0]}>
        {/* carriage block riding the rail — bright safety-orange so it reads
            as "the robot" and doesn't visually fuse with the slate-toned rack */}
        <mesh castShadow receiveShadow position={[0, -0.09, 0]}>
          <boxGeometry args={[0.4, 0.16, 0.42]} />
          <meshStandardMaterial color="#ea580c" metalness={0.5} roughness={0.35} />
        </mesh>
        <mesh position={[0, -0.02, 0]}>
          <boxGeometry args={[0.22, 0.02, 0.22]} />
          <meshStandardMaterial color={jointColor} emissive={jointColor} emissiveIntensity={isActive ? 0.6 : 0.15} toneMapped={false} />
        </mesh>

        <mesh castShadow receiveShadow>
          <cylinderGeometry args={[0.14, 0.14, 0.14, 20]} />
          <meshStandardMaterial color={jointColor} emissive={jointColor} emissiveIntensity={isActive ? 0.35 : 0.1} metalness={0.5} roughness={0.3} />
        </mesh>

        <group ref={shoulderRef} position={[0, 0.08, 0]}>
          <mesh castShadow receiveShadow position={[0, 0.28, 0]}>
            <capsuleGeometry args={[0.095, 0.5, 4, 10]} />
            <meshStandardMaterial color={armColor} metalness={0.3} roughness={0.35} />
          </mesh>

          <group ref={elbowRef} position={[0, 0.56, 0]}>
            <mesh castShadow receiveShadow>
              <sphereGeometry args={[0.11, 16, 16]} />
              <meshStandardMaterial color={jointColor} emissive={jointColor} emissiveIntensity={isActive ? 0.35 : 0.1} metalness={0.5} roughness={0.3} />
            </mesh>
            <mesh castShadow receiveShadow position={[0, 0.25, 0]}>
              <capsuleGeometry args={[0.08, 0.42, 4, 10]} />
              <meshStandardMaterial color={armColor} metalness={0.3} roughness={0.35} />
            </mesh>

            <group ref={wristRef} position={[0, 0.5, 0]}>
              <mesh castShadow receiveShadow>
                <sphereGeometry args={[0.09, 14, 14]} />
                <meshStandardMaterial color={jointColor} emissive={jointColor} emissiveIntensity={isActive ? 0.35 : 0.1} metalness={0.5} roughness={0.3} />
              </mesh>
              <mesh castShadow receiveShadow position={[0, 0.14, 0]}>
                <cylinderGeometry args={[0.06, 0.06, 0.18, 12]} />
                <meshStandardMaterial color="#9ca3af" metalness={0.6} roughness={0.3} />
              </mesh>
              <mesh ref={gripLRef} castShadow receiveShadow position={[-0.025, 0.24, 0]}>
                <boxGeometry args={[0.02, 0.12, 0.06]} />
                <meshStandardMaterial color="#1f2937" metalness={0.5} roughness={0.4} />
              </mesh>
              <mesh ref={gripRRef} castShadow receiveShadow position={[0.025, 0.24, 0]}>
                <boxGeometry args={[0.02, 0.12, 0.06]} />
                <meshStandardMaterial color="#1f2937" metalness={0.5} roughness={0.4} />
              </mesh>
              {/* held item, visible only while gripping */}
              <mesh ref={heldRef} castShadow receiveShadow position={[0, 0.32, 0]} visible={false}>
                <boxGeometry args={[0.15, 0.13, 0.15]} />
                <meshStandardMaterial color={heldColor || '#94a3b8'} emissive={heldColor || '#94a3b8'} emissiveIntensity={0.4} metalness={0.4} roughness={0.35} />
              </mesh>
            </group>
          </group>
        </group>
      </group>
    </>
  )
}

// ─── Table-mounted conveyor belt ───────────────────────────────────────────
// Function: TableConveyor
function TableConveyor({ length, y }) {
  const rollerRefs = useRef([])
  const beltWidth = 0.55
  const rollerCount = Math.max(6, Math.round(length / 0.35))

  useFrame((_, delta) => {
    const half = length / 2
    rollerRefs.current.forEach((mesh) => {
      if (!mesh) return
      let x = mesh.position.x + delta * 1.4
      if (x > half) x -= length
      mesh.position.x = x
    })
  })

  return (
    <group position={[0, y, 0]}>
      <mesh castShadow receiveShadow>
        <boxGeometry args={[length, 0.08, beltWidth]} />
        <meshStandardMaterial color="#1f2937" metalness={0.5} roughness={0.45} />
      </mesh>
      {[-1, 1].map((side) => (
        <mesh key={side} castShadow receiveShadow position={[0, 0.06, (beltWidth / 2 - 0.02) * side]}>
          <boxGeometry args={[length, 0.06, 0.04]} />
          <meshStandardMaterial color="#334155" metalness={0.6} roughness={0.3} />
        </mesh>
      ))}
      {Array.from({ length: rollerCount }, (_, i) => {
        const x = (i / (rollerCount - 1) - 0.5) * (length - 0.15)
        return (
          <mesh key={i} ref={(el) => { rollerRefs.current[i] = el }} position={[x, 0.045, 0]}>
            <boxGeometry args={[0.03, 0.008, beltWidth - 0.1]} />
            <meshStandardMaterial color="#0ea5e9" emissive="#0ea5e9" emissiveIntensity={0.5} toneMapped={false} />
          </mesh>
        )
      })}
    </group>
  )
}

// ─── Item physically riding the belt between the two robots ───────────────
const BELT_TRAVEL_MS = 3000
const BELT_ENTRY_X = -1.85
const BELT_EXIT_X = 1.85
const BELT_ITEM_Y = 1.0

// A one-shot 3-items-then-stop demo reads as "broken" once it settles — the
// source rack auto-restocks an emptied slot, and the destination rack
// auto-ships (clears) once full, so the cell keeps demonstrating indefinitely
// for as long as the simulation is running.
const RACK1_REPLENISH_MS = 1800
const RACK2_SHIP_MS = 1800

// Rail stations for each carriage — "source" is parked at the rack,
// "dest" is parked at the belt.
const ARM1_STATION_SOURCE = [-4.0, 0.9, -0.6]
const ARM1_STATION_DEST = [-2.0, 0.9, -0.15]
const ARM2_STATION_SOURCE = [2.0, 0.9, 0.15]
const ARM2_STATION_DEST = [4.0, 0.9, 0.6]

// Function: ConveyorRidingItem
function ConveyorRidingItem({ startedAt, color }) {
  const ref = useRef(null)

  useFrame(() => {
    if (!ref.current) return
    const progress = Math.min((Date.now() - startedAt) / BELT_TRAVEL_MS, 1)
    ref.current.position.x = BELT_ENTRY_X + (BELT_EXIT_X - BELT_ENTRY_X) * progress
  })

  return (
    <mesh ref={ref} castShadow receiveShadow position={[BELT_ENTRY_X, BELT_ITEM_Y, 0]}>
      <boxGeometry args={[0.2, 0.17, 0.2]} />
      <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.35} metalness={0.4} roughness={0.35} />
    </mesh>
  )
}

// ─── Manufacturing workbench: table, conveyor, fixtures ────────────────────
// Function: WorkTable
function WorkTable() {
  const tableLength = 5.6
  const tableWidth = 1.9
  const tableHeight = 0.85

  return (
    <group>
      <mesh castShadow receiveShadow position={[0, tableHeight, 0]}>
        <boxGeometry args={[tableLength, 0.08, tableWidth]} />
        <meshStandardMaterial color="#c7cbd1" metalness={0.5} roughness={0.4} />
      </mesh>

      {[
        [-tableLength / 2 + 0.15, -tableWidth / 2 + 0.15],
        [tableLength / 2 - 0.15, -tableWidth / 2 + 0.15],
        [-tableLength / 2 + 0.15, tableWidth / 2 - 0.15],
        [tableLength / 2 - 0.15, tableWidth / 2 - 0.15],
      ].map(([x, z], i) => (
        <mesh key={i} castShadow receiveShadow position={[x, tableHeight / 2, z]}>
          <boxGeometry args={[0.08, tableHeight, 0.08]} />
          <meshStandardMaterial color="#6b7280" metalness={0.6} roughness={0.3} />
        </mesh>
      ))}

      {/* open lower shelf */}
      <mesh receiveShadow position={[0, 0.05, 0]}>
        <boxGeometry args={[tableLength - 0.3, 0.04, tableWidth - 0.3]} />
        <meshStandardMaterial color="#eef0f2" metalness={0.2} roughness={0.6} />
      </mesh>

      <TableConveyor length={tableLength - 1.1} y={tableHeight + 0.06} />

      {/* sensor fixture posts */}
      {[-0.7, 0, 0.7].map((x, i) => (
        <group key={i} position={[x, tableHeight + 0.06, 0.42]}>
          <mesh castShadow receiveShadow position={[0, 0.28, 0]}>
            <boxGeometry args={[0.045, 0.55, 0.1]} />
            <meshStandardMaterial color="#4b5563" metalness={0.6} roughness={0.3} />
          </mesh>
          <mesh position={[0, 0.5, 0.03]}>
            <boxGeometry args={[0.06, 0.03, 0.03]} />
            <meshStandardMaterial color="#22d3ee" emissive="#22d3ee" emissiveIntensity={0.6} toneMapped={false} />
          </mesh>
        </group>
      ))}
    </group>
  )
}

// ─── Side rack: 3 stacked compartments, one item each ──────────────────────
// Function: SideRack
function SideRack({ position, label, slots, highlighted }) {
  const levels = [0, 1, 2]
  const levelSpacing = 0.42
  const footprint = 0.75
  const postColor = highlighted ? '#facc15' : '#f97316'

  return (
    <group position={position}>
      <mesh castShadow receiveShadow position={[0, 0.03, 0]}>
        <boxGeometry args={[footprint + 0.15, 0.05, footprint + 0.15]} />
        <meshStandardMaterial color="#1e293b" metalness={0.5} roughness={0.5} />
      </mesh>

      {[[0.32, 0.32], [-0.32, 0.32], [0.32, -0.32], [-0.32, -0.32]].map(([x, z], i) => (
        <mesh key={i} castShadow receiveShadow position={[x, 0.75, z]}>
          <boxGeometry args={[0.05, 1.5, 0.05]} />
          <meshStandardMaterial color={postColor} metalness={0.5} roughness={0.35} />
        </mesh>
      ))}

      {levels.map((level) => {
        const slot = level + 1
        const color = slots[slot]
        const y = 0.25 + level * levelSpacing
        return (
          <group key={level}>
            <mesh castShadow receiveShadow position={[0, y, 0]}>
              <boxGeometry args={[footprint, 0.03, footprint]} />
              <meshStandardMaterial color="#64748b" metalness={0.4} roughness={0.5} />
            </mesh>
            {color ? (
              <mesh castShadow receiveShadow position={[0, y + 0.14, 0]}>
                <boxGeometry args={[0.34, 0.22, 0.34]} />
                <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.3} metalness={0.4} roughness={0.35} />
              </mesh>
            ) : (
              <mesh position={[0, y + 0.04, 0]}>
                <boxGeometry args={[0.3, 0.01, 0.3]} />
                <meshStandardMaterial color="#94a3b8" wireframe />
              </mesh>
            )}
          </group>
        )
      })}

      <ProximityLabel position={[0, 1.65, 0]} text={label} color={highlighted ? '#facc15' : '#fb923c'} />
    </group>
  )
}

// Function: Scene
function Scene({ arm1Phase, arm2Phase, heldColors, rack1, rack2, rack1Active, rack2Active, beltItem }) {
  return (
    <group>
      <Room />
      <hemisphereLight args={['#f5f6f8', '#9a9da3', 0.75]} />
      <ambientLight intensity={0.55} color="#ffffff" />
      <pointLight position={[3, 4.5, 3]} intensity={1.1} castShadow color="#ffffff" />
      <pointLight position={[-3, 4.5, -2]} intensity={0.9} castShadow color="#ffffff" />
      <directionalLight position={[2, 4.8, 4]} intensity={1.0} castShadow color="#ffffff" />

      <WorkTable />

      <SideRack position={[-5.3, 0, -0.6]} label="Source Rack" slots={rack1} highlighted={rack1Active} />
      <SideRack position={[5.3, 0, 0.6]} label="Destination Rack" slots={rack2} highlighted={rack2Active} />

      {beltItem && <ConveyorRidingItem startedAt={beltItem.startedAt} color={beltItem.color} />}

      <IndustrialRobotArm stationSource={ARM1_STATION_SOURCE} stationDest={ARM1_STATION_DEST} mirrored={false} phase={arm1Phase} heldColor={heldColors['ARM-1']} />
      <IndustrialRobotArm stationSource={ARM2_STATION_SOURCE} stationDest={ARM2_STATION_DEST} mirrored phase={arm2Phase} heldColor={heldColors['ARM-2']} />

      <ProximityLabel position={[0, 3.4, 0]} text="ROBOTICS TRAINING CELL" color="#45b7d1" />
    </group>
  )
}

// ─── Main component ─────────────────────────────────────────────────────
const RACK1_START = { 1: '#f43f5e', 2: '#f59e0b', 3: '#38bdf8' }
const RACK2_START = { 1: null, 2: null, 3: null }

// ── ARM-1 tick: feeder — pick from rack1, place on belt ─────────────────────
// Function: runArm1Tick
function runArm1Tick(now, st, nextPhases, nextHeld, flags, runningRef, rack1Ref, beltItemRef, rack1RefillAtRef, setRack1, setBeltItem) {
  const id = 'ARM-1'
  if (!runningRef.current) {
    if (st.phaseIdx !== 0) { st.phaseIdx = 0; st.holdUntil = 0; st.slot = null; flags.phasesChanged = true }
    nextPhases[id] = 'idle'
    return
  }
  if (ARM_PHASES[st.phaseIdx] === 'idle') {
    const occupiedSlot = [1, 2, 3].find((s) => rack1Ref.current[s])
    if (occupiedSlot && !beltItemRef.current) {
      st.slot = occupiedSlot
      st.phaseIdx = 1
      st.holdUntil = now + PHASE_HOLD_MS.reach_source
      flags.phasesChanged = true
      nextPhases[id] = ARM_PHASES[st.phaseIdx]
    }
    return
  }
  if (now < st.holdUntil) return

  const phase = ARM_PHASES[st.phaseIdx]
  if (phase === 'grip_close') {
    const color = rack1Ref.current[st.slot]
    const nextRack1 = { ...rack1Ref.current, [st.slot]: null }
    rack1Ref.current = nextRack1
    setRack1(nextRack1)
    rack1RefillAtRef.current = { ...rack1RefillAtRef.current, [st.slot]: now + RACK1_REPLENISH_MS }
    nextHeld[id] = color
    flags.heldChanged = true
  }
  if (phase === 'lower_dest') {
    const color = nextHeld[id]
    const item = { startedAt: now, color }
    beltItemRef.current = item
    setBeltItem(item)
    nextHeld[id] = null
    flags.heldChanged = true
  }
  st.phaseIdx = (st.phaseIdx + 1) % ARM_PHASES.length
  st.holdUntil = now + (PHASE_HOLD_MS[ARM_PHASES[st.phaseIdx]] || 0)
  flags.phasesChanged = true
  nextPhases[id] = ARM_PHASES[st.phaseIdx]
}

// Function: _arm2ReadySlot
function _arm2ReadySlot(now, beltItemRef, rack2Ref) {
  const item = beltItemRef.current
  const arrived = item && now - item.startedAt >= BELT_TRAVEL_MS
  const emptySlot = [1, 2, 3].find((s) => !rack2Ref.current[s])
  return arrived && emptySlot ? emptySlot : null
}

// ── ARM-2 tick: receiver — pick from belt, place into rack2 ─────────────────
// Function: runArm2Tick
function runArm2Tick(now, st, nextPhases, nextHeld, flags, runningRef, beltItemRef, rack2Ref, rack2ShipAtRef, setBeltItem, setRack2) {
  const id = 'ARM-2'
  if (!runningRef.current) {
    if (st.phaseIdx !== 0) { st.phaseIdx = 0; st.holdUntil = 0; st.slot = null; flags.phasesChanged = true }
    nextPhases[id] = 'idle'
    return
  }
  if (ARM_PHASES[st.phaseIdx] === 'idle') {
    const emptySlot = _arm2ReadySlot(now, beltItemRef, rack2Ref)
    if (emptySlot) {
      st.slot = emptySlot
      st.phaseIdx = 1
      st.holdUntil = now + PHASE_HOLD_MS.reach_source
      flags.phasesChanged = true
      nextPhases[id] = ARM_PHASES[st.phaseIdx]
    }
    return
  }
  if (now < st.holdUntil) return

  const phase = ARM_PHASES[st.phaseIdx]
  if (phase === 'grip_close') {
    const item = beltItemRef.current
    nextHeld[id] = item ? item.color : '#94a3b8'
    beltItemRef.current = null
    setBeltItem(null)
    flags.heldChanged = true
  }
  if (phase === 'lower_dest') {
    const color = nextHeld[id]
    const nextRack2 = { ...rack2Ref.current, [st.slot]: color }
    rack2Ref.current = nextRack2
    setRack2(nextRack2)
    if ([1, 2, 3].every((s) => nextRack2[s]) && !rack2ShipAtRef.current) {
      rack2ShipAtRef.current = now + RACK2_SHIP_MS
    }
    nextHeld[id] = null
    flags.heldChanged = true
  }
  st.phaseIdx = (st.phaseIdx + 1) % ARM_PHASES.length
  st.holdUntil = now + (PHASE_HOLD_MS[ARM_PHASES[st.phaseIdx]] || 0)
  flags.phasesChanged = true
  nextPhases[id] = ARM_PHASES[st.phaseIdx]
}

// ── Keep the loop going indefinitely: restock the source rack and ship out
//    the destination rack once full, instead of freezing after one pass ─────
// Function: runRackReplenishAndShip
function runRackReplenishAndShip(now, runningRef, rack1Ref, rack1RefillAtRef, rack2Ref, rack2ShipAtRef, setRack1, setRack2) {
  if (!runningRef.current) return

  let rack1Touched = false
  const nextRack1 = { ...rack1Ref.current }
  ;[1, 2, 3].forEach((slot) => {
    const dueAt = rack1RefillAtRef.current[slot]
    if (dueAt && now >= dueAt && !nextRack1[slot]) {
      nextRack1[slot] = RACK1_START[slot]
      rack1RefillAtRef.current = { ...rack1RefillAtRef.current, [slot]: null }
      rack1Touched = true
    }
  })
  if (rack1Touched) {
    rack1Ref.current = nextRack1
    setRack1(nextRack1)
  }

  if (rack2ShipAtRef.current && now >= rack2ShipAtRef.current) {
    const clearedRack2 = { 1: null, 2: null, 3: null }
    rack2Ref.current = clearedRack2
    setRack2(clearedRack2)
    rack2ShipAtRef.current = null
  }
}

// Function: computeIoSignals
function computeIoSignals(runningRef, rack1Ref, rack2Ref, beltItemRef, nextPhases, nextHeld) {
  const rack1HasStock = [1, 2, 3].some((s) => rack1Ref.current[s])
  const rack2HasSpace = [1, 2, 3].some((s) => !rack2Ref.current[s])
  const rack2Full = !rack2HasSpace
  return {
    X0: Boolean(beltItemRef.current),
    X1: Boolean(nextHeld['ARM-1'] || nextHeld['ARM-2']),
    X2: nextPhases['ARM-1'] === 'idle' && nextPhases['ARM-2'] === 'idle',
    X3: runningRef.current,
    X4: rack1HasStock,
    X5: rack2HasSpace,
    X6: true,
    X7: runningRef.current,
    Y0: Boolean(nextHeld['ARM-1'] || nextHeld['ARM-2']),
    Y1: nextPhases['ARM-1'] !== 'idle',
    Y2: nextPhases['ARM-2'] !== 'idle',
    Y3: runningRef.current,
    Y4: Boolean(beltItemRef.current),
    Y5: rack2Full,
    Y6: nextPhases['ARM-1'] === 'travel_to_source' || nextPhases['ARM-2'] === 'travel_to_source',
    Y7: false,
  }
}

// Function: RackViewer3D
export default function RackViewer3D() {
  const [running, setRunning] = useState(false)
  const [plcType, setPlcType] = useState('PLC Types')
  const [trainingProgram, setTrainingProgram] = useState('Pick and Place')
  const [showIoTable, setShowIoTable] = useState(false)
  const [showIoMonitor, setShowIoMonitor] = useState(false)
  const [view, setView] = useState('overview')
  const [autoRotate, setAutoRotate] = useState(false)
  const [armPhases, setArmPhases] = useState({ 'ARM-1': 'idle', 'ARM-2': 'idle' })
  const [heldColors, setHeldColors] = useState({ 'ARM-1': null, 'ARM-2': null })
  const [rack1, setRack1] = useState(RACK1_START)
  const [rack2, setRack2] = useState(RACK2_START)
  const [beltItem, setBeltItem] = useState(null)
  const [ioSignals, setIoSignals] = useState(() => {
    const s = {}
    IO_INPUTS.concat(IO_OUTPUTS).forEach((sig) => { s[sig.key] = false })
    return s
  })

  const controlsRef = useRef(null)
  const runningRef = useRef(false)
  const armPhasesRef = useRef(armPhases)
  const heldColorsRef = useRef(heldColors)
  const rack1Ref = useRef(RACK1_START)
  const rack2Ref = useRef(RACK2_START)
  const beltItemRef = useRef(null)
  const rack1RefillAtRef = useRef({ 1: null, 2: null, 3: null })
  const rack2ShipAtRef = useRef(null)
  const stateRef = useRef({
    'ARM-1': { phaseIdx: 0, holdUntil: 0, slot: null },
    'ARM-2': { phaseIdx: 0, holdUntil: 0, slot: null },
  })
  const lastTickAtRef = useRef(Date.now())
  const tickRef = useRef(null)

  useEffect(() => { runningRef.current = running }, [running])

  // Function: tick
  const tick = () => {
    const now = Date.now()
    const nextPhases = { ...armPhasesRef.current }
    const nextHeld = { ...heldColorsRef.current }
    const flags = { phasesChanged: false, heldChanged: false }

    runArm1Tick(now, stateRef.current['ARM-1'], nextPhases, nextHeld, flags,
      runningRef, rack1Ref, beltItemRef, rack1RefillAtRef, setRack1, setBeltItem)

    runArm2Tick(now, stateRef.current['ARM-2'], nextPhases, nextHeld, flags,
      runningRef, beltItemRef, rack2Ref, rack2ShipAtRef, setBeltItem, setRack2)

    runRackReplenishAndShip(now, runningRef, rack1Ref, rack1RefillAtRef, rack2Ref, rack2ShipAtRef, setRack1, setRack2)

    if (flags.phasesChanged) { armPhasesRef.current = nextPhases; setArmPhases(nextPhases) }
    if (flags.heldChanged) { heldColorsRef.current = nextHeld; setHeldColors(nextHeld) }

    if (flags.phasesChanged || flags.heldChanged) {
      setIoSignals(computeIoSignals(runningRef, rack1Ref, rack2Ref, beltItemRef, nextPhases, nextHeld))
    }
  }

  tickRef.current = tick

  useEffect(() => {
    lastTickAtRef.current = Date.now()
    const timer = window.setInterval(() => tickRef.current?.(), 60)
    return () => window.clearInterval(timer)
  }, [])

  // Function: handleStart
  const handleStart = () => {
    const freshRack1 = { ...RACK1_START }
    const freshRack2 = { ...RACK2_START }
    rack1Ref.current = freshRack1
    rack2Ref.current = freshRack2
    beltItemRef.current = null
    rack1RefillAtRef.current = { 1: null, 2: null, 3: null }
    rack2ShipAtRef.current = null
    stateRef.current = {
      'ARM-1': { phaseIdx: 0, holdUntil: 0, slot: null },
      'ARM-2': { phaseIdx: 0, holdUntil: 0, slot: null },
    }
    heldColorsRef.current = { 'ARM-1': null, 'ARM-2': null }
    armPhasesRef.current = { 'ARM-1': 'idle', 'ARM-2': 'idle' }
    setRack1(freshRack1)
    setRack2(freshRack2)
    setBeltItem(null)
    setHeldColors({ 'ARM-1': null, 'ARM-2': null })
    setArmPhases({ 'ARM-1': 'idle', 'ARM-2': 'idle' })
    setRunning(true)
  }

  const plcOptions = ['PLC Types', 'TIA PLCSIM', 'GXWorks']
  const programOptions = ['Pick and Place', 'Sorting']
  const rack1Active = armPhases['ARM-1'] !== 'idle'
  const rack2Active = armPhases['ARM-2'] !== 'idle'

  return (
    <div className="relative w-full h-screen bg-black overflow-hidden">
      <Canvas
        shadows={{ type: THREE.PCFShadowMap }}
        camera={{ position: CAMERA_PRESETS.overview.position, fov: 50, near: 0.1, far: 100 }}
        gl={{ antialias: true, alpha: false }}
      >
        <Suspense fallback={null}>
          <fog attach="fog" args={['#dfe1e6', 18, 32]} />
          <color attach="background" args={['#dfe1e6']} />

          <Scene
            arm1Phase={armPhases['ARM-1']}
            arm2Phase={armPhases['ARM-2']}
            heldColors={heldColors}
            rack1={rack1}
            rack2={rack2}
            rack1Active={rack1Active}
            rack2Active={rack2Active}
            beltItem={beltItem}
          />

          <CameraRig view={view} controlsRef={controlsRef} />

          <OrbitControls
            ref={controlsRef}
            makeDefault
            autoRotate={autoRotate}
            autoRotateSpeed={1.2}
            enableRotate
            enableZoom
            enablePan
            minPolarAngle={0.1}
            maxPolarAngle={Math.PI / 2.05}
            target={CAMERA_PRESETS[view]?.target || CAMERA_PRESETS.overview.target}
            minDistance={2.5}
            maxDistance={22}
          />
        </Suspense>
      </Canvas>

      {/* Top toolbar — mirrors the reference PLC training UI */}
      <div className="absolute top-3 left-3 flex flex-wrap items-start gap-2">
        <button
          onClick={() => setShowIoTable((v) => !v)}
          className={`px-3 py-2 rounded shadow text-sm font-medium transition-colors ${showIoTable ? 'bg-blue-600 text-white' : 'bg-white text-gray-800 hover:bg-gray-100'}`}
        >
          View I/O table
        </button>
        <button
          onClick={() => setShowIoMonitor((v) => !v)}
          className={`px-3 py-2 rounded shadow text-sm font-medium transition-colors block ${showIoMonitor ? 'bg-blue-600 text-white' : 'bg-white text-gray-800 hover:bg-gray-100'}`}
        >
          View I/O MON
        </button>

        <select
          value={plcType}
          onChange={(e) => setPlcType(e.target.value)}
          className="px-3 py-2 rounded shadow text-sm font-medium bg-white text-gray-800 border-none outline-none"
        >
          {plcOptions.map((opt) => (
            <option key={opt} value={opt}>{opt}</option>
          ))}
        </select>

        <select
          value={trainingProgram}
          onChange={(e) => setTrainingProgram(e.target.value)}
          className="px-3 py-2 rounded shadow text-sm font-medium bg-white text-gray-800 border-none outline-none"
        >
          {programOptions.map((opt) => (
            <option key={opt} value={opt}>{opt}</option>
          ))}
        </select>

        <div className="flex flex-col gap-2">
          <button
            onClick={handleStart}
            disabled={running}
            className="px-4 py-2 rounded shadow text-sm font-semibold bg-white text-gray-800 hover:bg-emerald-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Start simulation
          </button>
          <button
            onClick={() => setRunning(false)}
            disabled={!running}
            className="px-4 py-2 rounded shadow text-sm font-semibold bg-white text-gray-800 hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Stop simulation
          </button>
        </div>
      </div>

      {/* View + auto-rotate controls */}
      <div className="absolute bottom-3 left-3 bg-white/95 rounded-lg shadow p-2 flex flex-col gap-2">
        <div className="grid grid-cols-4 gap-1">
          {[
            ['overview', 'Overview'],
            ['front', 'Front'],
            ['side', 'Side'],
            ['top', 'Top'],
          ].map(([key, label]) => (
            <button
              key={key}
              onClick={() => setView(key)}
              className={`px-2 py-1 rounded text-[11px] font-semibold transition-colors ${view === key ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
            >
              {label}
            </button>
          ))}
        </div>
        <button
          onClick={() => setAutoRotate((v) => !v)}
          className={`px-2 py-1.5 rounded text-xs font-semibold transition-colors ${autoRotate ? 'bg-amber-500 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
        >
          {autoRotate ? 'Stop Auto-Rotate' : 'Start Auto-Rotate'}
        </button>
      </div>

      {/* Status strip */}
      <div className="absolute bottom-3 right-3 bg-white/95 rounded-lg shadow px-3 py-2 text-xs text-gray-700">
        <p className="font-semibold text-gray-900">{plcType} · {trainingProgram}</p>
        <p>Status: <span className={running ? 'text-emerald-600 font-semibold' : 'text-gray-500'}>{running ? 'RUNNING' : 'STOPPED'}</span></p>
        <p>Arm 1 (feeder): {armPhases['ARM-1']} · Arm 2 (receiver): {armPhases['ARM-2']}</p>
      </div>

      {/* I/O Table */}
      {showIoTable && (
        <div className="absolute top-24 right-3 bg-white/97 rounded-lg shadow-lg p-3 w-64 text-xs">
          <div className="font-bold text-gray-900 mb-2">I/O Table</div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <p className="text-[10px] uppercase tracking-wide text-gray-400 mb-1">Inputs</p>
              {IO_INPUTS.map((sig) => (
                <div key={sig.key} className="flex items-center justify-between py-0.5">
                  <span className="text-gray-600">{sig.key}</span>
                  <span className={`w-2.5 h-2.5 rounded-full ${ioSignals[sig.key] ? 'bg-emerald-500' : 'bg-gray-300'}`} />
                </div>
              ))}
            </div>
            <div>
              <p className="text-[10px] uppercase tracking-wide text-gray-400 mb-1">Outputs</p>
              {IO_OUTPUTS.map((sig) => (
                <div key={sig.key} className="flex items-center justify-between py-0.5">
                  <span className="text-gray-600">{sig.key}</span>
                  <span className={`w-2.5 h-2.5 rounded-full ${ioSignals[sig.key] ? 'bg-amber-500' : 'bg-gray-300'}`} />
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* I/O Monitor */}
      {showIoMonitor && (
        <div className="absolute top-24 right-3 bg-slate-900/95 rounded-lg shadow-lg p-3 w-72 text-xs font-mono text-emerald-300" style={{ marginTop: showIoTable ? 340 : 0 }}>
          <div className="font-bold text-white mb-2">I/O Monitor</div>
          {IO_INPUTS.concat(IO_OUTPUTS).map((sig) => (
            <div key={sig.key} className="flex items-center justify-between py-0.5">
              <span className="text-slate-300">{sig.key} — {sig.label}</span>
              <span className={ioSignals[sig.key] ? 'text-emerald-400 font-bold' : 'text-slate-500'}>{ioSignals[sig.key] ? '1' : '0'}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
