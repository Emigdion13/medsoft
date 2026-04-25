import React from 'react'
import { Navigate } from 'react-router-dom'
import type { ActionKey, ModuleKey, PermissionContext } from '../../types'
import { useAuth } from '../../utils/auth'
import { can, canAccessRoute } from './can'

export function CanAccessRoute({ module, children }: { module: ModuleKey; children: React.ReactNode }) {
  const { user, loading, isAuthenticated } = useAuth()

  if (loading) return <div style={{ padding: 24 }}>Loading...</div>
  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (!canAccessRoute(user, module)) return <Navigate to="/dashboard" replace />

  return <>{children}</>
}

export function CanAccess({ module, action, context, children }: { module: ModuleKey; action: ActionKey; context?: PermissionContext; children: React.ReactNode }) {
  const { user } = useAuth()
  if (!can(user, action, module, context)) return null
  return <>{children}</>
}
