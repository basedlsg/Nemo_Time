import { Language } from '@/types'

export const translations = {
  zh: {
    // App title
    appName: 'Nemo',
    appSubtitle: '能源合规智能助手',

    // Sidebar
    newChat: '新对话',
    chatHistory: '对话历史',
    noChats: '暂无对话历史',
    settings: '设置',

    // Language toggle
    chinese: '中文',
    english: 'English',

    // Province selector
    selectProvince: '选择省份',
    provinces: {
      gd: '广东省',
      sd: '山东省',
      nm: '内蒙古自治区',
    },

    // Asset selector
    selectAsset: '选择资产类型',
    assets: {
      solar: '光伏',
      coal: '煤电',
      wind: '风电',
    },

    // Doc class selector
    selectDocClass: '选择文档类型',
    docClasses: {
      grid: '并网',
      land_survey: '土地勘测',
      environmental: '环境评估',
    },

    // Chat input
    inputPlaceholder: '请输入问题，例如：并网验收需要哪些资料？',
    send: '发送',
    sending: '发送中...',

    // Messages
    you: '您',
    assistant: 'Nemo',
    thinking: '正在思考...',
    error: '查询出错',
    errorMessage: '抱歉，查询时出现错误。请稍后重试。',

    // Citations
    citations: '参考文献',
    viewSource: '查看原文',
    effectiveDate: '生效日期',
    noCitations: '无参考文献',

    // Refusal
    refusalTitle: '无法回答',
    suggestions: '建议',

    // Trace
    traceId: 'Trace ID',

    // Empty state
    welcomeTitle: '欢迎使用 Nemo 能源合规助手',
    welcomeMessage: '请选择省份和资产类型，然后提出您的问题。我会帮您查找相关的政府法规和文件。',

    // Settings
    clearHistory: '清除历史记录',
    clearHistoryConfirm: '确定要清除所有对话历史吗？此操作不可撤销。',
    cancel: '取消',
    confirm: '确认',

    // Validation
    pleaseSelectProvince: '请选择省份',
    pleaseSelectAsset: '请选择资产类型',
    pleaseEnterQuestion: '请输入问题',
  },
  en: {
    // App title
    appName: 'Nemo',
    appSubtitle: 'Energy Compliance Assistant',

    // Sidebar
    newChat: 'New Chat',
    chatHistory: 'Chat History',
    noChats: 'No chat history',
    settings: 'Settings',

    // Language toggle
    chinese: '中文',
    english: 'English',

    // Province selector
    selectProvince: 'Select Province',
    provinces: {
      gd: 'Guangdong',
      sd: 'Shandong',
      nm: 'Inner Mongolia',
    },

    // Asset selector
    selectAsset: 'Select Asset Type',
    assets: {
      solar: 'Solar',
      coal: 'Coal',
      wind: 'Wind',
    },

    // Doc class selector
    selectDocClass: 'Select Document Type',
    docClasses: {
      grid: 'Grid Connection',
      land_survey: 'Land Survey',
      environmental: 'Environmental',
    },

    // Chat input
    inputPlaceholder: 'Ask a question, e.g., What documents are needed for grid acceptance?',
    send: 'Send',
    sending: 'Sending...',

    // Messages
    you: 'You',
    assistant: 'Nemo',
    thinking: 'Thinking...',
    error: 'Error',
    errorMessage: 'Sorry, an error occurred while processing your query. Please try again.',

    // Citations
    citations: 'References',
    viewSource: 'View Source',
    effectiveDate: 'Effective Date',
    noCitations: 'No references',

    // Refusal
    refusalTitle: 'Cannot Answer',
    suggestions: 'Suggestions',

    // Trace
    traceId: 'Trace ID',

    // Empty state
    welcomeTitle: 'Welcome to Nemo Energy Compliance Assistant',
    welcomeMessage: 'Please select a province and asset type, then ask your question. I\'ll help you find relevant government regulations and documents.',

    // Settings
    clearHistory: 'Clear History',
    clearHistoryConfirm: 'Are you sure you want to clear all chat history? This action cannot be undone.',
    cancel: 'Cancel',
    confirm: 'Confirm',

    // Validation
    pleaseSelectProvince: 'Please select a province',
    pleaseSelectAsset: 'Please select an asset type',
    pleaseEnterQuestion: 'Please enter a question',
  },
}

export function getTranslation(lang: Language, key: string): string {
  const keys = key.split('.')
  let value: any = translations[lang]

  for (const k of keys) {
    if (value && typeof value === 'object' && k in value) {
      value = value[k]
    } else {
      return key // Return key if translation not found
    }
  }

  return typeof value === 'string' ? value : key
}
