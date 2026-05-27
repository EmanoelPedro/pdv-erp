import { getRuntimeConfig, initializeRuntimeConfig } from '@/runtime/config'

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE'

type JsonBody = BodyInit | null | undefined

function getAuthHeaders(): Record<string, string> {
  const token = window.localStorage.getItem('pdv:auth-token')

  if (!token) {
    return {}
  }

  return {
    Authorization: `Bearer ${token}`
  }
}

export class ApiError extends Error {
  status: number

  constructor(status: number, detail: string) {
    super(detail)
    this.name = 'ApiError'
    this.status = status
  }
}

async function parseError(response: Response): Promise<ApiError> {
  let detail = `HTTP ${response.status}`

  try {
    const payload = (await response.json()) as { detail?: string }
    if (payload.detail) {
      detail = payload.detail
    }
  } catch {
    detail = `HTTP ${response.status}`
  }

  return new ApiError(response.status, detail)
}

async function request<T>(method: HttpMethod, path: string, body?: JsonBody): Promise<T> {
  const { apiBaseUrl } = await initializeRuntimeConfig()
  const isFormData = body instanceof FormData

  const response = await fetch(`${apiBaseUrl}${path}`, {
    method,
    headers: {
      Accept: 'application/json',
      ...getAuthHeaders(),
      ...(!isFormData && body ? { 'Content-Type': 'application/json' } : {})
    },
    body
  })

  if (!response.ok) {
    throw await parseError(response)
  }

  if (response.status === 204) {
    return undefined as T
  }

  const contentType = response.headers.get('content-type') ?? ''
  if (!contentType.includes('application/json')) {
    return undefined as T
  }

  const rawPayload = await response.text()
  if (!rawPayload) {
    return undefined as T
  }

  return JSON.parse(rawPayload) as T
}

export async function apiGet<T>(path: string): Promise<T> {
  return request<T>('GET', path)
}

export async function apiPost<TResponse, TRequest>(
  path: string,
  payload: TRequest
): Promise<TResponse> {
  return request<TResponse>('POST', path, JSON.stringify(payload))
}

export async function apiPostFormData<TResponse>(
  path: string,
  payload: FormData
): Promise<TResponse> {
  return request<TResponse>('POST', path, payload)
}

export async function apiPostWithoutBody<TResponse>(path: string): Promise<TResponse> {
  return request<TResponse>('POST', path)
}

export async function apiPut<TResponse, TRequest>(
  path: string,
  payload: TRequest
): Promise<TResponse> {
  return request<TResponse>('PUT', path, JSON.stringify(payload))
}

export async function apiDelete<TResponse>(path: string): Promise<TResponse> {
  return request<TResponse>('DELETE', path)
}

export function getApiBaseUrl(): string {
  return getRuntimeConfig().apiBaseUrl
}

