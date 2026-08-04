// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: InfraRationalization — frontend/src/components (ChromeShell.jsx)
// Date: 2026-08-04
// ---------------------------------------------------------------------------
import { FluentProvider, makeStyles } from '@fluentui/react-components'
import { azureNavyDarkTheme } from '../theme/azurePortalTheme.js'
import Sidebar from './Sidebar.jsx'

const useStyles = makeStyles({
  root: {
    display: 'flex',
    flexShrink: 0,
  },
})

/**
 * Owns the nested navy FluentProvider that scopes the dark Azure-Portal-style
 * left nav Sidebar (the top AppHeader renders its own instance of this same
 * theme per-page since it's called directly by each page component, not by
 * ChromeShell).
 *
 * Rendered once in App.jsx as a flex sibling of the routed content, outside
 * <Routes>, so the sidebar persists across route changes instead of
 * remounting on every navigation.
 */
// Function: ChromeShell
export default function ChromeShell() {
  const styles = useStyles()
  return (
    <FluentProvider theme={azureNavyDarkTheme} className={styles.root}>
      <Sidebar />
    </FluentProvider>
  )
}
