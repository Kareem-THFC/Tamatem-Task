import { readSession } from '@/lib/storage'
import type { ApiErrorBody, ApiErrorDetail } from '@/types/api'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:5000'


export class ApiError extends Error {
  readonly code: string
  readonly status: number
  readonly details: ApiErrorDetail[]

  constructor(
    code: string,
    message: string,
    status: number,
    details: ApiErrorDetail[] = [],
  ) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.status = status
    this.details = details
  }

  fieldErrors(): Record<string, string> {
    const errors: Record<string, string> = {}

    for (const detail of this.details) {
      if (!(detail.field in errors)) {
        errors[detail.field] = detail.message
      }
    }

    return errors
  }
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  body?: unknown
  auth?: boolean
  signal?: AbortSignal
}

export async function request<T>(
  path: string,
  { method = 'GET', body, auth = false, signal }: RequestOptions = {},
): Promise<T> {
  const headers: Record<string, string> = {}

  headers['Content-Type'] = 'application/json'

  if (auth) {
    const token = readSession()?.token

    if (token) {
      headers.Authorization = `Bearer ${token}`
    }
  }

  let response: Response

  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      signal,
    })
  } catch (error) {
    // fetch only rejects when the request never completed. An HTTP 500 is a
    // resolved promise, handled further down.
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw error
    }

    throw new ApiError(
      'NETWORK_ERROR',
      'Could not reach the server. Is the API running?',
      0,
    )
  }

  const payload = await parseJson(response)

  if (!response.ok) {
    const errorBody = payload as ApiErrorBody | null

    throw new ApiError(
      errorBody?.error?.code ?? 'HTTP_ERROR',
      errorBody?.error?.message ?? `Request failed with status ${response.status}.`,
      response.status,
      errorBody?.error?.details ?? [],
    )
  }

  return payload as T
}

async function parseJson(response: Response): Promise<unknown> {
  const text = await response.text()

  if (!text) {
    return null
  }

  try {
    return JSON.parse(text)
  } catch {
    return null
  }
}

export function buildQuery(
  params: Record<string, string | number | undefined | null>,
): string {
  const search = new URLSearchParams()

  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      search.set(key, String(value))
    }
  }

  const query = search.toString()

  return query ? `?${query}` : ''
}
