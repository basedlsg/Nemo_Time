import { useLanguage } from '@/hooks/useLanguage'
import { Globe } from 'lucide-react'
import { cn } from '@/lib/utils'

export function LanguageToggle() {
  const { lang, setLang, t } = useLanguage()

  return (
    <div className="flex items-center gap-2 px-3 py-2 bg-white border border-neutral-200 rounded-lg">
      <Globe className="w-4 h-4 text-neutral-500" />
      <button
        onClick={() => setLang('zh')}
        className={cn(
          'px-2 py-1 text-sm rounded transition-colors',
          lang === 'zh'
            ? 'bg-olive-500 text-white'
            : 'text-neutral-600 hover:bg-neutral-100'
        )}
      >
        {t('chinese')}
      </button>
      <button
        onClick={() => setLang('en')}
        className={cn(
          'px-2 py-1 text-sm rounded transition-colors',
          lang === 'en'
            ? 'bg-olive-500 text-white'
            : 'text-neutral-600 hover:bg-neutral-100'
        )}
      >
        {t('english')}
      </button>
    </div>
  )
}
