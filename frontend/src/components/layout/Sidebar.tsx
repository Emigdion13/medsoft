import React from 'react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../../utils/auth'
import { can } from '../../lib/rbac/can'

type NavItem = { to: string; label: string; icon: string; module: string }

const ROLE_LABELS: Record<string, string> = {
  ADMINISTRATOR: 'Administrador',
  DOCTOR: 'Médico',
  RECEPTIONIST: 'Recepcionista',
  SECRETARY: 'Secretario/a',
  NURSE: 'Enfermero/a',
  LAB_TECHNICIAN: 'Téc. Laboratorio',
}

const linkBase: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 12,
  padding: '10px 14px',
  borderRadius: 8,
  marginBottom: 3,
  fontSize: 14,
  color: '#94a3b8',
  transition: 'all .15s ease',
}

const activeStyle: React.CSSProperties = {
  ...linkBase,
  background: 'var(--sidebar-active)',
  color: '#e2e8f0',
  fontWeight: 500,
}

export default function Sidebar() {
  const { user, logout } = useAuth()
  const roleLabel = ROLE_LABELS[user?.role ?? ''] ?? user?.role ?? 'Usuario'

  const navItems: NavItem[] = [
    { to: '/dashboard', label: 'Escritorio', icon: '📊', module: 'dashboard' },
    { to: '/citas', label: 'Citas', icon: '📅', module: 'appointments' },
    { to: '/pacientes', label: 'Pacientes', icon: '👥', module: 'patients' },
    { to: '/historial-medico', label: 'Historial Médico', icon: '📋', module: 'medical_records' },
    { to: '/admin/users', label: 'Usuarios', icon: '⚙️', module: 'users' },
    { to: '/admin/specialties', label: 'Especialidades', icon: '🏥', module: 'users' },
  ]

  return (
    <aside style={{
      width: 250,
      background: 'var(--sidebar-bg)',
      color: '#fff',
      padding: '20px 12px',
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
    }}>
      {/* Logo */}
      <div style={{ padding: '0 8px 20px', borderBottom: '1px solid rgba(255,255,255,.08)', marginBottom: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 10,
            background: 'linear-gradient(135deg, #3b82f6, #2563eb)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 18, fontWeight: 700, color: '#fff',
          }}>M</div>
          <div>
            <div style={{ fontWeight: 700, fontSize: 16 }}>MediSoft</div>
            <div style={{ fontSize: 11, color: '#64748b' }}>Gestión Médica</div>
          </div>
        </div>
      </div>

      {/* User info + role badge */}
      <div style={{ padding: '0 8px 16px' }}>
        <div style={{ fontSize: 13, color: '#cbd5e1', marginBottom: 2 }}>
          {user?.first_name} {user?.last_name}
        </div>
        <span style={{
          display: 'inline-block',
          fontSize: 11,
          fontWeight: 500,
          color: '#93c5fd',
          background: 'rgba(59,130,246,.15)',
          padding: '3px 10px',
          borderRadius: 20,
          letterSpacing: '.3px',
        }}>
          {roleLabel}
        </span>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1 }}>
        {navItems.map((item) => {
          if (!can(user, 'view', item.module)) return null
          return (
            <NavLink
              key={item.to}
              to={item.to}
              style={({ isActive }) => isActive ? activeStyle : linkBase}
            >
              <span style={{ fontSize: 18, width: 24, textAlign: 'center' }}>{item.icon}</span>
              {item.label}
            </NavLink>
          )
        })}
      </nav>

      {/* Logout */}
      <button onClick={logout} style={{
        width: '100%', padding: '10px 14px', borderRadius: 8,
        border: 'none', background: 'rgba(239,68,68,.12)', color: '#fca5a5',
        fontSize: 13, fontWeight: 500, cursor: 'pointer',
        display: 'flex', alignItems: 'center', gap: 10,
        transition: 'background .15s',
      }}>
        <span style={{ fontSize: 16 }}>🚪</span>
        Cerrar sesión
      </button>
    </aside>
  )
}
