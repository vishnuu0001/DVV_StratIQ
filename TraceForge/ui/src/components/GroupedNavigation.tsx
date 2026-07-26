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
  const itemClass = ({ isActive }: { isActive: boolean }) =>
    `block border-r-2 px-4 py-1.5 text-xs transition-colors ${
      isActive
        ? 'border-blue-500 bg-blue-600/15 text-blue-300'
        : 'border-transparent text-gray-400 hover:bg-white/5 hover:text-white'
    }`

  return (
    <nav className="flex-1 overflow-y-auto py-2" aria-label="TraceForge workspace">
      <NavLink to={overview.to} end className={itemClass}>
        {overview.label}
      </NavLink>
      <div className="my-2 border-t border-white/5" />
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
              className="flex w-full items-center justify-between px-4 py-2 text-left text-[10px] font-semibold uppercase tracking-[0.12em] text-gray-500 hover:text-gray-300"
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
