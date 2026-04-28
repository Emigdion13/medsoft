import type { AuthResponse } from '../types'
import { session } from './session'

type HttpMethod = 'GET' | 'POST' | 'PATCH' | 'PUT' | 'DELETE'

interface RequestOptions {
  method?: HttpMethod
  body?: unknown
  params?: Record<string, string | number | boolean | undefined>
  headers?: Record<string, string>
  retry?: boolean
}

// Use /api as the default so the Vite dev proxy handles routing during local dev.
// Docker builds override this via ENV VITE_API_URL=/api in the Dockerfile.
const BASE_URL = import.meta.env.VITE_API_URL || '/api'

function buildUrl(path: string, params?: RequestOptions['params']): string {
  // Remove leading slash from path if present to avoid double slashes
  const cleanPath = path.startsWith('/') ? path : `/${path}`
  
  // If BASE_URL is a full URL, use it directly
  if (BASE_URL.startsWith('http://') || BASE_URL.startsWith('https://')) {
    return `${BASE_URL}${cleanPath}`
  }
  
  // For relative paths, construct with window location
  const url = new URL(`${BASE_URL}${cleanPath}`, window.location.origin)
  
  // Add query params if present
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null) url.searchParams.set(k, String(v))
    })
  }
  
  return url.toString()
}

async function refreshAccessToken(): Promise<string | null> {
  const refresh = session.getRefreshToken()
  if (!refresh) return null

  const res = await fetch(`${BASE_URL}/auth/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh }),
  })

  if (!res.ok) return null
  const data = (await res.json()) as Partial<AuthResponse> & { access?: string }
  const access = data.access
  if (!access) return null

  // Backend may rotate the refresh token; use the new one if provided
  const newRefresh = data.refresh ?? refresh
  session.setTokens({ access, refresh: newRefresh })
  return access
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, params, headers = {}, retry = true } = options
  const token = session.getAccessToken()

  console.log('[API Request]', {
    url: buildUrl(path, params),
    method,
    hasToken: !!token,
    tokenPrefix: token ? token.slice(0, 20) + '...' : 'none',
    path,
  })

  const res = await fetch(buildUrl(path, params), {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  console.log('[API Response]', {
    path,
    status: res.status,
    statusText: res.statusText,
    ok: res.ok,
  })

  if (res.status === 401 && retry) {
    console.log('[API] 401 received, attempting token refresh...')
    const refreshed = await refreshAccessToken()
    if (refreshed) {
      console.log('[API] Token refreshed successfully')
      return request<T>(path, { ...options, retry: false })
    }
    console.warn('[API] Token refresh failed — session expired')
    session.clear()
    throw new Error('Session expired. Please log in again.')
  }

  const text = await res.text()
  const data = text ? JSON.parse(text) : null

  if (!res.ok) {
    const message = data?.detail || data?.message || 'Request failed'
    console.error('[API Error]', { path, status: res.status, message, response: data })
    throw new Error(message)
  }

  return data as T
}

export const api = {
  get<T>(path: string, opts?: Omit<RequestOptions, 'method' | 'body'>) {
    return request<T>(path, { ...opts, method: 'GET' })
  },

  post<T>(path: string, body?: unknown, opts?: Omit<RequestOptions, 'method' | 'body'>) {
    return request<T>(path, { ...opts, method: 'POST', body })
  },

  patch<T>(path: string, body?: unknown, opts?: Omit<RequestOptions, 'method' | 'body'>) {
    return request<T>(path, { ...opts, method: 'PATCH', body })
  },

  put<T>(path: string, body?: unknown, opts?: Omit<RequestOptions, 'method' | 'body'>) {
    return request<T>(path, { ...opts, method: 'PUT', body })
  },

  delete<T>(path: string, opts?: Omit<RequestOptions, 'method' | 'body'>) {
    return request<T>(path, { ...opts, method: 'DELETE' })
  },
}
