import React from 'react'
import { PageContainer } from '../../components/common/SharedComponents'
import type { UserRole } from '../../types'

interface UserFormState {
  first_name: string
  last_name: string
  username: string
  email: string
  role: UserRole
  is_active: boolean
}

interface UserFormProps {
  value: UserFormState
  onChange: (next: UserFormState) => void
  onSubmit: () => void
  submitLabel: string
}

export function UserForm({ value, onChange, onSubmit, submitLabel }: UserFormProps) {
  return (
    <PageContainer title="Formulario de Usuario">
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0,1fr))', gap: 10 }}>
        <input placeholder="Nombre" value={value.first_name} onChange={(e) => onChange({ ...value, first_name: e.target.value })} style={{ padding: 10 }} />
        <input placeholder="Apellido" value={value.last_name} onChange={(e) => onChange({ ...value, last_name: e.target.value })} style={{ padding: 10 }} />
        <input placeholder="Nombre de usuario" value={value.username} onChange={(e) => onChange({ ...value, username: e.target.value })} style={{ padding: 10 }} />
        <input placeholder="Email" value={value.email} onChange={(e) => onChange({ ...value, email: e.target.value })} style={{ padding: 10 }} />
        <select value={value.role} onChange={(e) => onChange({ ...value, role: e.target.value as UserRole })} style={{ padding: 10 }}>
          <option value="DOCTOR">Médico</option>
          <option value="NURSE">Enfermero/a</option>
          <option value="SECRETARY">Secretario/a</option>
          <option value="RECEPTIONIST">Recepcionista</option>
          <option value="LAB_TECHNICIAN">Técnico de Laboratorio</option>
          <option value="ADMINISTRATOR">Administrador</option>
        </select>
        <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input type="checkbox" checked={value.is_active} onChange={(e) => onChange({ ...value, is_active: e.target.checked })} /> Activo
        </label>
      </div>
      <button onClick={onSubmit} style={{ marginTop: 12, padding: '10px 14px', border: 0, borderRadius: 8, background: '#2563eb', color: '#fff' }}>{submitLabel}</button>
    </PageContainer>
  )
}
