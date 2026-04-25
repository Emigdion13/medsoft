import { jwtDecode } from 'jwt-decode'
import type { AuthTokens, User } from '../types'

const ACCESS_TOKEN_KEY = 'accessToken'
const REFRESH_TOKEN_KEY = 'refreshToken'
const USER_KEY = 'user'

interface JwtPayload {
  exp?: number
}

export const session = {
  setTokens(tokens: AuthTokens): void {
    localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access)
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh)
  },

  getAccessToken(): string | null {
    return localStorage.getItem(ACCESS_TOKEN_KEY)
  },

  getRefreshToken(): string | null {
    return localStorage.getItem(REFRESH_TOKEN_KEY)
  },

  setUser(user: User): void {
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  },

  getUser(): User | null {
    const raw = localStorage.getItem(USER_KEY)
    if (!raw) return null
    try {
      return JSON.parse(raw) as User
    } catch {
      return null
    }
  },

  clear(): void {
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  },

  isAccessTokenExpired(bufferMs = Number(import.meta.env.VITE_TOKEN_REFRESH_BUFFER || 300000)): boolean {
    const token = this.getAccessToken()
    if (!token) return true
    try {
      const payload = jwtDecode<JwtPayload>(token)
      if (!payload.exp) return true
      const expiry = payload.exp * 1000
      return Date.now() + bufferMs >= expiry
    } catch {
      return true
    }
  },
}
