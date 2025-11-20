import { useEffect, useRef } from 'react'
import { useChatStore } from '@/stores/chatStore'
import { useLanguage } from '@/hooks/useLanguage'
import { ChatMessage } from './ChatMessage'
import { ContextSelectors } from './ContextSelectors'
import { Sparkles } from 'lucide-react'

export function ChatArea() {
  const { getCurrentSession } = useChatStore()
  const { t } = useLanguage()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const currentSession = getCurrentSession()

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [currentSession?.messages])

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden">
      {/* Context Selectors (Province & Asset) */}
      <ContextSelectors />

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        {!currentSession || currentSession.messages.length === 0 ? (
          // Empty state
          <div className="h-full flex items-center justify-center p-8">
            <div className="text-center max-w-2xl">
              <div className="inline-flex items-center justify-center w-16 h-16 mb-4 bg-olive-100 rounded-full">
                <Sparkles className="w-8 h-8 text-olive-600" />
              </div>
              <h2 className="text-2xl font-bold text-neutral-900 mb-2">
                {t('welcomeTitle')}
              </h2>
              <p className="text-neutral-600 leading-relaxed">
                {t('welcomeMessage')}
              </p>
            </div>
          </div>
        ) : (
          // Messages
          <div>
            {currentSession.messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>
    </div>
  )
}
