import React from 'react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../../utils/auth'
import { can } from '../../lib/rbac/can'

const linkStyle: React.CSSProperties = {
  display: 'block',
  padding: '10px 12px',
  borderRadius: 8,
  marginBottom: 6,
}

export default function Sidebar() {
  const { user, logout } = useAuth()

  return (
    <aside style={{ width: 260, background: '#0f172a', color: '#fff', padding: 16, minHeight: '100vh' }}>
      <h2 style={{ marginTop: 0 }}>MediSoft</h2>
      <div style={{ opacity: 0.8, marginBottom: 12 }}>{user?.first_name} {user?.last_name}</div>

      <NavLink to="/dashboard" style={linkStyle}>Dashboard</NavLink>

      {can(user, 'view', 'appointments') && <NavLink to="/appointments" style={linkStyle}>Appointments</NavLink>}
      {can(user, 'view', 'patients') && <NavLink to="/patients" style={linkStyle}>Patients</NavLink>}
      {can(user, 'view', 'medical_records') && <NavLink to="/medical-records" style={linkStyle}>Medical Records</NavLink>}
      {can(user, 'view', 'users') && <NavLink to="/admin/users" style={linkStyle}>User Management</NavLink>}

      <button onClick={logout} style={{ marginTop: 16, width: '100%', padding: '10px 12px', borderRadius: 8, border: 0, background: '#ef4444', color: '#fff' }}>
        Logout
      </button>
    </aside>
  )
}
