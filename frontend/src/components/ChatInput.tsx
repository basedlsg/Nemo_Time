import { useState, useRef, KeyboardEvent } from 'react'
import { useLanguage } from '@/hooks/useLanguage'
import { useChatStore } from '@/stores/chatStore'
import { Send, AlertCircle } from 'lucide-react'
import { sendQuery } from '@/lib/api'
import { cn } from '@/lib/utils'

export function ChatInput() {
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const { t, lang } = useLanguage()
  const { province, asset, docClass, addMessage, updateMessage, getCurrentSession } = useChatStore()

  const handleSubmit = async () => {
    const question = input.trim()

    if (!question) {
      return
    }

    if (!province) {
      alert(t('pleaseSelectProvince'))
      return
    }

    if (!asset) {
      alert(t('pleaseSelectAsset'))
      return
    }

    // Clear input
    setInput('')
    setIsLoading(true)

    // Add user message
    addMessage({
      role: 'user',
      content: question,
    })

    // Add loading assistant message
    addMessage({
      role: 'assistant',
      content: '',
      loading: true,
    })

    try {
      // Send query to API
      const response = await sendQuery({
        province,
        asset,
        doc_class: docClass,
        question,
        lang: lang === 'zh' ? 'zh' : 'en',
      })

      // Get the current messages to find the loading message
      const currentSession = getCurrentSession()
      const loadingMessage = currentSession?.messages.find((m) => m.loading)

      if (loadingMessage) {
        // Update the loading message with the response
        if (response.error) {
          updateMessage(loadingMessage.id, {
            content: response.message || t('errorMessage'),
            loading: false,
            error: true,
          })
        } else if (response.refusal) {
          const refusalContent = response.refusal + (response.tips ? '\n\n' + response.tips.join('\n') : '')
          updateMessage(loadingMessage.id, {
            content: refusalContent,
            loading: false,
            error: false,
          })
        } else {
          updateMessage(loadingMessage.id, {
            content: response.answer_zh || response.answer || '',
            citations: response.citations || [],
            loading: false,
            error: false,
          })
        }
      }
    } catch (error) {
      console.error('Error sending query:', error)
      const currentSession = getCurrentSession()
      const loadingMessage = currentSession?.messages.find((m) => m.loading)
      if (loadingMessage) {
        updateMessage(loadingMessage.id, {
          content: t('errorMessage'),
          loading: false,
          error: true,
        })
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  // Auto-resize textarea
  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value)
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px'
    }
  }

  const canSend = input.trim() && province && asset && !isLoading

  return (
    <div className="border-t border-neutral-200 bg-white p-4">
      <div className="max-w-3xl mx-auto">
        {/* Validation warnings */}
        {input.trim() && (!province || !asset) && (
          <div className="mb-3 p-2 bg-amber-50 border border-amber-200 rounded-lg flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0" />
            <span className="text-sm text-amber-700">
              {!province ? t('pleaseSelectProvince') : t('pleaseSelectAsset')}
            </span>
          </div>
        )}

        {/* Input area */}
        <div className="flex gap-3 items-end">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={handleInput}
              onKeyDown={handleKeyDown}
              placeholder={t('inputPlaceholder')}
              rows={1}
              className="w-full px-4 py-3 pr-12 border border-neutral-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-olive-500 focus:border-transparent resize-none max-h-40 transition-all"
              disabled={isLoading}
            />
          </div>
          <button
            onClick={handleSubmit}
            disabled={!canSend}
            className={cn(
              'px-4 py-3 rounded-xl transition-all flex items-center gap-2',
              canSend
                ? 'bg-olive-500 hover:bg-olive-600 text-white shadow-md hover:shadow-lg'
                : 'bg-neutral-200 text-neutral-400 cursor-not-allowed'
            )}
          >
            <Send className="w-5 h-5" />
          </button>
        </div>

        {/* Tips */}
        <div className="mt-2 text-xs text-neutral-500 text-center">
          {isLoading ? t('sending') : 'Enter to send, Shift+Enter for new line'}
        </div>
      </div>
    </div>
  )
}
