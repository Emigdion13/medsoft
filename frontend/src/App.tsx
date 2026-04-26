import React from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import Sidebar from './components/layout/Sidebar'
import TopBar from './components/layout/TopBar'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import Register from './pages/Register'
import AdminUsersPage from './pages/admin/UsersPage'
import { CanAccessRoute } from './lib/rbac/guards'
import { useAuth } from './utils/auth'

function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const { loading, isAuthenticated } = useAuth()

  if (loading) return <div style={{ padding: 24 }}>Loading...</div>
  if (!isAuthenticated) return <Navigate to="/login" replace />

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '260px 1fr', minHeight: '100vh' }}>
      <Sidebar />
      <div>
        <TopBar />
        {children}
      </div>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      <Route
        path="/dashboard"
        element={
          <ProtectedLayout>
            <CanAccessRoute module="dashboard">
              <Dashboard />
            </CanAccessRoute>
          </ProtectedLayout>
        }
      />

      <Route
        path="/admin/users"
        element={
          <ProtectedLayout>
            <CanAccessRoute module="users">
              <AdminUsersPage />
            </CanAccessRoute>
          </ProtectedLayout>
        }
      />

      <Route
        path="/admin/users/register"
        element={
          <ProtectedLayout>
            <CanAccessRoute module="users">
              <Register />
            </CanAccessRoute>
          </ProtectedLayout>
        }
      />

      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}
