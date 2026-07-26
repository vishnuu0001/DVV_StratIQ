// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/context (TicketContext.jsx)
// Date: 2026-01-07
// ---------------------------------------------------------------------------
import React, { createContext, useCallback, useContext, useRef, useState } from 'react'
import api from '../services/api.js'

const TicketContext = createContext({
  activeTicket: null,
  setActiveTicket: () => {},
  tickets: [],
  ticketsLoading: false,
  ticketsTotal: 0,
  loadTickets: async () => {},
  searchTickets: async () => {},
})

// Function: TicketProvider
export function TicketProvider({ children }) {
  const [activeTicket, setActiveTicket] = useState(null)
  const [tickets, setTickets] = useState([])
  const [ticketsLoading, setTicketsLoading] = useState(false)
  const [ticketsTotal, setTicketsTotal] = useState(0)
  const [loaded, setLoaded] = useState(false)
  const requestSequence = useRef(0)

  // Function: searchTickets
  const searchTickets = useCallback(async (query = '', offset = 0, append = false) => {
    const requestId = ++requestSequence.current
    setTicketsLoading(true)
    try {
      const { data } = await api.get('/tickets/search', {
        params: { q: query, limit: 100, offset },
      })
      if (requestId !== requestSequence.current) return data

      const rows = data.tickets || []
      setTickets(previous => {
        if (!append) return rows
        const byNumber = new Map(previous.map(ticket => [ticket.number, ticket]))
        rows.forEach(ticket => byNumber.set(ticket.number, ticket))
        return Array.from(byNumber.values())
      })
      setTicketsTotal(Number(data.total || 0))
      if (!query && offset === 0) setLoaded(true)
      return data
    } catch (error) {
      if (requestId === requestSequence.current) {
        setTicketsTotal(0)
        if (!append) setTickets([])
      }
      throw error
    } finally {
      if (requestId === requestSequence.current) setTicketsLoading(false)
    }
  }, [])

  // Function: loadTickets
  const loadTickets = useCallback(async () => {
    if (loaded || ticketsLoading) return
    try {
      await searchTickets('', 0, false)
    } catch {
      // The picker is an enhancement and must not block the surrounding AI tool.
    }
  }, [loaded, ticketsLoading, searchTickets])

  return (
    <TicketContext.Provider value={{
      activeTicket, setActiveTicket, tickets, ticketsLoading, ticketsTotal,
      loadTickets, searchTickets,
    }}>
      {children}
    </TicketContext.Provider>
  )
}

// Function: useTicket
export function useTicket() {
  return useContext(TicketContext)
}
