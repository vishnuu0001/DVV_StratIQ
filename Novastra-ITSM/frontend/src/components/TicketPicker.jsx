// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/components (TicketPicker.jsx)
// Date: 2026-07-13
// ---------------------------------------------------------------------------
import React, { useEffect, useRef, useState } from 'react'
import { Ticket, X, ChevronDown, ChevronUp, Search, Loader2 } from 'lucide-react'
import { useTicket } from '../context/TicketContext.jsx'

const PRIORITY_CHIP = {
  '1 - Critical': 'text-red-300 bg-red-500/20 border-red-500/30',
  '2 - High': 'text-orange-300 bg-orange-500/20 border-orange-500/30',
  '3 - Medium': 'text-yellow-300 bg-yellow-500/20 border-yellow-500/30',
  '4 - Low': 'text-gray-300 bg-gray-500/20 border-gray-500/30',
  '1': 'text-red-300 bg-red-500/20 border-red-500/30',
  '2': 'text-orange-300 bg-orange-500/20 border-orange-500/30',
  '3': 'text-yellow-300 bg-yellow-500/20 border-yellow-500/30',
  '4': 'text-gray-300 bg-gray-500/20 border-gray-500/30',
}
const STATE_DOT = {
  Open: 'bg-blue-400',
  'In Progress': 'bg-yellow-400',
  Resolved: 'bg-green-400',
  Closed: 'bg-gray-500',
}

// Function: priorityLabel
function priorityLabel(priority) {
  const labels = { '1': 'Critical', '2': 'High', '3': 'Medium', '4': 'Low' }
  return priority?.split(' - ')[1] || labels[priority] || priority || '—'
}

