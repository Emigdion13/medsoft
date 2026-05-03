import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../utils/auth'
import type { UserRole } from '../types'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [first_name, setFirstName] = useState('')
  const [last_name, setLastName] = useState('')
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [role, setRole] = useState<UserRole>('RECEPTIONIST')
  const [password, setPassword] = useState('')
  const [confirm_password, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (password !== confirm_password) {
      setError('Las contraseñas no coinciden')
      return
    }
    setSubmitting(true)
    try {
      await register({ username, email, first_name, last_name, role, password, confirm_password })
      navigate('/dashboard')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error en el registro')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'grid', placeItems: 'center' }}>
      <form onSubmit={onSubmit} style={{ width: 420, background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, padding: 20 }}>
        <h2 style={{ marginTop: 0 }}>Registro</h2>
        <label>Nombre</label>
        <input value={first_name} onChange={(e) => setFirstName(e.target.value)} style={{ width: '100%', marginBottom: 10, padding: 10 }} />
        <label>Apellido</label>
        <input value={last_name} onChange={(e) => setLastName(e.target.value)} style={{ width: '100%', marginBottom: 10, padding: 10 }} />
        <label>Nombre de usuario</label>
        <input value={username} onChange={(e) => setUsername(e.target.value)} style={{ width: '100%', marginBottom: 10, padding: 10 }} />
        <label>Email</label>
        <input value={email} onChange={(e) => setEmail(e.target.value)} style={{ width: '100%', marginBottom: 10, padding: 10 }} />
        <label>Rol</label>
        <select value={role} onChange={(e) => setRole(e.target.value as UserRole)} style={{ width: '100%', marginBottom: 10, padding: 10 }}>
          <option value="ADMINISTRATOR">Administrador</option>
          <option value="DOCTOR">Médico</option>
          <option value="NURSE">Enfermero/a</option>
          <option value="SECRETARY">Secretario/a</option>
          <option value="RECEPTIONIST">Recepcionista</option>
          <option value="LAB_TECHNICIAN">Técnico de Laboratorio</option>
        </select>
        <label>Contraseña</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} style={{ width: '100%', marginBottom: 10, padding: 10 }} />
        <label>Confirmar contraseña</label>
        <input type="password" value={confirm_password} onChange={(e) => setConfirmPassword(e.target.value)} style={{ width: '100%', marginBottom: 10, padding: 10 }} />
        {error && <div style={{ color: '#b91c1c', marginBottom: 10 }}>{error}</div>}
        <button disabled={submitting} style={{ width: '100%', padding: 10, background: '#0d9488', color: '#fff', border: 0, borderRadius: 8 }}>
          {submitting ? 'Creando...' : 'Crear cuenta'}
        </button>
        <p style={{ marginTop: 10 }}>
          ¿Tiene una cuenta? <Link to="/login">Inicio de Sesión</Link>
        </p>
      </form>
    </div>
  )
}
