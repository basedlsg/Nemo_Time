import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { Language } from '@/types'
import { getTranslation } from '@/lib/i18n'

interface LanguageState {
  lang: Language
  setLang: (lang: Language) => void
  t: (key: string) => string
}

export const useLanguage = create<LanguageState>()(
  persist(
    (set, get) => ({
      lang: 'zh', // Default to Chinese
      setLang: (lang: Language) => set({ lang }),
      t: (key: string) => {
        const { lang } = get()
        return getTranslation(lang, key)
      },
    }),
    {
      name: 'nemo-language',
    }
  )
)
