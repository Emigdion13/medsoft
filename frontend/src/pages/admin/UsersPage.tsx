import React, { useState } from 'react'
import { UserList } from './UserList'
import { UserForm } from './UserForm'
import { usersService } from '../../services/authService'
import type { UserListItem, UserRole } from '../../types'

const defaultForm: {
  first_name: string
  last_name: string
  username: string
  email: string
  role: UserRole
  is_active: boolean
} = {
  first_name: '',
  last_name: '',
  username: '',
  email: '',
  role: 'RECEPTIONIST',
  is_active: true,
}

export default function AdminUsersPage() {
  const [editing, setEditing] = useState<UserListItem | null>(null)
  const [form, setForm] = useState(defaultForm)

  const onSelectEdit = (u: UserListItem) => {
    setEditing(u)
    setForm({
      first_name: u.first_name,
      last_name: u.last_name,
      username: u.username,
      email: u.email,
      role: u.role,
      is_active: u.is_active,
    })
  }

  const onSubmit = async () => {
    if (editing) {
      await usersService.update(editing.id, form)
      setEditing(null)
      setForm(defaultForm)
      return
    }
    await usersService.create(form)
    setForm(defaultForm)
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: 12 }}>
      <UserList onSelectEdit={onSelectEdit} />
      <UserForm value={form} onChange={setForm} onSubmit={() => void onSubmit()} submitLabel={editing ? 'Update user' : 'Create user'} />
    </div>
  )
}
