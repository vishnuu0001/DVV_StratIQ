// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: InfraRationalization — frontend/src/components (Breadcrumb.jsx)
// Date: 2026-08-04
// ---------------------------------------------------------------------------
import { useLocation, useNavigate } from 'react-router-dom'
import {
  Breadcrumb as FluentBreadcrumb,
  BreadcrumbItem,
  BreadcrumbButton,
  BreadcrumbDivider,
  makeStyles,
  tokens,
} from '@fluentui/react-components'
import { matchRoute } from '../navigation/routeMeta.js'

const useStyles = makeStyles({
  bar: {
    display: 'flex',
    alignItems: 'center',
    minHeight: '36px',
    padding: '0 16px',
    backgroundColor: '#FAFAFA',
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
  },
})

// Function: Breadcrumb
// Renders "Dashboard > <current page>" for any route other than "/". Param
// routes (":scanId") resolve to their static label via matchRoute.
export default function Breadcrumb() {
  const styles = useStyles()
  const location = useLocation()
  const navigate = useNavigate()
  const current = matchRoute(location.pathname)

  if (!current || current.path === '/') {
    return (
      <div className={styles.bar}>
        <FluentBreadcrumb aria-label="Breadcrumb">
          <BreadcrumbItem>
            <BreadcrumbButton current>Dashboard</BreadcrumbButton>
          </BreadcrumbItem>
        </FluentBreadcrumb>
      </div>
    )
  }

  return (
    <div className={styles.bar}>
      <FluentBreadcrumb aria-label="Breadcrumb">
        <BreadcrumbItem>
          <BreadcrumbButton onClick={() => navigate('/')}>Dashboard</BreadcrumbButton>
        </BreadcrumbItem>
        <BreadcrumbDivider />
        <BreadcrumbItem>
          <BreadcrumbButton current>{current.label}</BreadcrumbButton>
        </BreadcrumbItem>
      </FluentBreadcrumb>
    </div>
  )
}