// Function: TicketPicker
export default function TicketPicker() {
  const {
    activeTicket, setActiveTicket, tickets, ticketsLoading, ticketsTotal,
    searchTickets,
  } = useTicket()
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const inputRef = useRef(null)
  const containerRef = useRef(null)

  // Function: handleToggle
  const handleToggle = () => {
    setOpen(value => !value)
  }

  useEffect(() => {
    if (open) setTimeout(() => inputRef.current?.focus(), 60)
  }, [open])

  // Search the complete server-side operational store. Debouncing avoids one
  // database request per keystroke while still making every matching ticket reachable.
  useEffect(() => {
    if (!open) return undefined
    const timer = setTimeout(() => {
      searchTickets(query.trim(), 0, false).catch(() => {})
    }, query ? 250 : 0)
    return () => clearTimeout(timer)
  }, [open, query, searchTickets])

  useEffect(() => {
    // Function: onDown
    const onDown = event => {
      if (open && containerRef.current && !containerRef.current.contains(event.target)) setOpen(false)
    }
    document.addEventListener('mousedown', onDown)
    return () => document.removeEventListener('mousedown', onDown)
  }, [open])

  // Function: select
  const select = ticket => {
    setActiveTicket(ticket)
    setOpen(false)
    setQuery('')
  }

  // Function: clear
  const clear = event => {
    event.stopPropagation()
    setActiveTicket(null)
  }

  return (
    <div ref={containerRef} className="relative mb-4">
      <button
        onClick={handleToggle}
        className={`w-full flex items-center gap-2 px-3 py-2.5 rounded-xl border text-sm transition-all ${
          activeTicket
            ? 'bg-blue-500/10 border-blue-500/40 hover:border-blue-400/60'
            : 'bg-gray-900 border-white/10 hover:border-white/20'
        }`}
      >
        <Ticket size={14} className={activeTicket ? 'text-blue-400 shrink-0' : 'text-gray-500 shrink-0'} />

        {activeTicket ? (
          <span className="flex items-center gap-2 flex-1 min-w-0 text-left">
            <span className="font-mono text-xs font-bold text-blue-300 shrink-0">{activeTicket.number}</span>
            <span className="text-xs text-gray-200 truncate">{activeTicket.short_description}</span>
            <span className={`shrink-0 px-1.5 py-0.5 rounded border text-[10px] font-medium ${PRIORITY_CHIP[activeTicket.priority] || PRIORITY_CHIP['4']}`}>
              {priorityLabel(activeTicket.priority)}
            </span>
            <span className="shrink-0 text-[10px] text-gray-500 hidden sm:block">{activeTicket.category}</span>
          </span>
        ) : (
          <span className="flex-1 text-left text-xs text-gray-400">
            Load ticket to auto-fill fields across all AI tools
          </span>
        )}

        <span className="flex items-center gap-1 shrink-0 ml-1">
          {activeTicket && (
            <span onClick={clear} className="p-0.5 rounded text-gray-500 hover:text-red-400 hover:bg-red-500/10 transition-colors" title="Clear ticket">
              <X size={12} />
            </span>
          )}
          {open ? <ChevronUp size={12} className="text-gray-500" /> : <ChevronDown size={12} className="text-gray-500" />}
        </span>
      </button>

      {open && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-gray-900 border border-white/15 rounded-xl shadow-2xl z-50 overflow-hidden">
          <div className="flex items-center gap-2 px-3 py-2.5 border-b border-white/10">
            <Search size={13} className="text-gray-500 shrink-0" />
            <input
              ref={inputRef}
              value={query}
              onChange={event => setQuery(event.target.value)}
              placeholder="Search all tickets by number, keyword, category, or assignee…"
              className="flex-1 bg-transparent text-sm text-white placeholder-gray-500 outline-none"
            />
            {ticketsLoading && <Loader2 size={13} className="text-blue-400 animate-spin shrink-0" />}
          </div>

          <div className="max-h-72 overflow-y-auto">
            {!ticketsLoading && tickets.length === 0 && (
              <p className="px-4 py-4 text-xs text-gray-500 text-center">No tickets found</p>
            )}
            {tickets.map(ticket => (
              <button
                key={ticket.number}
                onClick={() => select(ticket)}
                className={`w-full text-left px-3 py-2.5 hover:bg-white/5 transition-colors border-b border-white/5 last:border-0 ${
                  activeTicket?.number === ticket.number ? 'bg-blue-500/10' : ''
                }`}
              >
                <div className="flex items-center gap-2 min-w-0">
                  <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${STATE_DOT[ticket.state] || 'bg-gray-500'}`} title={ticket.state} />
                  <span className="font-mono text-xs font-bold text-blue-300 shrink-0 w-24">{ticket.number}</span>
                  <span className="text-xs text-white flex-1 truncate">{ticket.short_description}</span>
                  <span className={`shrink-0 px-1.5 py-0.5 rounded border text-[10px] font-medium ${PRIORITY_CHIP[ticket.priority] || PRIORITY_CHIP['4']}`}>
                    {priorityLabel(ticket.priority)}
                  </span>
                </div>
                <div className="flex items-center gap-3 mt-0.5 pl-[calc(6px+96px+8px)]">
                  <span className="text-[10px] text-gray-500">{ticket.category} · {ticket.state}</span>
                  {ticket.assignment_group && <span className="text-[10px] text-gray-600">{ticket.assignment_group}</span>}
                </div>
              </button>
            ))}
            {!ticketsLoading && tickets.length < ticketsTotal && (
              <button
                onClick={() => searchTickets(query.trim(), tickets.length, true).catch(() => {})}
                className="w-full px-4 py-3 text-xs font-semibold text-blue-300 hover:bg-blue-500/10 border-t border-white/10 transition-colors"
              >
                Load more ({tickets.length.toLocaleString()} of {ticketsTotal.toLocaleString()})
              </button>
            )}
          </div>
          <div className="flex items-center justify-between px-3 py-1.5 border-t border-white/10 bg-gray-950/60 text-[10px] text-gray-500">
            <span>{tickets.length.toLocaleString()} loaded</span>
            <span>{ticketsTotal.toLocaleString()} matching tickets</span>
          </div>
        </div>
      )}
    </div>
  )
}
