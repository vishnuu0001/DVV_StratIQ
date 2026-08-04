// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: InfraRationalization — frontend/src/theme (azurePortalTheme.js)
// Date: 2026-08-04
// ---------------------------------------------------------------------------
import { createLightTheme, createDarkTheme } from '@fluentui/react-components'

// Brand ramp seeded from the module's existing accent (#0078d4, see
// tailwind.config.js brand.blue) so the Fluent theme stays continuous with
// the rest of the app's palette instead of introducing an unrelated hue.
const azureBrandRamp = {
  10: '#020305',
  20: '#0D1F2C',
  30: '#0F2A3D',
  40: '#0F354E',
  50: '#0D4060',
  60: '#0A4C72',
  70: '#005985',
  80: '#0066A0',
  90: '#0078D4',
  100: '#1A86DA',
  110: '#3994DF',
  120: '#57A2E4',
  130: '#78B2E9',
  140: '#9CC3EF',
  150: '#C2D8F5',
  160: '#E6EFFC',
}

export const azureLightTheme = createLightTheme(azureBrandRamp)

// The real Azure Portal command bar and left nav blade read as navy, not
// Fluent's default near-black charcoal — override the neutral background
// tokens after generating the base dark theme rather than hand-rolling one.
export const azureNavyDarkTheme = {
  ...createDarkTheme(azureBrandRamp),
  colorNeutralBackground1: '#14233B',
  colorNeutralBackground1Hover: '#1C304D',
  colorNeutralBackground1Pressed: '#0F1B2E',
  colorNeutralBackground2: '#0F1B2E',
  colorNeutralBackground2Hover: '#1C304D',
  colorNeutralForeground1: '#F3F2F1',
  colorNeutralForeground2: '#C8C6C4',
  colorNeutralForeground2Hover: '#F3F2F1',
  colorNeutralStroke1: 'rgba(255, 255, 255, 0.08)',
  colorNeutralStroke2: 'rgba(255, 255, 255, 0.14)',
}

// Sidebar active-item treatment — not a Fluent theme token, just shared
// constants so Sidebar.jsx and any future module copy stay in sync.
export const sidebarActiveStyles = {
  background: 'rgba(0, 120, 212, 0.16)',
  accentBar: '#0078D4',
}
