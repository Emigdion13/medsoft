import React, { useEffect, useState } from 'react'
import { PageContainer } from '../components/common/SharedComponents'
import {
  appointmentsService,
  doctorsService,
  patientsService,
} from '../services/resourceServices'
import type {
  Appointment,
  CreateAppointmentPayload,
  Doctor,
  Patient,
} from '../types'

type FormErrors = Record<string, string>

const APPOINTMENT_TYPES: { value: CreateAppointmentPayload['appointment_type']; label: string; icon: string }[] = [
  { value: 'CONSULTA', label: 'Consulta General', icon: '🩺' },
  { value: 'CONTROL', label: 'Control Médico', icon: '📊' },
  { value: 'EMERGENCIA', label: 'Emergencia', icon: '⚡' },
  { value: 'SEGUIMIENTO', label: 'Seguimiento', icon: '📅' },
]

const STATUS_CONFIG: Record<string, { color: string; bg: string; label: string }> = {
  PROGRAMADA: { color: '#1d4ed8', bg: '#dbeafe', label: 'Programada' },
  CONFIRMADA: { color: '#047857', bg: '#d1fae5', label: 'Confirmada' },
  EN_CURSO: { color: '#b45309', bg: '#fef3c7', label: 'En curso' },
  COMPLETADA: { color: '#047857', bg: '#d1fae5', label: 'Completada' },
  CANCELADA: { color: '#b91c1c', bg: '#fee2e2', label: 'Cancelada' },
  NO_ASISTIO: { color: '#374151', bg: '#e5e7eb', label: 'No asistió' },
}

// Quick time slots for one-click selection
const TIME_PRESETS = [
  { label: '08:00 AM', hour: 8 },
  { label: '09:00 AM', hour: 9 },
  { label: '10:00 AM', hour: 10 },
  { label: '11:00 AM', hour: 11 },
  { label: '02:00 PM', hour: 14 },
  { label: '03:00 PM', hour: 15 },
  { label: '04:00 PM', hour: 16 },
]

function toDatetimeLocal(date: Date): string {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  const h = String(date.getHours()).padStart(2, '0')
  const min = String(date.getMinutes()).padStart(2, '0')
  return `${y}-${m}-${d}T${h}:${min}`
}

function fromDatetimeLocal(val: string): Date | null {
  if (!val) return null
  return new Date(val)
}

