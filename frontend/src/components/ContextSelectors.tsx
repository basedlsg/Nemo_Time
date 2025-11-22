import { useChatStore } from '@/stores/chatStore'
import { useLanguage } from '@/hooks/useLanguage'
import { MapPin, Zap } from 'lucide-react'
import { Province, Asset } from '@/types'
import { cn } from '@/lib/utils'

const PROVINCES: Province[] = ['gd', 'sd', 'nm']
const ASSETS: Asset[] = ['solar', 'coal', 'wind']

export function ContextSelectors() {
  const { province, asset, setProvince, setAsset } = useChatStore()
  const { t } = useLanguage()

  return (
    <div className="flex flex-col gap-4 p-4 bg-white border-b border-neutral-200">
      {/* Province Selector */}
      <div>
        <label className="flex items-center gap-2 mb-2 text-sm font-medium text-neutral-700">
          <MapPin className="w-4 h-4" />
          {t('selectProvince')}
        </label>
        <select
          value={province}
          onChange={(e) => setProvince(e.target.value as Province)}
          className="w-full px-3 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition-all"
        >
          <option value="">{t('selectProvince')}...</option>
          {PROVINCES.map((p) => (
            <option key={p} value={p}>
              {t(`provinces.${p}`)}
            </option>
          ))}
        </select>
      </div>

      {/* Asset Selector */}
      <div>
        <label className="flex items-center gap-2 mb-2 text-sm font-medium text-neutral-700">
          <Zap className="w-4 h-4" />
          {t('selectAsset')}
        </label>
        <div className="grid grid-cols-3 gap-2">
          {ASSETS.map((a) => (
            <button
              key={a}
              onClick={() => setAsset(a)}
              className={cn(
                'px-3 py-2 text-sm font-medium rounded-lg transition-all',
                asset === a
                  ? 'bg-brand-500 text-white shadow-md'
                  : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200'
              )}
            >
              {t(`assets.${a}`)}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
