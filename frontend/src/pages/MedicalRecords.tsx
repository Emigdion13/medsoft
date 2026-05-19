import React, { useEffect, useState } from 'react'
import { PageContainer } from '../components/common/SharedComponents'
import { api } from '../utils/api'

interface Encounter {
  id: string
  patient: { id: string; first_name: string; last_name: string; cedula: string }
  doctor: { id: string; first_name: string; last_name: string }
  appointment: { id: string; start_at: string; reason: string } | null
  encounter_type: string
  status: string
  start_at: string
  end_at: string | null
  chief_complaint: string | null
  room_number: string | null
  bed_number: string | null
  created_by_name: string | null
  created_at: string
}

interface PaginatedEncounter {
  count: number
  next: string | null
  previous: string | null
  results: Encounter[]
}

const ENCOUNTER_TYPES: Record<string, string> = {
  AMBULATORIO: '🏥 Ambulatorio',
  INTERNAMIENTO: '🛏️ Internamiento',
  EMERGENCIA: '🚨 Emergencia',
  TELECONSULTA: '📞 Teleconsulta',
}

const ENCOUNTER_STATUS: Record<string, { label: string; color: string; bg: string }> = {
  ABIERTO: { label: 'Abierto', color: '#b45309', bg: '#fef3c7' },
  CERRADO: { label: 'Cerrado', color: '#047857', bg: '#d1fae5' },
  CANCELADO: { label: 'Cancelado', color: '#b91c1c', bg: '#fee2e2' },
}

export default function MedicalRecords() {
  const [encounters, setEncounters] = useState<Encounter[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [error, setError] = useState<string | null>(null)

  const load = async (searchTerm?: string) => {
    try {
      setError(null)
      const params: Record<string, string | number> = { page: 1 }
      if (searchTerm) params.search = searchTerm
      const data = await api.get<PaginatedEncounter>('/encounters/encounters/', { params })
      setEncounters(data?.results ?? [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar historial')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { void load() }, [])

  if (loading) return <PageContainer title="Historial Médico"><p style={{ color: '#6b7280' }}>Cargando...</p></PageContainer>

  return (
    <PageContainer title="Historial Médico">
      {/* Toolbar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16, gap: 12, flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <input type="text" placeholder="Buscar por nombre de paciente..."
            value={search}
            onChange={e => { setSearch(e.target.value); load(e.target.value) }}
            style={{ padding: '8px 12px', borderRadius: 6, border: '1px solid #d1d5db', fontSize: 14, width: 280 }} />
          <span style={{ color: '#6b7280', fontSize: 13 }}>
            {encounters.length} encuentro{encounters.length !== 1 ? 's' : ''}
          </span>
        </div>
      </div>

      {error && (
        <div style={{ background: '#fef2f2', border: '1px solid #fecaca', color: '#991b1b', padding: '12px 16px', borderRadius: 8, marginBottom: 16 }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* List */}
      <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, overflow: 'hidden' }}>
        {encounters.length === 0 ? (
          <div style={{ padding: 48, textAlign: 'center' }}>
            <div style={{ fontSize: 40, marginBottom: 8 }}>📋</div>
            <p style={{ margin: 0, color: '#6b7280', fontSize: 15 }}>
              No hay encuentros médicos registrados. Los encuentros se crean al iniciar una consulta desde una cita.
            </p>
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
            <thead>
              <tr style={{ background: '#f8fafc', borderBottom: '2px solid #e5e7eb' }}>
                <th style={thStyle}>Paciente</th>
                <th style={thStyle}>Médico</th>
                <th style={thStyle}>Tipo</th>
                <th style={thStyle}>Inicio</th>
                <th style={thStyle}>Estado</th>
                <th style={thStyle}>Motivo</th>
              </tr>
            </thead>
            <tbody>
              {encounters.map(e => {
                const st = ENCOUNTER_STATUS[e.status] || { label: e.status, color: '#6b7280', bg: '#f3f4f6' }
                return (
                  <tr key={e.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                    <td style={{ padding: '12px 16px', fontWeight: 500 }}>
                      {e.patient?.first_name} {e.patient?.last_name}
                      <br /><span style={{ fontSize: 12, color: '#9ca3af' }}>{e.patient?.cedula}</span>
                    </td>
                    <td style={{ padding: '12px 16px', color: '#475569' }}>
                      Dr. {e.doctor?.first_name} {e.doctor?.last_name}
                    </td>
                    <td style={{ padding: '12px 16px', fontSize: 13 }}>
                      {ENCOUNTER_TYPES[e.encounter_type] || e.encounter_type}
                    </td>
                    <td style={{ padding: '12px 16px', whiteSpace: 'nowrap', fontSize: 13, color: '#475569' }}>
                      {new Date(e.start_at).toLocaleString('es-DO', {
                        year: 'numeric', month: '2-digit', day: '2-digit',
                        hour: '2-digit', minute: '2-digit',
                      })}
                    </td>
                    <td style={{ padding: '12px 16px' }}>
                      <span style={{ display: 'inline-block', padding: '3px 12px', borderRadius: 20, fontSize: 12, fontWeight: 600, color: st.color, background: st.bg }}>
                        {st.label}
                      </span>
                    </td>
                    <td style={{ padding: '12px 16px', color: '#6b7280', fontSize: 13, maxWidth: 250, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {e.chief_complaint || e.appointment?.reason || '—'}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>
    </PageContainer>
  )
}

const thStyle: React.CSSProperties = {
  textAlign: 'left', padding: '12px 16px', fontWeight: 600, color: '#475569',
  fontSize: 12, textTransform: 'uppercase', letterSpacing: '0.05em',
}
