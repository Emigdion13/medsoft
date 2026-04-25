import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'
import type { LoginPayload, RegisterPayload, User } from '../types'
import { authService } from '../services/authService'
import { session } from './session'

interface AuthContextValue {
  user: User | null
  loading: boolean
  isAuthenticated: boolean
  login: (payload: LoginPayload) => Promise<void>
  register: (payload: RegisterPayload) => Promise<void>
  logout: () => void
  refreshSession: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(session.getUser())
  const [loading, setLoading] = useState(true)

  const logout = () => {
    session.clear()
    setUser(null)
  }

  const refreshSession = async () => {
    try {
      const me = await authService.me()
      session.setUser(me)
      setUser(me)
    } catch {
      logout()
    }
  }

  const login = async (payload: LoginPayload) => {
    const res = await authService.login(payload)
    session.setTokens({ access: res.access, refresh: res.refresh })
    session.setUser(res.user)
    setUser(res.user)
  }

  const register = async (payload: RegisterPayload) => {
    const res = await authService.register(payload)
    session.setTokens({ access: res.access, refresh: res.refresh })
    session.setUser(res.user)
    setUser(res.user)
  }

  useEffect(() => {
    const init = async () => {
      const token = session.getAccessToken()
      if (!token) {
        setLoading(false)
        return
      }
      await refreshSession()
      setLoading(false)
    }
    void init()
  }, [])

  const value = useMemo(
    () => ({
      user,
      loading,
      isAuthenticated: Boolean(user),
      login,
      register,
      logout,
      refreshSession,
    }),
    [user, loading]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
