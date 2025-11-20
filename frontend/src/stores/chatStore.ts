import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { ChatSession, Message, Province, Asset, DocClass } from '@/types'
import { generateId } from '@/lib/utils'

interface ChatState {
  sessions: ChatSession[]
  currentSessionId: string | null
  province: Province
  asset: Asset
  docClass: DocClass

  // Session management
  createSession: () => void
  deleteSession: (id: string) => void
  setCurrentSession: (id: string) => void
  getCurrentSession: () => ChatSession | null
  clearAllSessions: () => void

  // Message management
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void
  updateMessage: (id: string, updates: Partial<Message>) => void
  deleteMessage: (id: string) => void

  // Context management
  setProvince: (province: Province) => void
  setAsset: (asset: Asset) => void
  setDocClass: (docClass: DocClass) => void

  // Update session title
  updateSessionTitle: (id: string, title: string) => void
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      sessions: [],
      currentSessionId: null,
      province: '',
      asset: '',
      docClass: 'grid',

      createSession: () => {
        const newSession: ChatSession = {
          id: generateId(),
          title: 'New Chat',
          messages: [],
          province: get().province,
          asset: get().asset,
          docClass: get().docClass,
          createdAt: Date.now(),
          updatedAt: Date.now(),
        }
        set((state) => ({
          sessions: [newSession, ...state.sessions],
          currentSessionId: newSession.id,
        }))
      },

      deleteSession: (id: string) => {
        set((state) => ({
          sessions: state.sessions.filter((s) => s.id !== id),
          currentSessionId: state.currentSessionId === id ? null : state.currentSessionId,
        }))
      },

      setCurrentSession: (id: string) => {
        const session = get().sessions.find((s) => s.id === id)
        if (session) {
          set({
            currentSessionId: id,
            province: session.province,
            asset: session.asset,
            docClass: session.docClass,
          })
        }
      },

      getCurrentSession: () => {
        const { sessions, currentSessionId } = get()
        return sessions.find((s) => s.id === currentSessionId) || null
      },

      clearAllSessions: () => {
        set({
          sessions: [],
          currentSessionId: null,
        })
      },

      addMessage: (message) => {
        const currentSession = get().getCurrentSession()
        if (!currentSession) {
          get().createSession()
        }

        const newMessage: Message = {
          ...message,
          id: generateId(),
          timestamp: Date.now(),
        }

        set((state) => ({
          sessions: state.sessions.map((session) =>
            session.id === state.currentSessionId
              ? {
                  ...session,
                  messages: [...session.messages, newMessage],
                  updatedAt: Date.now(),
                }
              : session
          ),
        }))

        // Auto-generate title from first user message
        const session = get().getCurrentSession()
        if (session && session.messages.length === 1 && message.role === 'user') {
          const title = message.content.slice(0, 50)
          get().updateSessionTitle(session.id, title)
        }
      },

      updateMessage: (id, updates) => {
        set((state) => ({
          sessions: state.sessions.map((session) =>
            session.id === state.currentSessionId
              ? {
                  ...session,
                  messages: session.messages.map((msg) =>
                    msg.id === id ? { ...msg, ...updates } : msg
                  ),
                  updatedAt: Date.now(),
                }
              : session
          ),
        }))
      },

      deleteMessage: (id) => {
        set((state) => ({
          sessions: state.sessions.map((session) =>
            session.id === state.currentSessionId
              ? {
                  ...session,
                  messages: session.messages.filter((msg) => msg.id !== id),
                  updatedAt: Date.now(),
                }
              : session
          ),
        }))
      },

      setProvince: (province) => {
        set({ province })
        const currentSession = get().getCurrentSession()
        if (currentSession) {
          set((state) => ({
            sessions: state.sessions.map((session) =>
              session.id === state.currentSessionId
                ? { ...session, province, updatedAt: Date.now() }
                : session
            ),
          }))
        }
      },

      setAsset: (asset) => {
        set({ asset })
        const currentSession = get().getCurrentSession()
        if (currentSession) {
          set((state) => ({
            sessions: state.sessions.map((session) =>
              session.id === state.currentSessionId
                ? { ...session, asset, updatedAt: Date.now() }
                : session
            ),
          }))
        }
      },

      setDocClass: (docClass) => {
        set({ docClass })
        const currentSession = get().getCurrentSession()
        if (currentSession) {
          set((state) => ({
            sessions: state.sessions.map((session) =>
              session.id === state.currentSessionId
                ? { ...session, docClass, updatedAt: Date.now() }
                : session
            ),
          }))
        }
      },

      updateSessionTitle: (id, title) => {
        set((state) => ({
          sessions: state.sessions.map((session) =>
            session.id === id ? { ...session, title } : session
          ),
        }))
      },
    }),
    {
      name: 'nemo-chat-store',
    }
  )
)
