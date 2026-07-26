// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: SSDLC_Process_Assessment — frontend/src/context (WorkbookContext.tsx)
// Date: 2025-10-22
// ---------------------------------------------------------------------------
import React, { createContext, useContext, useState, useCallback } from 'react'

interface WorkbookContextValue {
  workbookId: string | null
  setWorkbookId: (id: string) => void
  clearWorkbook: () => void
}

const WorkbookContext = createContext<WorkbookContextValue | null>(null)

const SESSION_KEY = 'csm_workbook_id'

// Function: WorkbookProvider
export function WorkbookProvider({ children }: { children: React.ReactNode }) {
  const [workbookId, setWorkbookIdState] = useState<string | null>(() => {
    return sessionStorage.getItem(SESSION_KEY)
  })

  const setWorkbookId = useCallback((id: string) => {
    sessionStorage.setItem(SESSION_KEY, id)
    setWorkbookIdState(id)
  }, [])

  const clearWorkbook = useCallback(() => {
    sessionStorage.removeItem(SESSION_KEY)
    setWorkbookIdState(null)
  }, [])

  return (
    <WorkbookContext.Provider value={{ workbookId, setWorkbookId, clearWorkbook }}>
      {children}
    </WorkbookContext.Provider>
  )
}

// Function: useWorkbook
export function useWorkbook(): WorkbookContextValue {
  const ctx = useContext(WorkbookContext)
  if (!ctx) throw new Error('useWorkbook must be used inside WorkbookProvider')
  return ctx
}
