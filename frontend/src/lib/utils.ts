import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

export function formatDate(timestamp: number, lang: 'zh' | 'en'): string {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) {
    return lang === 'zh' ? '刚刚' : 'Just now'
  } else if (diffMins < 60) {
    return lang === 'zh' ? `${diffMins}分钟前` : `${diffMins}m ago`
  } else if (diffHours < 24) {
    return lang === 'zh' ? `${diffHours}小时前` : `${diffHours}h ago`
  } else if (diffDays < 7) {
    return lang === 'zh' ? `${diffDays}天前` : `${diffDays}d ago`
  } else {
    return date.toLocaleDateString(lang === 'zh' ? 'zh-CN' : 'en-US')
  }
}

export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}
