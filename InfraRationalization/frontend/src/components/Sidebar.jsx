// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: InfraRationalization — frontend/src/components (Sidebar.jsx)
// Date: 2026-08-04
// ---------------------------------------------------------------------------
import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import {
  Button,
  Tooltip,
  Divider,
  makeStyles,
  tokens,
  mergeClasses,
} from '@fluentui/react-components'
import { ChevronLeftRegular, ChevronRightRegular } from '@fluentui/react-icons'
import { ROUTES } from '../navigation/routeMeta.js'
import { sidebarActiveStyles } from '../theme/azurePortalTheme.js'

const STORAGE_KEY = 'infra-sidebar-collapsed'
const EXPANDED_WIDTH = '240px'
const COLLAPSED_WIDTH = '52px'

const useStyles = makeStyles({
  root: {
    display: 'flex',
    flexDirection: 'column',
    flexShrink: 0,
    height: '100%',
    backgroundColor: tokens.colorNeutralBackground2,
    borderRight: `1px solid ${tokens.colorNeutralStroke1}`,
    transition: 'width 150ms ease',
    overflow: 'hidden',
  },
  nav: {
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
    padding: '8px',
    flex: 1,
  },
  item: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    height: '36px',
    padding: '0 10px',
    borderRadius: tokens.borderRadiusMedium,
    color: tokens.colorNeutralForeground2,
    borderLeft: '2px solid transparent',
    justifyContent: 'flex-start',
    minWidth: 0,
    ':hover': {
      backgroundColor: tokens.colorNeutralBackground2Hover,
      color: tokens.colorNeutralForeground1,
    },
  },
  itemActive: {
    backgroundColor: sidebarActiveStyles.background,
    borderLeftColor: sidebarActiveStyles.accentBar,
    color: tokens.colorNeutralForeground1,
  },
  itemLabel: {
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
    fontSize: '13px',
  },
  toggleRow: {
    display: 'flex',
    justifyContent: 'flex-end',
    padding: '6px',
  },
})

// Function: Sidebar
export default function Sidebar() {
  const styles = useStyles()
  const location = useLocation()
  const navigate = useNavigate()
  const [collapsed, setCollapsed] = useState(() => {
    try {
      return localStorage.getItem(STORAGE_KEY) === '1'
    } catch {
      return false
    }
  })

  // Function: toggleCollapsed
  const toggleCollapsed = () => {
    setCollapsed((prev) => {
      const next = !prev
      try {
        localStorage.setItem(STORAGE_KEY, next ? '1' : '0')
      } catch {
        // best-effort persistence only
      }
      return next
    })
  }

  const items = ROUTES.filter((r) => r.sidebar)

  return (
    <aside
      className={styles.root}
      style={{ width: collapsed ? COLLAPSED_WIDTH : EXPANDED_WIDTH }}
    >
      <nav className={styles.nav}>
        {items.map(({ path, icon: Icon, label }) => {
          const active = location.pathname === path
          const button = (
            <Button
              key={path}
              appearance="transparent"
              className={mergeClasses(styles.item, active && styles.itemActive)}
              icon={<Icon fontSize={18} />}
              onClick={() => navigate(path)}
            >
              {!collapsed && <span className={styles.itemLabel}>{label}</span>}
            </Button>
          )
          return collapsed ? (
            <Tooltip key={path} content={label} relationship="label" positioning="after">
              {button}
            </Tooltip>
          ) : (
            button
          )
        })}
      </nav>
      <Divider />
      <div className={styles.toggleRow}>
        <Tooltip content={collapsed ? 'Expand' : 'Collapse'} relationship="label" positioning="after">
          <Button
            appearance="transparent"
            icon={collapsed ? <ChevronRightRegular /> : <ChevronLeftRegular />}
            onClick={toggleCollapsed}
          />
        </Tooltip>
      </div>
    </aside>
  )
}
