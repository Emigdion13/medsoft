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
      setError('Passwords do not match')
      return
    }
    setSubmitting(true)
    try {
      await register({ username, email, first_name, last_name, role, password, confirm_password })
      navigate('/dashboard')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'grid', placeItems: 'center' }}>
      <form onSubmit={onSubmit} style={{ width: 420, background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, padding: 20 }}>
        <h2 style={{ marginTop: 0 }}>Register</h2>
        <label>First name</label>
        <input value={first_name} onChange={(e) => setFirstName(e.target.value)} style={{ width: '100%', marginBottom: 10, padding: 10 }} />
        <label>Last name</label>
        <input value={last_name} onChange={(e) => setLastName(e.target.value)} style={{ width: '100%', marginBottom: 10, padding: 10 }} />
        <label>Username</label>
        <input value={username} onChange={(e) => setUsername(e.target.value)} style={{ width: '100%', marginBottom: 10, padding: 10 }} />
        <label>Email</label>
        <input value={email} onChange={(e) => setEmail(e.target.value)} style={{ width: '100%', marginBottom: 10, padding: 10 }} />
        <label>Role</label>
        <select value={role} onChange={(e) => setRole(e.target.value as UserRole)} style={{ width: '100%', marginBottom: 10, padding: 10 }}>
          <option value="ADMINISTRATOR">Administrator</option>
          <option value="DOCTOR">Doctor</option>
          <option value="NURSE">Nurse</option>
          <option value="SECRETARY">Secretary</option>
          <option value="RECEPTIONIST">Receptionist</option>
          <option value="LAB_TECHNICIAN">Lab Technician</option>
        </select>
        <label>Password</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} style={{ width: '100%', marginBottom: 10, padding: 10 }} />
        <label>Confirm password</label>
        <input type="password" value={confirm_password} onChange={(e) => setConfirmPassword(e.target.value)} style={{ width: '100%', marginBottom: 10, padding: 10 }} />
        {error && <div style={{ color: '#b91c1c', marginBottom: 10 }}>{error}</div>}
        <button disabled={submitting} style={{ width: '100%', padding: 10, background: '#0d9488', color: '#fff', border: 0, borderRadius: 8 }}>
          {submitting ? 'Creating...' : 'Create account'}
        </button>
        <p style={{ marginTop: 10 }}>
          Have an account? <Link to="/login">Login</Link>
        </p>
      </form>
    </div>
  )
}
