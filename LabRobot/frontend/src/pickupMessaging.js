// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: LabRobot — frontend/src (pickupMessaging.js)
// Date: 2026-05-30
// ---------------------------------------------------------------------------
export const PICKUP_MESSAGE_EVENT = 'labPickupMessage'
export const PICKUP_SUCCESS_EVENT = 'placementFetchSuccess'

let pickupSequence = 0

// Function: nextPickupMessageId
function nextPickupMessageId() {
  pickupSequence += 1
  return `pickup-msg-${pickupSequence}`
}

// Function: emitPickupMessage
export function emitPickupMessage(stage, payload = {}) {
  const detail = {
    id: nextPickupMessageId(),
    stage,
    timestamp: new Date().toISOString(),
    ...payload,
  }

  document.dispatchEvent(new CustomEvent(PICKUP_MESSAGE_EVENT, { detail }))
  return detail
}

// Function: emitPickupSuccess
export function emitPickupSuccess(payload = {}) {
  document.dispatchEvent(new CustomEvent(PICKUP_SUCCESS_EVENT, { detail: payload }))
}