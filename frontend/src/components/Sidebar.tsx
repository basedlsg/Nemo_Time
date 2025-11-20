import { useChatStore } from '@/stores/chatStore'
import { useLanguage } from '@/hooks/useLanguage'
import { MessageSquarePlus, Trash2, MessageSquare } from 'lucide-react'
import { LanguageToggle } from './LanguageToggle'
import { formatDate, truncate, cn } from '@/lib/utils'

export function Sidebar() {
  const {
    sessions,
    currentSessionId,
    createSession,
    setCurrentSession,
    deleteSession,
    clearAllSessions,
  } = useChatStore()
  const { t, lang } = useLanguage()

  const handleClearHistory = () => {
    if (window.confirm(t('clearHistoryConfirm'))) {
      clearAllSessions()
    }
  }

  return (
    <div className="w-64 h-screen bg-neutral-900 text-white flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-neutral-800">
        <h1 className="text-xl font-bold text-olive-400 mb-1">{t('appName')}</h1>
        <p className="text-xs text-neutral-400">{t('appSubtitle')}</p>
      </div>

      {/* New Chat Button */}
      <div className="p-3 border-b border-neutral-800">
        <button
          onClick={createSession}
          className="w-full flex items-center gap-2 px-3 py-2 bg-olive-600 hover:bg-olive-700 rounded-lg transition-colors"
        >
          <MessageSquarePlus className="w-5 h-5" />
          <span className="font-medium">{t('newChat')}</span>
        </button>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-3">
          <h3 className="text-xs font-semibold text-neutral-400 uppercase tracking-wide mb-2">
            {t('chatHistory')}
          </h3>
          {sessions.length === 0 ? (
            <div className="text-sm text-neutral-500 text-center py-8">
              {t('noChats')}
            </div>
          ) : (
            <div className="space-y-1">
              {sessions.map((session) => (
                <div
                  key={session.id}
                  className={cn(
                    'group relative flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-colors',
                    currentSessionId === session.id
                      ? 'bg-neutral-800 text-white'
                      : 'hover:bg-neutral-800 text-neutral-300'
                  )}
                  onClick={() => setCurrentSession(session.id)}
                >
                  <MessageSquare className="w-4 h-4 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="text-sm truncate">
                      {truncate(session.title, 30)}
                    </div>
                    <div className="text-xs text-neutral-500">
                      {formatDate(session.updatedAt, lang)}
                    </div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      deleteSession(session.id)
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-neutral-700 rounded transition-all"
                  >
                    <Trash2 className="w-4 h-4 text-red-400" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Bottom Section */}
      <div className="p-3 border-t border-neutral-800 space-y-3">
        {/* Language Toggle */}
        <LanguageToggle />

        {/* Clear History Button */}
        {sessions.length > 0 && (
          <button
            onClick={handleClearHistory}
            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-400 hover:bg-neutral-800 rounded-lg transition-colors"
          >
            <Trash2 className="w-4 h-4" />
            <span>{t('clearHistory')}</span>
          </button>
        )}
      </div>
    </div>
  )
}
