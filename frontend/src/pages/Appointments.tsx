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

// 30-minute time slots for one-click selection (morning + afternoon)
function generateTimeSlots() {
  const slots: { hour: number; minute: number; label: string; endLabel: string }[] = []
  const morning = [8, 9, 10, 11]
  const afternoon = [12, 13, 14, 15, 16, 17]
  for (const h of [...morning, ...afternoon]) {
    for (const m of [0, 30]) {
      const startH = h + Math.floor(m / 60)
      const startM = m % 60
      const end = new Date(2020, 0, 1, startH, startM + 30)
      const endH = end.getHours()
      const endM = end.getMinutes()
      const fmt = (hh: number, mm: number) =>
        `${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')}`
      const period = (hh: number) => (hh < 12 ? 'AM' : 'PM')
      slots.push({
        hour: startH,
        minute: startM,
        label: `${fmt(h % 12 || 12, m)} ${period(h)}`,
        endLabel: `${fmt(endH % 12 || 12, endM)} ${period(endH)}`,
      })
    }
  }
  return slots
}
const TIME_SLOTS = generateTimeSlots()

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

  const setTimeSlot = (hour: number, minute: number) => {
    // Use selected date or today
    const dateStr = form.start_at ? form.start_at.slice(0, 10) : new Date().toISOString().slice(0, 10)
    const start = new Date(`${dateStr}T${String(hour).padStart(2,'0')}:${String(minute).padStart(2,'0')}:00`)
    const end = new Date(start.getTime() + 30 * 60 * 1000)
    setForm({ ...form, start_at: toDatetimeLocal(start), end_at: toDatetimeLocal(end) })
  }

  const setDateOnly = (dateStr: string) => {
    // Keep existing time if set, otherwise default to 8:00-8:30
    if (form.start_at) {
      const timePart = form.start_at.slice(11, 16)
      const endTimePart = form.end_at ? form.end_at.slice(11, 16) : '08:30'
      setForm({
        ...form,
        start_at: `${dateStr}T${timePart}`,
        end_at: `${dateStr}T${endTimePart}`,
      })
    } else {
      setForm({
        ...form,
        start_at: `${dateStr}T08:00`,
        end_at: `${dateStr}T08:30`,
      })
    }
  }

  const dateOnlyValue = form.start_at ? form.start_at.slice(0, 10) : ''

  // Check if a time slot overlaps any existing appointment (excluding the one being edited)
  const isSlotBooked = (slotHour: number, slotMinute: number): boolean => {
    if (!dateOnlyValue) return false
    const slotStart = new Date(`${dateOnlyValue}T${String(slotHour).padStart(2,'0')}:${String(slotMinute).padStart(2,'0')}:00`)
    const slotEnd = new Date(slotStart.getTime() + 30 * 60 * 1000)
    return appointments.some(a => {
      if (editingId && a.id === editingId) return false // don't block own slot when editing
      if (a.status === 'CANCELADA' || a.status === 'NO_ASISTIO') return false
      const aStart = new Date(a.start_at)
      const aEnd = new Date(a.end_at)
      return slotStart < aEnd && slotEnd > aStart // overlap check
    })
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

          {/* ⋙ DATE + TIME BLOCKS ⟀ */}
          <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 10, padding: 20, marginBottom: 16 }}>
            <h4 style={{ margin: '0 0 14px', fontSize: 14, color: '#475569', fontWeight: 600 }}>
              📆 Selección de Fecha y Hora
            </h4>

            {/* Date picker */}
            <div style={{ marginBottom: 16 }}>
              <label style={{ ...labelStyle, marginBottom: 4, display: 'block' }}>Fecha <span style={{ color: '#ef4444' }}>*</span></label>
              <input type="date" value={dateOnlyValue}
                onChange={e => setDateOnly(e.target.value)}
                style={{ ...inputStyle(), width: 220 }} />
            </div>

            {/* Time slot blocks */}
            <div style={{ marginBottom: 4 }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: '#64748b', marginBottom: 8 }}>
                Mañana — clic para seleccionar horario (30 min)
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))', gap: 8, marginBottom: 16 }}>
                {TIME_SLOTS.filter(s => s.hour < 12).map(slot => {
                  const startVal = `${dateOnlyValue || new Date().toISOString().slice(0,10)}T${String(slot.hour).padStart(2,'0')}:${String(slot.minute).padStart(2,'0')}`
                  const isSelected = form.start_at === startVal
                  const booked = isSlotBooked(slot.hour, slot.minute)
                  return (
                    <button key={startVal} type="button"
                      disabled={booked}
                      onClick={() => setTimeSlot(slot.hour, slot.minute)}
                      style={{
                        padding: '10px 12px', borderRadius: 8,
                        border: isSelected ? '2px solid #2563eb' : booked ? '1px solid #e5e7eb' : '1px solid #d1d5db',
                        background: isSelected ? '#eff6ff' : booked ? '#f9fafb' : '#fff',
                        cursor: booked ? 'not-allowed' : 'pointer',
                        textAlign: 'center', transition: 'all .1s',
                        fontWeight: isSelected ? 600 : 400,
                        opacity: booked ? 0.5 : 1,
                      }}>
                      <div style={{ fontSize: 17, fontWeight: 700, color: isSelected ? '#1d4ed8' : booked ? '#9ca3af' : '#1e293b' }}>
                        {slot.label}
                      </div>
                      <div style={{ fontSize: 11, color: booked ? '#9ca3af' : '#64748b', marginTop: 2 }}>
                        {booked ? 'Ocupado' : `a ${slot.endLabel}`}
                      </div>
                    </button>
                  )
                })}
              </div>

              <div style={{ fontSize: 12, fontWeight: 600, color: '#64748b', marginBottom: 8 }}>
                Tarde
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))', gap: 8 }}>
                {TIME_SLOTS.filter(s => s.hour >= 12).map(slot => {
                  const startVal = `${dateOnlyValue || new Date().toISOString().slice(0,10)}T${String(slot.hour).padStart(2,'0')}:${String(slot.minute).padStart(2,'0')}`
                  const isSelected = form.start_at === startVal
                  const booked = isSlotBooked(slot.hour, slot.minute)
                  return (
                    <button key={startVal} type="button"
                      disabled={booked}
                      onClick={() => setTimeSlot(slot.hour, slot.minute)}
                      style={{
                        padding: '10px 12px', borderRadius: 8,
                        border: isSelected ? '2px solid #2563eb' : booked ? '1px solid #e5e7eb' : '1px solid #d1d5db',
                        background: isSelected ? '#eff6ff' : booked ? '#f9fafb' : '#fff',
                        cursor: booked ? 'not-allowed' : 'pointer',
                        textAlign: 'center', transition: 'all .1s',
                        fontWeight: isSelected ? 600 : 400,
                        opacity: booked ? 0.5 : 1,
                      }}>
                      <div style={{ fontSize: 17, fontWeight: 700, color: isSelected ? '#1d4ed8' : booked ? '#9ca3af' : '#1e293b' }}>
                        {slot.label}
                      </div>
                      <div style={{ fontSize: 11, color: booked ? '#9ca3af' : '#64748b', marginTop: 2 }}>
                        {booked ? 'Ocupado' : `a ${slot.endLabel}`}
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>

            {/* Hidden datetime fields kept for form validation/submission */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 16 }}>
              <div>
                <label style={{ ...labelStyle, marginBottom: 4 }}>Inicio <span style={{ color: '#ef4444' }}>*</span></label>
                <input id="start-at" type="datetime-local" value={form.start_at}
                  onChange={e => setForm({ ...form, start_at: e.target.value })}
                  style={inputStyle(errors.start_at)} />
                {errors.start_at && <span style={errStyle}>{errors.start_at}</span>}
              </div>
              <div>
                <label style={{ ...labelStyle, marginBottom: 4 }}>Fin <span style={{ color: '#ef4444' }}>*</span></label>
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
