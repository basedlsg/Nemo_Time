import { QueryRequest, QueryResponse } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

export async function sendQuery(request: QueryRequest): Promise<QueryResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    const data = await response.json()

    if (!response.ok) {
      return {
        error: true,
        message: data.message || 'Unknown error occurred',
        trace_id: data.trace_id || 'unknown',
      }
    }

    return data
  } catch (error) {
    console.error('API request failed:', error)
    return {
      error: true,
      message: error instanceof Error ? error.message : 'Network error',
      trace_id: `client-error-${Date.now()}`,
    }
  }
}
