export type Language = 'zh' | 'en'

export type Province = 'gd' | 'sd' | 'nm' | ''

export type Asset = 'solar' | 'coal' | 'wind' | ''

export type DocClass = 'grid' | 'land_survey' | 'environmental' | ''

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
  citations?: Citation[]
  loading?: boolean
  error?: boolean
}

export interface Citation {
  title: string
  url: string
  effective_date?: string
  snippet?: string
}

export interface ChatSession {
  id: string
  title: string
  messages: Message[]
  province: Province
  asset: Asset
  docClass: DocClass
  createdAt: number
  updatedAt: number
}

export interface QueryRequest {
  province: Province
  asset: Asset
  doc_class: DocClass
  question: string
  lang: Language
}

export interface QueryResponse {
  answer_zh?: string
  answer?: string
  citations?: Citation[]
  trace_id?: string
  refusal?: string
  tips?: string[]
  error?: boolean
  message?: string
  elapsed_ms?: number
}
