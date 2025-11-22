import { Message } from '@/types'
import { useLanguage } from '@/hooks/useLanguage'
import { User, Bot, ExternalLink, AlertCircle } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { cn } from '@/lib/utils'

interface ChatMessageProps {
  message: Message
}

export function ChatMessage({ message }: ChatMessageProps) {
  const { t } = useLanguage()
  const isUser = message.role === 'user'

  return (
    <div
      className={cn(
        'py-8 px-4',
        isUser ? 'bg-white' : 'bg-neutral-50'
      )}
    >
      <div className="max-w-3xl mx-auto">
        <div className="flex gap-4">
          {/* Avatar */}
          <div
            className={cn(
              'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
              isUser ? 'bg-purple-500' : 'bg-teal-500'  // ChatGPT colors: purple for user, teal for AI
            )}
          >
            {isUser ? (
              <User className="w-5 h-5 text-white" />
            ) : (
              <Bot className="w-5 h-5 text-white" />
            )}
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="mb-2 font-semibold text-neutral-900">
              {isUser ? t('you') : t('assistant')}
            </div>

            {/* Loading state */}
            {message.loading && (
              <div className="typing-indicator py-2">
                <span style={{ '--delay': 0 } as any}></span>
                <span style={{ '--delay': 1 } as any}></span>
                <span style={{ '--delay': 2 } as any}></span>
              </div>
            )}

            {/* Error state */}
            {message.error && (
              <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                <div className="text-sm text-red-700">
                  {message.content || t('errorMessage')}
                </div>
              </div>
            )}

            {/* Normal content */}
            {!message.loading && !message.error && (
              <div className="message-content prose prose-neutral max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {message.content}
                </ReactMarkdown>
              </div>
            )}

            {/* Citations */}
            {message.citations && message.citations.length > 0 && (
              <div className="mt-6 pt-6 border-t border-neutral-200">
                <h4 className="text-sm font-semibold text-neutral-700 mb-3 flex items-center gap-2">
                  <ExternalLink className="w-4 h-4" />
                  {t('citations')}
                </h4>
                <div className="space-y-2">
                  {message.citations.map((citation, index) => (
                    <div
                      key={index}
                      className="p-3 bg-neutral-100 rounded-lg border border-neutral-200 hover:border-brand-500 transition-colors"
                    >
                      <div className="text-sm font-medium text-neutral-900 mb-1">
                        {citation.title}
                      </div>
                      {citation.effective_date && (
                        <div className="text-xs text-neutral-600 mb-2">
                          {t('effectiveDate')}: {citation.effective_date}
                        </div>
                      )}
                      <a
                        href={citation.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-brand-600 hover:text-brand-700 flex items-center gap-1"
                      >
                        {t('viewSource')}
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
