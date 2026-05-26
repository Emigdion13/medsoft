import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
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
      setError(err instanceof Error ? err.message : 'Credenciales inválidas')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      background: 'linear-gradient(135deg, #0f1a2e 0%, #1e3a5f 50%, #1e40af 100%)',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Decorative blobs */}
      <div style={{
        position: 'absolute', top: -100, left: -100,
        width: 400, height: 400, borderRadius: '50%',
        background: 'rgba(59,130,246,.1)',
      }} />
      <div style={{
        position: 'absolute', bottom: -80, right: -80,
        width: 350, height: 350, borderRadius: '50%',
        background: 'rgba(99,102,241,.08)',
      }} />

      {/* Left brand panel */}
      <div style={{
        flex: 1, display: 'flex', flexDirection: 'column',
        justifyContent: 'center', alignItems: 'center',
        padding: 60, color: '#fff', position: 'relative', zIndex: 1,
      }}>
        <div style={{ maxWidth: 420, textAlign: 'center' }}>
          <div style={{
            width: 64, height: 64, borderRadius: 18,
            background: 'linear-gradient(135deg, #3b82f6, #2563eb)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 30, fontWeight: 700, margin: '0 auto 20px',
            boxShadow: '0 8px 32px rgba(37,99,235,.4)',
          }}>M</div>
          <h1 style={{ fontSize: 32, fontWeight: 700, margin: '0 0 8px', letterSpacing: '-.5px' }}>
            MediSoft
          </h1>
          <p style={{ fontSize: 16, opacity: .7, margin: 0, lineHeight: 1.6 }}>
            Sistema de Gestión Médica Integral.<br />
            Administre pacientes, citas e historiales clínicos en un solo lugar.
          </p>
        </div>
      </div>

      {/* Right form panel */}
      <div style={{
        flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center',
        position: 'relative', zIndex: 1,
      }}>
        <form onSubmit={onSubmit} style={{
          width: 380, background: '#fff', borderRadius: 20,
          padding: '36px 32px', boxShadow: '0 20px 60px rgba(0,0,0,.3)',
        }}>
          <h2 style={{ margin: '0 0 6px', fontSize: 22, fontWeight: 700 }}>
            Inicio de Sesión
          </h2>
          <p style={{ margin: '0 0 24px', fontSize: 14, color: 'var(--gray-500)' }}>
            Ingrese sus credenciales para acceder
          </p>

          <div style={{ marginBottom: 16 }}>
            <label htmlFor="username" style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: 'var(--gray-700)' }}>
              Nombre de usuario
            </label>
            <input
              id="username" autoFocus
              value={username} onChange={(e) => setUsername(e.target.value)}
              placeholder="admin"
              style={{
                width: '100%', padding: '10px 14px', fontSize: 14,
                border: '1px solid var(--gray-300)', borderRadius: 8,
                outline: 'none', transition: 'border-color .15s',
                boxSizing: 'border-box',
              }}
            />
          </div>

          <div style={{ marginBottom: 16 }}>
            <label htmlFor="password" style={{ display: 'block', fontSize: 13, fontWeight: 600, marginBottom: 6, color: 'var(--gray-700)' }}>
              Contraseña
            </label>
            <input
              type="password" id="password"
              value={password} onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              style={{
                width: '100%', padding: '10px 14px', fontSize: 14,
                border: '1px solid var(--gray-300)', borderRadius: 8,
                outline: 'none', transition: 'border-color .15s',
                boxSizing: 'border-box',
              }}
            />
          </div>

          {error && (
            <div style={{
              background: '#fef2f2', border: '1px solid #fecaca',
              color: '#991b1b', padding: '10px 14px', borderRadius: 8,
              marginBottom: 16, fontSize: 13,
            }}>{error}</div>
          )}

          <button disabled={submitting} style={{
            width: '100%', padding: '11px 0', fontSize: 15, fontWeight: 600,
            background: submitting ? '#93c5fd' : 'linear-gradient(135deg, #2563eb, #1d4ed8)',
            color: '#fff', border: 'none', borderRadius: 8,
            cursor: submitting ? 'not-allowed' : 'pointer',
            transition: 'opacity .15s',
            boxShadow: '0 4px 14px rgba(37,99,235,.3)',
          }}>
            {submitting ? 'Iniciando sesión...' : 'Iniciar Sesión'}
          </button>
        </form>
      </div>
    </div>
  )
}
