// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: TraceForge — ui/src/components (GroupedNavigation.tsx)
// Date: 2026-03-01
// ---------------------------------------------------------------------------
import { useEffect, useState } from 'react'
import { ChevronDown, ChevronRight } from 'lucide-react'
import { NavLink, useLocation } from 'react-router-dom'

export interface NavigationItem {
  to: string
  label: string
  end?: boolean
}

export interface NavigationGroup {
  label: string
  items: NavigationItem[]
}

interface Props {
  overview: NavigationItem
  groups: NavigationGroup[]
}

// Function: GroupedNavigation
export default function GroupedNavigation({ overview, groups }: Props) {
  const location = useLocation()
  const activeGroup = groups.find((group) =>
    group.items.some((item) =>
      item.end ? location.pathname === item.to : location.pathname.startsWith(item.to),
    ),
  )?.label
  const [openGroups, setOpenGroups] = useState<Set<string>>(
    () => new Set(activeGroup ? [activeGroup] : ['Discovery']),
  )

  useEffect(() => {
    if (!activeGroup) return
    setOpenGroups((current) => new Set([...current, activeGroup]))
  }, [activeGroup])

  // Function: itemClass
  const itemClass = () => 'az-navd-item'

  return (
    <nav className="flex-1 overflow-y-auto py-2" aria-label="TraceForge workspace">
      <NavLink to={overview.to} end className="az-navd-overview">
        {overview.label}
      </NavLink>
      <div className="my-1" style={{ borderTop: '1px solid #edebe9' }} />
      {groups.map((group) => {
        const expanded = openGroups.has(group.label)
        return (
          <section key={group.label}>
            <button
              type="button"
              aria-expanded={expanded}
              onClick={() => setOpenGroups((current) => {
                const next = new Set(current)
                if (next.has(group.label)) next.delete(group.label)
                else next.add(group.label)
                return next
              })}
              className="az-navd-group-btn"
            >
              {group.label}
              {expanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
            </button>
            {expanded && (
              <div className="mb-1">
                {group.items.map((item) => (
                  <NavLink key={item.to} to={item.to} end={item.end} className={itemClass}>
                    {item.label}
                  </NavLink>
                ))}
              </div>
            )}
          </section>
        )
      })}
    </nav>
  )
}
