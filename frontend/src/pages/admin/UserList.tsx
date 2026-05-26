import React, { useEffect, useState } from 'react'
import type { UserListItem } from '../../types'
import { usersService } from '../../services/authService'

interface UserListProps {
  onSelectEdit: (user: UserListItem) => void
  refreshKey?: number
}

const ROLE_STYLE: Record<string, { bg: string; color: string; label: string }> = {
  ADMINISTRATOR: { bg: '#ede9fe', color: '#7c3aed', label: 'Administrador' },
  DOCTOR: { bg: '#dbeafe', color: '#2563eb', label: 'Médico' },
  SECRETARY: { bg: '#fce7f3', color: '#db2777', label: 'Secretario/a' },
  RECEPTIONIST: { bg: '#d1fae5', color: '#059669', label: 'Recepcionista' },
  NURSE: { bg: '#fef3c7', color: '#d97706', label: 'Enfermero/a' },
  LAB_TECHNICIAN: { bg: '#e0e7ff', color: '#4f46e5', label: 'Téc. Lab.' },
}

export function UserList({ onSelectEdit, refreshKey }: UserListProps) {
  const [users, setUsers] = useState<UserListItem[]>([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    try {
      setLoading(true)
      setError(null)
      const res = await usersService.list({ search, page: 1 })
      setUsers(res?.results ?? [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar usuarios')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { void load() }, [refreshKey])

  if (loading && users.length === 0) {
    return (
      <div style={cardStyle}>
        <div style={{ textAlign: 'center', padding: 40, color: '#9ca3af' }}>Cargando usuarios...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div style={cardStyle}>
        <div style={{ textAlign: 'center', padding: 40 }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>⚠️</div>
          <div style={{ color: '#dc2626', marginBottom: 12, fontWeight: 500 }}>{error}</div>
          <button onClick={() => void load()} style={btnOutline}>Reintentar</button>
        </div>
      </div>
    )
  }

  return (
    <div style={cardStyle}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h2 style={{ margin: 0, fontSize: 18, fontWeight: 700, color: '#1e293b' }}>Usuarios</h2>
        <span style={{
          background: '#f1f5f9', color: '#475569', borderRadius: 20,
          padding: '3px 12px', fontSize: 13, fontWeight: 500,
        }}>
          {users.length} usuario{users.length !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Search bar */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <div style={{ position: 'relative', flex: 1 }}>
          <span style={{ position: 'absolute', left: 12, top: 10, fontSize: 14 }}>🔍</span>
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && load()}
            placeholder="Buscar por nombre o email..."
            style={{
              width: '100%', padding: '9px 12px 9px 36px', fontSize: 14,
              border: '1px solid #e2e8f0', borderRadius: 8,
              outline: 'none', boxSizing: 'border-box',
              transition: 'border-color .15s',
            }}
          />
        </div>
        <button onClick={() => void load()} style={btnOutline}>Buscar</button>
      </div>

      {/* Table */}
      <div style={{ borderRadius: 10, overflow: 'hidden', border: '1px solid #e5e7eb' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
          <thead>
            <tr style={{ background: '#f8fafc', borderBottom: '2px solid #e5e7eb' }}>
              <th style={thStyle}>Nombre</th>
              <th style={thStyle}>Email</th>
              <th style={thStyle}>Rol</th>
              <th style={{ ...thStyle, textAlign: 'center' }}>Estado</th>
              <th style={{ ...thStyle, textAlign: 'center', width: 90 }}>Acción</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u, i) => {
              const roleCfg = ROLE_STYLE[u.role] || { bg: '#f1f5f9', color: '#475569', label: u.role }
              return (
                <tr key={u.id} style={{
                  background: i % 2 === 0 ? '#fff' : '#fafbfc',
                  borderBottom: '1px solid #f1f5f9',
                  transition: 'background .1s',
                }}>
                  <td style={tdStyle}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <div style={{
                        width: 32, height: 32, borderRadius: '50%',
                        background: roleCfg.bg, color: roleCfg.color,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: 14, fontWeight: 600,
                      }}>
                        {u.first_name.charAt(0)}{u.last_name.charAt(0)}
                      </div>
                      <div>
                        <div style={{ fontWeight: 600 }}>{u.first_name} {u.last_name}</div>
                        <div style={{ fontSize: 12, color: '#94a3b8' }}>@{u.username}</div>
                      </div>
                    </div>
                  </td>
                  <td style={{ ...tdStyle, color: '#64748b' }}>{u.email}</td>
                  <td style={tdStyle}>
                    <span style={{
                      display: 'inline-block', padding: '3px 10px', borderRadius: 20,
                      fontSize: 12, fontWeight: 500,
                      background: roleCfg.bg, color: roleCfg.color,
                    }}>
                      {roleCfg.label}
                    </span>
                  </td>
                  <td style={{ ...tdStyle, textAlign: 'center' }}>
                    <span style={{
                      display: 'inline-block', width: 8, height: 8, borderRadius: '50%',
                      background: u.is_active ? '#10b981' : '#ef4444',
                      marginRight: 6, verticalAlign: 'middle',
                    }} />
                    <span style={{ fontSize: 13, color: u.is_active ? '#059669' : '#dc2626' }}>
                      {u.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td style={{ ...tdStyle, textAlign: 'center' }}>
                    <button onClick={() => onSelectEdit(u)} style={{
                      padding: '6px 14px', borderRadius: 6, border: '1px solid #d1d5db',
                      background: '#fff', color: '#374151', cursor: 'pointer',
                      fontSize: 13, fontWeight: 500, transition: 'all .15s',
                    }}>
                      Editar
                    </button>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

const cardStyle: React.CSSProperties = {
  background: '#fff', border: '1px solid #e5e7eb',
  borderRadius: 14, padding: 20, boxShadow: 'var(--shadow)',
}
const thStyle: React.CSSProperties = {
  textAlign: 'left', padding: '10px 14px', fontWeight: 600,
  fontSize: 12, color: '#64748b', textTransform: 'uppercase', letterSpacing: '.5px',
}
const tdStyle: React.CSSProperties = { padding: '12px 14px' }
const btnOutline: React.CSSProperties = {
  padding: '8px 16px', borderRadius: 8, border: '1px solid #d1d5db',
  background: '#fff', color: '#374151', cursor: 'pointer',
  fontSize: 13, fontWeight: 500, transition: 'all .15s',
}
