// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: InfraRationalization — frontend/src/components (AppHeader.jsx)
// Date: 2026-08-04
// ---------------------------------------------------------------------------
import { useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Button,
  Text,
  Badge,
  FluentProvider,
  makeStyles,
  tokens,
} from '@fluentui/react-components'
import {
  ServerRegular,
  SignOutRegular,
  HomeRegular,
  ArrowLeftRegular,
  SearchRegular,
  ShieldCheckmarkRegular,
} from '@fluentui/react-icons'
import { AppContext } from '../App.jsx'
import { getPortalHomeUrl, logoutFromPortal } from '../api/client.js'
import { azureNavyDarkTheme } from '../theme/azurePortalTheme.js'
import Breadcrumb from './Breadcrumb.jsx'

/**
 * Shared top navigation bar for all Infra Scan pages.
 *
 * Props:
 *   title      – main heading text
 *   subtitle   – optional secondary info shown below title
 *   backTo     – if provided, shows a ← back arrow button routing to this path
 *   rightSlot  – optional JSX rendered between the chip and Portal button (e.g. Export button)
 */

const useStyles = makeStyles({
  header: {
    position: 'sticky',
    top: 0,
    zIndex: 30,
    display: 'flex',
    flexWrap: 'wrap',
    alignItems: 'center',
    gap: '12px',
    minHeight: '48px',
    padding: '8px 12px',
    backgroundColor: tokens.colorNeutralBackground1,
    borderBottom: `1px solid ${tokens.colorNeutralStroke1}`,
  },
  left: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    minWidth: 0,
  },
  logoMark: {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: '28px',
    height: '28px',
    flexShrink: 0,
    borderRadius: tokens.borderRadiusSmall,
    background: 'linear-gradient(135deg, #0078D4, #50E6FF)',
    color: '#ffffff',
  },
  textBlock: { minWidth: 0 },
  eyebrow: {
    fontSize: '10px',
    letterSpacing: '0.14em',
    textTransform: 'uppercase',
    color: tokens.colorNeutralForeground2,
  },
  title: {
    fontSize: '14px',
    fontWeight: 600,
    color: tokens.colorNeutralForeground1,
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
  subtitle: {
    fontSize: '12px',
    marginTop: '2px',
    color: tokens.colorNeutralForeground2,
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
    maxWidth: '32rem',
  },
  right: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    flexWrap: 'wrap',
    marginLeft: 'auto',
  },
  signedInAs: {
    fontSize: '12.5px',
    color: tokens.colorNeutralForeground2,
    display: 'none',
    '@media (min-width: 640px)': { display: 'inline' },
  },
  chip: {
    display: 'none',
    '@media (min-width: 1024px)': { display: 'inline-flex' },
  },
})

// Function: AppHeader
export default function AppHeader({ title, subtitle, backTo, rightSlot }) {
  return (
    <>
      <FluentProvider theme={azureNavyDarkTheme}>
        <AppHeaderBar title={title} subtitle={subtitle} backTo={backTo} rightSlot={rightSlot} />
      </FluentProvider>
      <Breadcrumb />
    </>
  )
}

// Function: AppHeaderBar
function AppHeaderBar({ title, subtitle, backTo, rightSlot }) {
  const styles = useStyles()
  const { user } = useContext(AppContext)
  const navigate = useNavigate()

  return (
    <header className={styles.header}>
      {/* ── Left: icon + labels ── */}
      <div className={styles.left}>
        {backTo && (
          <Button
            appearance="subtle"
            size="small"
            icon={<ArrowLeftRegular />}
            aria-label="Back"
            onClick={() => navigate(backTo)}
          />
        )}
        <div className={styles.logoMark}>
          <ServerRegular fontSize={15} />
        </div>
        <div className={styles.textBlock}>
          <Text className={styles.eyebrow} block>Unified Modernization Suite</Text>
          <Text className={styles.title} block>{title}</Text>
          {subtitle && <Text className={styles.subtitle} block>{subtitle}</Text>}
        </div>
      </div>

      {/* ── Right: user info + nav buttons ── */}
      <div className={styles.right}>
        {user?.username && (
          <Text className={styles.signedInAs}>
            Signed in as <strong>{user.username}</strong>
          </Text>
        )}

        <Badge
          className={styles.chip}
          appearance="outline"
          color="informative"
          icon={<SearchRegular />}
        >
          Infra Scanner
        </Badge>

        {rightSlot}

        {backTo && backTo !== '/' && (
          <Button appearance="secondary" size="small" icon={<HomeRegular />} onClick={() => navigate('/')}>
            Dashboard
          </Button>
        )}

        <Button
          appearance="secondary"
          size="small"
          icon={<HomeRegular />}
          as="a"
          href={getPortalHomeUrl()}
        >
          Portal Home
        </Button>

        {user?.role === 'admin' && (
          <Button
            appearance="secondary"
            size="small"
            icon={<ShieldCheckmarkRegular />}
            as="a"
            href={(() => {
              try {
                return new URL('/admin', getPortalHomeUrl()).href
              } catch {
                return '/admin'
              }
            })()}
          >
            Admin Console
          </Button>
        )}

        <Button appearance="secondary" size="small" icon={<SignOutRegular />} onClick={logoutFromPortal}>
          Logout
        </Button>
      </div>
    </header>
  )
}
