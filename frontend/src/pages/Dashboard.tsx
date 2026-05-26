import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { CanAccess } from '../lib/rbac/guards'
import { api } from '../utils/api'

interface Stats {
  total_patients: number
  new_this_month: number
  today_appointments: number
  active_records: number
}

const cardColors = [
  { bg: '#eff6ff', icon: '#3b82f6', border: '#bfdbfe' },
  { bg: '#f0fdf4', icon: '#22c55e', border: '#bbf7d0' },
  { bg: '#fefce8', icon: '#eab308', border: '#fef08a' },
  { bg: '#faf5ff', icon: '#a855f7', border: '#e9d5ff' },
]

export default function Dashboard() {
  const [stats, setStats] = useState<Stats>({
    total_patients: 0,
    new_this_month: 0,
    today_appointments: 0,
    active_records: 0,
  })

  useEffect(() => {
    Promise.all([
      api.get<{ count: number }>('/patients/', { params: { page: 1 } }).catch(() => ({ count: 0 })),
      api.get<{ count: number }>('/appointments/', { params: { page: 1 } }).catch(() => ({ count: 0 })),
      api.get<{ count: number }>('/encounters/encounters/', { params: { page: 1 } }).catch(() => ({ count: 0 })),
    ]).then(([patients, appointments, encounters]) => {
      setStats({
        total_patients: patients?.count ?? 0,
        new_this_month: 0,
        today_appointments: appointments?.count ?? 0,
        active_records: encounters?.count ?? 0,
      })
    }).catch(() => {})
  }, [])

  const statCards = [
    { label: 'Total Pacientes', value: stats.total_patients, icon: '👥' },
    { label: 'Nuevos Este Mes', value: stats.new_this_month, icon: '🆕' },
    { label: 'Citas Hoy', value: stats.today_appointments, icon: '📅' },
    { label: 'Historias Médicas', value: stats.active_records, icon: '📋' },
  ]

  return (
    <div className="animate-fade" style={{ padding: 24 }}>
      {/* Welcome Banner */}
      <div style={{
        background: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #6366f1 100%)',
        borderRadius: 16,
        padding: '28px 32px',
        marginBottom: 24,
        color: '#fff',
        position: 'relative',
        overflow: 'hidden',
        boxShadow: '0 4px 24px rgba(37,99,235,.25)',
      }}>
        {/* Decorative circles */}
        <div style={{
          position: 'absolute', top: -40, right: -20,
          width: 160, height: 160, borderRadius: '50%',
          background: 'rgba(255,255,255,.06)',
        }} />
        <div style={{
          position: 'absolute', bottom: -60, right: 100,
          width: 200, height: 200, borderRadius: '50%',
          background: 'rgba(255,255,255,.04)',
        }} />

        <div style={{ position: 'relative', zIndex: 1 }}>
          <h1 style={{ margin: 0, fontSize: 26, fontWeight: 700, letterSpacing: '-.3px' }}>
            Bienvenido a MediSoft
          </h1>
          <p style={{ margin: '6px 0 20px', fontSize: 15, opacity: .85, fontWeight: 400 }}>
            Soluciones de Gestión Médica y Atención al Paciente
          </p>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            <Link to="/pacientes" style={{
              background: '#fff', color: '#1e40af', border: 'none',
              borderRadius: 8, padding: '10px 20px', fontSize: 14,
              fontWeight: 600, cursor: 'pointer', textDecoration: 'none',
              display: 'inline-flex', alignItems: 'center', gap: 6,
              transition: 'transform .15s',
            }}>
              <span>👥</span> Gestionar Pacientes
            </Link>
            <Link to="/citas" style={{
              background: 'rgba(255,255,255,.15)', color: '#fff',
              border: '1px solid rgba(255,255,255,.25)',
              borderRadius: 8, padding: '10px 20px', fontSize: 14,
              fontWeight: 600, cursor: 'pointer', textDecoration: 'none',
              display: 'inline-flex', alignItems: 'center', gap: 6,
              transition: 'background .15s',
            }}>
              <span>📅</span> Agendar Cita
            </Link>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: 16,
        marginBottom: 28,
      }}>
        {statCards.map((card, i) => (
          <div key={card.label} className="animate-fade" style={{
            background: '#fff',
            borderRadius: 14,
            padding: '20px 24px',
            boxShadow: 'var(--shadow)',
            border: '1px solid var(--gray-200)',
            display: 'flex',
            alignItems: 'center',
            gap: 16,
            animationDelay: `${i * .1}s`,
          }}>
            <div style={{
              width: 48, height: 48, borderRadius: 12,
              background: cardColors[i].bg,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 22,
            }}>
              {card.icon}
            </div>
            <div>
              <div style={{ fontSize: 24, fontWeight: 700, color: 'var(--gray-900)', lineHeight: 1 }}>
                {card.value.toLocaleString()}
              </div>
              <div style={{ fontSize: 13, color: 'var(--gray-500)', marginTop: 4 }}>
                {card.label}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <h2 style={{ fontSize: 18, fontWeight: 600, margin: '0 0 14px' }}>Acciones Rápidas</h2>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: 12,
      }}>
        <QuickAction to="/citas" icon="📅" label="Nueva Cita" desc="Agendar una consulta médica" />
        <QuickAction to="/pacientes" icon="👤" label="Nuevo Paciente" desc="Registrar un paciente" />
        <CanAccess module="users" action="view">
          <QuickAction to="/admin/users" icon="⚙️" label="Gestionar Usuarios" desc="Administrar cuentas del sistema" />
        </CanAccess>
        <QuickAction to="/historial-medico" icon="📋" label="Historial Médico" desc="Consultar expedientes" />
      </div>
    </div>
  )
}

function QuickAction({ to, icon, label, desc }: { to: string; icon: string; label: string; desc: string }) {
  return (
    <Link to={to} style={{
      background: '#fff',
      border: '1px solid var(--gray-200)',
      borderRadius: 12,
      padding: '18px 20px',
      textDecoration: 'none',
      color: 'inherit',
      boxShadow: 'var(--shadow)',
      transition: 'all .15s',
      display: 'flex',
      alignItems: 'center',
      gap: 14,
    }}>
      <div style={{
        width: 44, height: 44, borderRadius: 10,
        background: 'var(--primary-light)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: 20,
      }}>{icon}</div>
      <div>
        <div style={{ fontWeight: 600, fontSize: 14 }}>{label}</div>
        <div style={{ fontSize: 12, color: 'var(--gray-500)', marginTop: 2 }}>{desc}</div>
      </div>
    </Link>
  )
}
