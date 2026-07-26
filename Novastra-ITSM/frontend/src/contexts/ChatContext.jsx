// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Novastra-ITSM — frontend/src/contexts (ChatContext.jsx)
// Date: 2025-08-20
// ---------------------------------------------------------------------------
import { createContext, useContext, useState, useCallback, useEffect } from 'react'
import {
  getSettings,
  updateSettings,
  historyListSessions,
  historyCreateSession,
  historyUpdateSession,
  historyDeleteSession,
} from '../services/api.js'
import { useAuth } from './AuthContext.jsx'

const STORAGE_KEY = 'novastra_itsm_chat_sessions'

const ChatContext = createContext(null)

// Function: ChatProvider
export function ChatProvider({ children }) {
  const { user, isAuthenticated } = useAuth()
  const userStorageKey = `${STORAGE_KEY}_${user?.id || 'anon'}`

  const [sessions, setSessions] = useState(() => {
    try { return JSON.parse(localStorage.getItem(`${STORAGE_KEY}_anon`) || '[]') }
    catch { return [] }
  })
  const [activeSessionId, setActiveSessionId] = useState(null)
  const [selectedModel, setSelectedModel] = useState('ollama')
  const [serverSettings, setServerSettings] = useState(null)

  // Load server settings on mount
  useEffect(() => {
    getSettings()
      .then(({ data }) => {
        setServerSettings(data)
        setSelectedModel(data.llm_provider)
      })
      .catch(() => {})
  }, [])

  // Load server-side chat sessions per logged-in user (5-day retention enforced by backend).
  useEffect(() => {
    let cancelled = false

    // Function: loadSessions
    const loadSessions = async () => {
      if (!isAuthenticated || !user?.id) {
        setSessions([])
        setActiveSessionId(null)
        return
      }

      try {
        const { data } = await historyListSessions(200)
        if (!cancelled) {
          const next = data?.sessions || []
          setSessions(next)
          setActiveSessionId((prev) => (prev && next.some((s) => s.id === prev) ? prev : null))
        }
      } catch {
        // Fallback to local cache if server history is temporarily unavailable.
        try {
          if (!cancelled) {
            setSessions(JSON.parse(localStorage.getItem(userStorageKey) || '[]'))
          }
        } catch {
          if (!cancelled) setSessions([])
        }
      }
    }

    loadSessions()
    return () => { cancelled = true }
  }, [isAuthenticated, user?.id, userStorageKey])

  // Keep local cache per user for resilience.
  useEffect(() => {
    try { localStorage.setItem(userStorageKey, JSON.stringify(sessions)) }
    catch {}
  }, [sessions, userStorageKey])

  const changeModel = useCallback(async (provider) => {
    setSelectedModel(provider)
    try {
      const { data } = await updateSettings({ llm_provider: provider })
      setServerSettings(data)
    } catch {}
  }, [])

  const startNewChat = useCallback(() => {
    setActiveSessionId(null)
  }, [])

  const createSession = useCallback(async (title, provider, chatType = 'general') => {
    if (!isAuthenticated) {
      const id = `session_${Date.now()}`
      const newSession = {
        id,
        title: title.slice(0, 120),
        messages: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        provider,
        chat_type: chatType,
      }
      setSessions((prev) => [newSession, ...prev])
      setActiveSessionId(id)
      return id
    }

    try {
      const { data } = await historyCreateSession({
        title: title.slice(0, 120),
        provider,
        chat_type: chatType,
      })
      const session = {
        ...data,
        messages: data?.messages || [],
      }
      setSessions((prev) => [session, ...prev.filter((s) => s.id !== session.id)])
      setActiveSessionId(session.id)
      return session.id
    } catch {
      const id = `session_${Date.now()}`
      const fallbackSession = {
        id,
        title: title.slice(0, 120),
        messages: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        provider,
        chat_type: chatType,
      }
      setSessions((prev) => [fallbackSession, ...prev])
      setActiveSessionId(id)
      return id
    }
  }, [isAuthenticated])

  const updateSessionMessages = useCallback(async (id, messages, title) => {
    setSessions((prev) => prev.map((s) => (s.id === id ? { ...s, messages, updatedAt: new Date().toISOString() } : s)))

    if (!isAuthenticated) return

    try {
      const safeTitle = typeof title === 'string' ? title.slice(0, 120) : undefined
      const { data } = await historyUpdateSession(id, {
        title: safeTitle,
        messages: (messages || []).map((m) => ({
          role: m.role,
          content: m.content,
          sources: m.sources || [],
          confidence: m.confidence,
          context_used: m.context_used,
        })),
      })
      setSessions((prev) => prev.map((s) => (s.id === id ? { ...s, ...data, messages: data?.messages || [] } : s)))
    } catch {
      // Keep local state; next refresh will retry syncing.
    }
  }, [isAuthenticated])

  const deleteSession = useCallback(async (id) => {
    setSessions((prev) => prev.filter((s) => s.id !== id))
    setActiveSessionId((prev) => (prev === id ? null : prev))

    if (!isAuthenticated) return
    try {
      await historyDeleteSession(id)
    } catch {
      // If server delete fails, keep UI responsive; server copy will be cleaned by TTL.
    }
  }, [isAuthenticated])

  return (
    <ChatContext.Provider
      value={{
        sessions,
        activeSessionId,
        setActiveSessionId,
        selectedModel,
        serverSettings,
        changeModel,
        startNewChat,
        createSession,
        updateSessionMessages,
        deleteSession,
      }}
    >
      {children}
    </ChatContext.Provider>
  )
}

// Function: useChatContext
export function useChatContext() {
  return useContext(ChatContext)
}
