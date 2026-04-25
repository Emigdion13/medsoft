import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../utils/auth'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await login({ username, password })
      navigate('/dashboard')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'grid', placeItems: 'center' }}>
      <form onSubmit={onSubmit} style={{ width: 380, background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, padding: 20 }}>
        <h2 style={{ marginTop: 0 }}>Login</h2>
        <label>Username</label>
        <input value={username} onChange={(e) => setUsername(e.target.value)} style={{ width: '100%', marginBottom: 10, padding: 10 }} />
        <label>Password</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} style={{ width: '100%', marginBottom: 10, padding: 10 }} />
        {error && <div style={{ color: '#b91c1c', marginBottom: 10 }}>{error}</div>}
        <button disabled={submitting} style={{ width: '100%', padding: 10, background: '#2563eb', color: '#fff', border: 0, borderRadius: 8 }}>
          {submitting ? 'Signing in...' : 'Sign in'}
        </button>
        <p style={{ marginTop: 10 }}>
          No account? <Link to="/register">Register</Link>
        </p>
      </form>
    </div>
  )
}
