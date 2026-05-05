import React, { useEffect, useState } from 'react'
import { PageContainer } from '../../components/common/SharedComponents'
import type { UserListItem } from '../../types'
import { usersService } from '../../services/authService'

interface UserListProps {
  onSelectEdit: (user: UserListItem) => void
}

export function UserList({ onSelectEdit }: UserListProps) {
  const [users, setUsers] = useState<UserListItem[]>([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    try {
      setLoading(true)
      setError(null)
      const res = await usersService.list({ search, page: 1 })
      console.log('[UserList] API Response:', res)
      console.log('[UserList] Results:', res?.results)
      setUsers(res?.results ?? [])
    } catch (err) {
      console.error('Error loading users:', err)
      setError(err instanceof Error ? err.message : 'Error al cargar usuarios')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  if (loading && users.length === 0) {
    return (
      <PageContainer title="Usuarios">
        <div>Cargando...</div>
      </PageContainer>
    )
  }

  if (error) {
    return (
      <PageContainer title="Usuarios">
        <div style={{ color: 'red' }}>Error: {error}</div>
        <button onClick={() => void load()}>Reintentar</button>
      </PageContainer>
    )
  }

  // Safety check - if users is still undefined or null
  if (!users || !Array.isArray(users)) {
    return (
      <PageContainer title="Usuarios">
        <div style={{ color: 'red' }}>Datos inválidos recibidos</div>
      </PageContainer>
    )
  }

  return (
    <PageContainer title="Usuarios">
      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Buscar" style={{ padding: 10, minWidth: 240 }} />
        <button onClick={() => void load()} style={{ padding: '10px 12px' }}>Buscar</button>
      </div>
      <table style={{ width: '100%', background: '#fff', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={{ textAlign: 'left', padding: 8 }}>Nombre</th>
            <th style={{ textAlign: 'left', padding: 8 }}>Email</th>
            <th style={{ textAlign: 'left', padding: 8 }}>Rol</th>
            <th style={{ textAlign: 'left', padding: 8 }}>Estado</th>
            <th style={{ textAlign: 'left', padding: 8 }}>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td style={{ padding: 8 }}>{u.first_name} {u.last_name}</td>
              <td style={{ padding: 8 }}>{u.email}</td>
              <td style={{ padding: 8 }}>{u.role}</td>
              <td style={{ padding: 8 }}>{u.is_active ? 'Activo' : 'Inactivo'}</td>
              <td style={{ padding: 8 }}>
                <button onClick={() => onSelectEdit(u)} style={{ padding: '6px 10px' }}>Editar</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </PageContainer>
  )
}
