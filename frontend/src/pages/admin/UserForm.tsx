import React from 'react'
import type { UserRole } from '../../types'

interface UserFormState {
  first_name: string
  last_name: string
  username: string
  email: string
  phone: string
  role: UserRole
  is_active: boolean
}

interface UserFormProps {
  value: UserFormState
  onChange: (next: UserFormState) => void
  onSubmit: () => void
  submitLabel: string
}

const labelStyle: React.CSSProperties = {
  display: 'block', fontSize: 13, fontWeight: 600,
  color: '#374151', marginBottom: 5,
}

const inputBase: React.CSSProperties = {
  width: '100%', padding: '10px 14px', fontSize: 14,
  border: '1px solid #d1d5db', borderRadius: 8,
  outline: 'none', boxSizing: 'border-box',
  transition: 'border-color .15s',
}

export function UserForm({ value, onChange, onSubmit, submitLabel }: UserFormProps) {
  const isEditing = submitLabel.includes('Actualizar')

  return (
    <div style={{
      background: '#fff', border: '1px solid #e5e7eb',
      borderRadius: 14, padding: 24, boxShadow: 'var(--shadow)',
    }}>
      <h2 style={{ margin: '0 0 6px', fontSize: 18, fontWeight: 700, color: '#1e293b' }}>
        {isEditing ? 'Editar Usuario' : 'Nuevo Usuario'}
      </h2>
      <p style={{ margin: '0 0 20px', fontSize: 13, color: '#6b7280' }}>
        {isEditing ? 'Modifique los datos del usuario' : 'Complete el formulario para crear una cuenta'}
      </p>

      {/* Name row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginBottom: 16 }}>
        <div>
          <label style={labelStyle}>Nombre</label>
          <input
            placeholder="Ej: María"
            value={value.first_name}
            onChange={(e) => onChange({ ...value, first_name: e.target.value })}
            style={inputBase}
          />
        </div>
        <div>
          <label style={labelStyle}>Apellido</label>
          <input
            placeholder="Ej: López"
            value={value.last_name}
            onChange={(e) => onChange({ ...value, last_name: e.target.value })}
            style={inputBase}
          />
        </div>
      </div>

      {/* Username + Email */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginBottom: 16 }}>
        <div>
          <label style={labelStyle}>Nombre de usuario</label>
          <input
            placeholder="ej: maria.lopez"
            value={value.username}
            onChange={(e) => onChange({ ...value, username: e.target.value })}
            style={inputBase}
          />
        </div>
        <div>
          <label style={labelStyle}>Email</label>
          <input
            type="email"
            placeholder="ej: maria@clinica.com"
            value={value.email}
            onChange={(e) => onChange({ ...value, email: e.target.value })}
            style={inputBase}
          />
        </div>
      </div>

      {/* Phone */}
      <div style={{ marginBottom: 16 }}>
        <label style={labelStyle}>Teléfono</label>
        <input
          placeholder="+1-809-555-0000"
          value={value.phone}
          onChange={(e) => onChange({ ...value, phone: e.target.value })}
          style={inputBase}
        />
      </div>

      {/* Role + Status */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginBottom: 20 }}>
        <div>
          <label style={labelStyle}>Rol</label>
          <select
            value={value.role}
            onChange={(e) => onChange({ ...value, role: e.target.value as UserRole })}
            style={{ ...inputBase, cursor: 'pointer', background: '#fff' }}
          >
            <option value="DOCTOR">👨‍⚕️ Médico</option>
            <option value="NURSE">💉 Enfermero/a</option>
            <option value="SECRETARY">📋 Secretario/a</option>
            <option value="RECEPTIONIST">🛎️ Recepcionista</option>
            <option value="LAB_TECHNICIAN">🔬 Técnico de Laboratorio</option>
            <option value="ADMINISTRATOR">⚙️ Administrador</option>
          </select>
        </div>
        <div>
          <label style={labelStyle}>Estado</label>
          <label style={{
            display: 'flex', alignItems: 'center', gap: 10,
            padding: '10px 14px', border: '1px solid #d1d5db',
            borderRadius: 8, cursor: 'pointer', background: value.is_active ? '#f0fdf4' : '#fff',
          }}>
            <input
              type="checkbox"
              checked={value.is_active}
              onChange={(e) => onChange({ ...value, is_active: e.target.checked })}
              style={{ width: 18, height: 18, accentColor: '#10b981' }}
            />
            <span style={{ fontSize: 14, fontWeight: 500, color: value.is_active ? '#059669' : '#6b7280' }}>
              {value.is_active ? '🟢 Activo' : '⚪ Inactivo'}
            </span>
          </label>
        </div>
      </div>

      {/* Submit */}
      <button onClick={onSubmit} style={{
        width: '100%', padding: '11px 0', fontSize: 15, fontWeight: 600,
        background: isEditing
          ? 'linear-gradient(135deg, #2563eb, #1d4ed8)'
          : 'linear-gradient(135deg, #059669, #047857)',
        color: '#fff', border: 'none', borderRadius: 8,
        cursor: 'pointer', boxShadow: isEditing
          ? '0 4px 14px rgba(37,99,235,.3)'
          : '0 4px 14px rgba(5,150,105,.3)',
      }}>
        {submitLabel}
      </button>
    </div>
  )
}
