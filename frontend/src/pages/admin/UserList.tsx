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

  const load = async () => {
    const res = await usersService.list({ search, page: 1 })
    setUsers(res.results)
  }

  useEffect(() => {
    void load()
  }, [])

  return (
    <PageContainer title="Users">
      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search" style={{ padding: 10, minWidth: 240 }} />
        <button onClick={() => void load()} style={{ padding: '10px 12px' }}>Search</button>
      </div>
      <table style={{ width: '100%', background: '#fff', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={{ textAlign: 'left', padding: 8 }}>Name</th>
            <th style={{ textAlign: 'left', padding: 8 }}>Email</th>
            <th style={{ textAlign: 'left', padding: 8 }}>Role</th>
            <th style={{ textAlign: 'left', padding: 8 }}>Status</th>
            <th style={{ textAlign: 'left', padding: 8 }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td style={{ padding: 8 }}>{u.first_name} {u.last_name}</td>
              <td style={{ padding: 8 }}>{u.email}</td>
              <td style={{ padding: 8 }}>{u.role}</td>
              <td style={{ padding: 8 }}>{u.is_active ? 'Active' : 'Inactive'}</td>
              <td style={{ padding: 8 }}>
                <button onClick={() => onSelectEdit(u)} style={{ padding: '6px 10px' }}>Edit</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </PageContainer>
  )
}