export default function Appointments() {
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [doctors, setDoctors] = useState<Doctor[]>([])
  const [patients, setPatients] = useState<Patient[]>([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [errors, setErrors] = useState<FormErrors>({})
  const [editingId, setEditingId] = useState<string | null>(null)
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [initError, setInitError] = useState<string | null>(null)

  const [form, setForm] = useState<Omit<CreateAppointmentPayload, 'notes'> & { notes: string }>({
    doctor_id: '',
    patient_id: '',
    start_at: '',
    end_at: '',
    appointment_type: 'CONSULTA',
    reason: '',
    notes: '',
  })

  useEffect(() => {
    Promise.all([
      appointmentsService.list({ page: 1 }),
      doctorsService.list({ page: 1, search: '' }),
      patientsService.list({ page: 1, search: '' }),
    ])
      .then(([apptRes, docRes, patRes]) => {
        setAppointments(apptRes.results ?? [])
        setDoctors(docRes.results ?? [])
        setPatients(patRes.results ?? [])
        setLoading(false)
        setInitError(null)
      })
      .catch((err) => {
        console.error('Failed to load initial data:', err)
        setInitError(err instanceof Error ? err.message : 'Error al cargar los datos')
        setAppointments([]); setDoctors([]); setPatients([])
        setLoading(false)
      })
  }, [])

  const resetForm = () => {
    setForm({ doctor_id: '', patient_id: '', start_at: '', end_at: '', appointment_type: 'CONSULTA', reason: '', notes: '' })
    setErrors({})
    setEditingId(null)
    setShowForm(false)
  }

  const validate = (): boolean => {
    const errs: FormErrors = {}
    if (!form.doctor_id) errs.doctor_id = 'Seleccione un médico'
    if (!form.patient_id) errs.patient_id = 'Seleccione un paciente'
    if (!form.start_at) errs.start_at = 'La fecha y hora de inicio es obligatoria'
    if (!form.end_at) errs.end_at = 'La fecha y hora de fin es obligatoria'
    if (form.start_at && form.end_at && form.end_at <= form.start_at) errs.end_at = 'La hora de fin debe ser posterior a la de inicio'
    if (!form.reason.trim()) errs.reason = 'El motivo es obligatorio'
    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return
    setSubmitting(true)
    try {
      const payload: CreateAppointmentPayload = { ...form, notes: form.notes || undefined }
      let res
      if (editingId) res = await appointmentsService.update(editingId, payload)
      else res = await appointmentsService.create(payload)
      const created = res as Appointment
      if (editingId) setAppointments(prev => prev.map(a => a.id === editingId ? created : a))
      else setAppointments(prev => [created, ...prev])
      resetForm()
    } catch (err: unknown) {
      const apiErr = err as { response?: { data?: Record<string, string[]> } }
      if (apiErr.response?.data) {
        const errs: FormErrors = {}
        for (const [key, msgs] of Object.entries(apiErr.response.data)) errs[key] = msgs[0]
        setErrors(errs)
      }
    } finally { setSubmitting(false) }
  }

  const handleEdit = (a: Appointment) => {
    setEditingId(a.id)
    setForm({
      doctor_id: a.doctor.id,
      patient_id: a.patient.id,
      start_at: new Date(a.start_at).toISOString().slice(0, 16),
      end_at: new Date(a.end_at).toISOString().slice(0, 16),
      appointment_type: a.appointment_type,
      reason: a.reason || '',
      notes: a.notes || '',
    })
    setErrors({})
    setShowForm(true)
  }

  const handleDelete = async (id: string) => {
    if (!window.confirm('¿Está seguro de eliminar esta cita?')) return
    try { await appointmentsService.delete(id); setAppointments(prev => prev.filter(a => a.id !== id)) } catch {}
  }

  const handleCancel = async (id: string) => {
    if (!window.confirm('¿Cancelar esta cita?')) return
    try { await appointmentsService.cancel(id); setAppointments(prev => prev.map(a => a.id === id ? { ...a, status: 'CANCELADA' as const } : a)) } catch {}
  }

  const setTimePreset = (hour: number) => {
    const today = new Date()
    const start = new Date(today.getFullYear(), today.getMonth(), today.getDate(), hour, 0, 0)
    const end = new Date(start.getTime() + 60 * 60 * 1000)
    setForm({ ...form, start_at: toDatetimeLocal(start), end_at: toDatetimeLocal(end) })
  }

  const filtered = filterStatus === 'all' ? appointments : appointments.filter(a => a.status === filterStatus)

  if (loading) return <PageContainer title="Citas"><p style={{ color: '#6b7280', padding: 24 }}>Cargando...</p></PageContainer>

  return (
    <PageContainer title="Citas">
      {/* ── Toolbar ── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, flexWrap: 'wrap', gap: 8 }}>
        <div style={{ display: 'flex', gap: 6, alignItems: 'center', flexWrap: 'wrap' }}>
          <span style={{ fontWeight: 600, fontSize: 14, color: '#374151' }}>{appointments.length} cita{appointments.length !== 1 ? 's' : ''}</span>
          {['all', 'PROGRAMADA', 'CONFIRMADA', 'COMPLETADA', 'CANCELADA'].map(s => (
            <button key={s} type="button" onClick={() => setFilterStatus(s)}
              style={{
                padding: '4px 12px', borderRadius: 20, border: filterStatus === s ? '2px solid #2563eb' : '1px solid #d1d5db',
                background: filterStatus === s ? '#eff6ff' : '#fff', color: filterStatus === s ? '#1d4ed8' : '#6b7280',
                fontSize: 12, fontWeight: filterStatus === s ? 600 : 400, cursor: 'pointer',
              }}>
              {s === 'all' ? 'Todas' : STATUS_CONFIG[s]?.label || s}
            </button>
          ))}
        </div>
        <button type="button" onClick={() => showForm ? resetForm() : setShowForm(true)}
          style={{ background: '#2563eb', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 18px', cursor: 'pointer', fontWeight: 600, fontSize: 14 }}>
          {showForm ? '✕ Cerrar' : '+ Nueva Cita'}
        </button>
      </div>

      {/* ── Form ── */}
      {showForm && (
        <form onSubmit={handleSubmit} style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, padding: 24, marginBottom: 20, boxShadow: '0 4px 16px rgba(0,0,0,0.06)' }}>
          <h3 style={{ margin: '0 0 20px 0', fontSize: 18, color: '#1f2937' }}>📅 {editingId ? 'Editar Cita' : 'Crear Cita'}</h3>

          {/* Doctor + Patient row */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
            <div>
              <label style={labelStyle}>Médico <span style={{ color: '#ef4444' }}>*</span></label>
              <select value={form.doctor_id} onChange={e => setForm({ ...form, doctor_id: e.target.value })}
                style={selectStyle(errors.doctor_id)}>
                <option value="">Seleccione médico...</option>
                {doctors.map(d => <option key={d.id} value={d.id}>{d.first_name} {d.last_name} — {d.specialty_main?.name || 'Sin especialidad'}</option>)}
              </select>
              {errors.doctor_id && <span style={errStyle}>{errors.doctor_id}</span>}
            </div>
            <div>
              <label style={labelStyle}>Paciente <span style={{ color: '#ef4444' }}>*</span></label>
              <select value={form.patient_id} onChange={e => setForm({ ...form, patient_id: e.target.value })}
                style={selectStyle(errors.patient_id)}>
                <option value="">Seleccione paciente...</option>
                {patients.map(p => <option key={p.id} value={p.id}>{p.first_name} {p.last_name} — {p.cedula}</option>)}
              </select>
              {errors.patient_id && <span style={errStyle}>{errors.patient_id}</span>}
            </div>
          </div>

          {/* ⋙ DATE/TIME PICKERS ⟀ */}
          <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 10, padding: 20, marginBottom: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <h4 style={{ margin: 0, fontSize: 14, color: '#475569', fontWeight: 600 }}>📆 Selección de Fecha y Hora</h4>
              <div style={{ display: 'flex', gap: 4 }}>
                {TIME_PRESETS.map(t => (
                  <button key={t.hour} type="button" onClick={() => setTimePreset(t.hour)}
                    style={{ padding: '4px 10px', borderRadius: 6, border: '1px solid #cbd5e1', background: '#fff', color: '#475569', fontSize: 11, cursor: 'pointer', fontWeight: 500, whiteSpace: 'nowrap' }}>
                    {t.label}
                  </button>
                ))}
              </div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div>
                <label style={{ ...labelStyle, marginBottom: 4 }}>Fecha y hora de inicio <span style={{ color: '#ef4444' }}>*</span></label>
                <input id="start-at" type="datetime-local" value={form.start_at}
                  onChange={e => setForm({ ...form, start_at: e.target.value })}
                  style={inputStyle(errors.start_at)} />
                {errors.start_at && <span style={errStyle}>{errors.start_at}</span>}
              </div>
              <div>
                <label style={{ ...labelStyle, marginBottom: 4 }}>Fecha y hora de fin <span style={{ color: '#ef4444' }}>*</span></label>
                <input id="end-at" type="datetime-local" value={form.end_at}
                  onChange={e => setForm({ ...form, end_at: e.target.value })}
                  style={inputStyle(errors.end_at)} />
                {errors.end_at && <span style={errStyle}>{errors.end_at}</span>}
              </div>
            </div>
          </div>

          {/* Type + Reason row */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
            <div>
              <label style={labelStyle}>Tipo de cita</label>
              <select value={form.appointment_type} onChange={e => setForm({ ...form, appointment_type: e.target.value as CreateAppointmentPayload['appointment_type'] })}
                style={selectStyle()}>
                {APPOINTMENT_TYPES.map(t => <option key={t.value} value={t.value}>{t.icon} {t.label}</option>)}
              </select>
            </div>
            <div>
              <label style={labelStyle}>Motivo <span style={{ color: '#ef4444' }}>*</span></label>
              <input type="text" placeholder="Motivo de la visita..." value={form.reason}
                onChange={e => setForm({ ...form, reason: e.target.value })}
                style={inputStyle(errors.reason)} />
              {errors.reason && <span style={errStyle}>{errors.reason}</span>}
            </div>
          </div>

          {/* Notes */}
          <div style={{ marginBottom: 16 }}>
            <label style={labelStyle}>Notas (opcional)</label>
            <textarea value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} rows={2}
              placeholder="Observaciones adicionales..."
              style={{ ...textareaStyle, width: '100%', boxSizing: 'border-box' }} />
          </div>

          {initError && (
            <div style={{ background: '#fef2f2', border: '1px solid #fecaca', color: '#991b1b', padding: '10px 14px', borderRadius: 8, marginBottom: 16, fontSize: 13 }}>
              <strong>Error:</strong> {initError}
            </div>
          )}

          <div style={{ display: 'flex', gap: 8 }}>
            <button type="submit" disabled={submitting}
              style={{ background: submitting ? '#93c5fd' : '#2563eb', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 24px', cursor: submitting ? 'not-allowed' : 'pointer', fontWeight: 600, fontSize: 14 }}>
              {submitting ? (editingId ? 'Guardando...' : 'Creando...') : (editingId ? 'Guardar Cambios' : 'Crear')}
            </button>
            <button type="button" onClick={resetForm}
              style={{ background: '#f9fafb', color: '#374151', border: '1px solid #d1d5db', borderRadius: 8, padding: '10px 20px', cursor: 'pointer', fontWeight: 500, fontSize: 14 }}>
              Cerrar
            </button>
          </div>
        </form>
      )}

      {/* ── List ── */}
      <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
        {filtered.length === 0 ? (
          <div style={{ padding: 48, textAlign: 'center' }}>
            <div style={{ fontSize: 40, marginBottom: 8 }}>📋</div>
            <p style={{ margin: 0, color: '#6b7280', fontSize: 15 }}>
              {appointments.length === 0 ? <>No hay citas. Haga clic en <strong>+ Nueva Cita</strong> para crear una.</> : 'No hay citas con el filtro seleccionado.'}
            </p>
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
            <thead>
              <tr style={{ background: '#f8fafc', borderBottom: '2px solid #e5e7eb' }}>
                <th style={thStyle}>Paciente</th>
                <th style={thStyle}>Médico</th>
                <th style={thStyle}>Inicio</th>
                <th style={thStyle}>Fin</th>
                <th style={thStyle}>Tipo</th>
                <th style={thStyle}>Estado</th>
                <th style={thStyle}>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(a => {
                const st = STATUS_CONFIG[a.status] || { color: '#6b7280', bg: '#f3f4f6', label: a.status }
                return (
                  <tr key={a.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                    <td style={{ padding: '12px 16px', fontWeight: 500 }}>{a.patient.first_name} {a.patient.last_name}</td>
                    <td style={{ padding: '12px 16px', color: '#475569' }}>{a.doctor.first_name} {a.doctor.last_name}</td>
                    <td style={{ padding: '12px 16px', whiteSpace: 'nowrap', fontSize: 13, color: '#475569' }}>
                      {new Date(a.start_at).toLocaleString('es-DO', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td style={{ padding: '12px 16px', whiteSpace: 'nowrap', fontSize: 13, color: '#64748b' }}>
                      {new Date(a.end_at).toLocaleString('es-DO', { hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td style={{ padding: '12px 16px', fontSize: 13 }}>
                      {APPOINTMENT_TYPES.find(t => t.value === a.appointment_type)?.label || a.appointment_type}
                    </td>
                    <td style={{ padding: '12px 16px' }}>
                      <span style={{ display: 'inline-block', padding: '3px 12px', borderRadius: 20, fontSize: 12, fontWeight: 600, color: st.color, background: st.bg }}>
                        {st.label}
                      </span>
                    </td>
                    <td style={{ padding: '12px 16px' }}>
                      <div style={{ display: 'flex', gap: 4 }}>
                        {a.status !== 'CANCELADA' && (
                          <button onClick={() => handleCancel(a.id)}
                            style={actionBtnStyle('#ef4444')}>Cancelar</button>
                        )}
                        <button onClick={() => handleEdit(a)}
                          style={actionBtnStyle('#2563eb')}>Editar</button>
                        <button onClick={() => handleDelete(a.id)}
                          style={actionBtnStyle('#6b7280')}>Eliminar</button>
                      </div>
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

// ── styles ──

const labelStyle: React.CSSProperties = { display: 'block', marginBottom: 4, fontWeight: 600, fontSize: 13, color: '#374151' }
const errStyle: React.CSSProperties = { color: '#ef4444', fontSize: 12, marginTop: 2, display: 'block' }
const thStyle: React.CSSProperties = { textAlign: 'left', padding: '12px 16px', fontWeight: 600, color: '#475569', fontSize: 12, textTransform: 'uppercase', letterSpacing: '0.05em' }

const inputStyle = (err?: string): React.CSSProperties => ({
  width: '100%', padding: '10px 14px', borderRadius: 8, border: `2px solid ${err ? '#fca5a5' : '#e2e8f0'}`,
  fontSize: 14, boxSizing: 'border-box', background: '#fff', outline: 'none',
  transition: 'border-color 0.15s',
})
const selectStyle = (err?: string): React.CSSProperties => ({
  width: '100%', padding: '10px 14px', borderRadius: 8, border: `2px solid ${err ? '#fca5a5' : '#e2e8f0'}`,
  fontSize: 14, boxSizing: 'border-box', background: '#fff', outline: 'none',
})
const textareaStyle: React.CSSProperties = { ...inputStyle(), resize: 'vertical' }
const actionBtnStyle = (color: string): React.CSSProperties => ({
  background: 'none', border: `1px solid ${color}`, color, borderRadius: 6, padding: '4px 12px', cursor: 'pointer', fontSize: 12, fontWeight: 500,
})
