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
  PaginatedResponse,
} from '../types'

type FormErrors = Record<string, string>

const APPOINTMENT_TYPES: { value: CreateAppointmentPayload['appointment_type']; label: string }[] = [
  { value: 'CONSULTA', label: 'Consulta General' },
  { value: 'CONTROL', label: 'Control Médico' },
  { value: 'EMERGENCIA', label: 'Emergencia' },
  { value: 'SEGUIMIENTO', label: 'Seguimiento' },
]

export default function Appointments() {
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [doctors, setDoctors] = useState<Doctor[]>([])
  const [patients, setPatients] = useState<Patient[]>([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [errors, setErrors] = useState<FormErrors>({})
  const [editingId, setEditingId] = useState<string | null>(null)

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
      appointmentsService.list({ page: 1 }).catch(() => ({ data: { results: [] } })),
      doctorsService.list({ page: 1, search: '' }).catch(() => ({ data: { results: [] } })),
      patientsService.list({ page: 1, search: '' }).catch(() => ({ data: { results: [] } })),
    ]).then(([apptRes, docRes, patRes]) => {
      setAppointments((apptRes as PaginatedResponse<Appointment>)?.results ?? [])
      setDoctors((docRes as PaginatedResponse<Doctor>)?.results ?? [])
      setPatients((patRes as PaginatedResponse<Patient>)?.results ?? [])
      setLoading(false)
    })
  }, [])

  const resetForm = () => {
    setForm({
      doctor_id: '',
      patient_id: '',
      start_at: '',
      end_at: '',
      appointment_type: 'CONSULTA',
      reason: '',
      notes: '',
    })
    setErrors({})
    setEditingId(null)
  }

  const validate = (): boolean => {
    const errs: FormErrors = {}
    if (!form.doctor_id) errs.doctor_id = 'Seleccione un médico'
    if (!form.patient_id) errs.patient_id = 'Seleccione un paciente'
    if (!form.start_at) errs.start_at = 'La fecha y hora de inicio es obligatoria'
    if (!form.end_at) errs.end_at = 'La fecha y hora de fin es obligatoria'
    if (form.start_at && form.end_at && form.end_at <= form.start_at) {
      errs.end_at = 'La hora de fin debe ser posterior a la de inicio'
    }
    if (!form.reason.trim()) errs.reason = 'El motivo es obligatorio'
    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return

    setSubmitting(true)
    try {
      const payload: CreateAppointmentPayload = {
        ...form,
        notes: form.notes || undefined,
      }
      
      let res
      if (editingId) {
        res = await appointmentsService.update(editingId, payload)
      } else {
        res = await appointmentsService.create(payload)
      }
      const created = res as Appointment

      if (editingId) {
        setAppointments((prev) =>
          prev.map((a) => (a.id === editingId ? created : a))
        )
      } else {
        setAppointments((prev) => [created, ...prev])
      }

      resetForm()
      setShowForm(false)
    } catch (err: unknown) {
      const apiErr = err as { response?: { data?: Record<string, string[]> } }
      const detail = apiErr.response?.data
      if (detail) {
        const errs: FormErrors = {}
        for (const [key, msgs] of Object.entries(detail)) {
          errs[key] = msgs[0]
        }
        setErrors(errs)
      }
    } finally {
      setSubmitting(false)
    }
  }

  // Helper to convert UTC datetime string to local timezone for display
  // Returns a value suitable for datetime-local input (YYYY-MM-DDTHH:MM)
  const formatDateTimeForInput = (isoString: string): string => {
    // Parse the ISO string - Date constructor treats 'Z' suffix as UTC
    const date = new Date(isoString)

    // Get the user's local timezone components
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')

    // Return in the format expected by datetime-local input
    return `${year}-${month}-${day}T${hours}:${minutes}`
  }

  const handleEdit = (a: Appointment) => {
    setEditingId(a.id)
    
    // Convert UTC datetime from API to user's local timezone for display
    // This ensures the form shows times in the user's current timezone context
    const startLocal = formatDateTimeForInput(a.start_at)
    const endLocal = formatDateTimeForInput(a.end_at)
    
    setForm({
      doctor_id: a.doctor.id,
      patient_id: a.patient.id,
      start_at: startLocal,
      end_at: endLocal,
      appointment_type: a.appointment_type,
      reason: a.reason || '',
      notes: a.notes || '',
    })
    setErrors({})
    setShowForm(true)
  }

  const handleDelete = async (id: string) => {
    if (!window.confirm('¿Está seguro de eliminar esta cita?')) return
    try {
      await appointmentsService.delete(id)
      setAppointments((prev) => prev.filter((a) => a.id !== id))
    } catch {
      // ignore
    }
  }

  const handleCancel = async (id: string) => {
    if (!window.confirm('¿Cancelar esta cita?')) return
    try {
      await appointmentsService.cancel(id)
      setAppointments((prev) =>
        prev.map((a) => (a.id === id ? { ...a, status: 'CANCELADA' as const } : a))
      )
    } catch {
      // ignore
    }
  }

  const statusColor = (status: string) => {
    switch (status) {
      case 'PROGRAMADA': return '#3b82f6'
      case 'CONFIRMADA': return '#8b5cf6'
      case 'EN_CURSO': return '#f59e0b'
      case 'COMPLETADA': return '#10b981'
      case 'CANCELADA': return '#ef4444'
      case 'NO_ASISTIO': return '#6b7280'
      default: return '#6b7280'
    }
  }

  const statusLabel = (status: string) => {
    const labels: Record<string, string> = {
      PROGRAMADA: 'Programada',
      CONFIRMADA: 'Confirmada',
      EN_CURSO: 'En curso',
      COMPLETADA: 'Completada',
      CANCELADA: 'Cancelada',
      NO_ASISTIO: 'No asistió',
    }
    return labels[status] || status
  }

  if (loading) return <PageContainer title="Citas"><p>Cargando...</p></PageContainer>

  return (
    <PageContainer title="Citas">
      {/* ── Toolbar ── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <span style={{ color: '#6b7280' }}>
          {appointments.length} cita{appointments.length !== 1 ? 's' : ''}
        </span>
        <button
          type="button"
          onClick={() => {
            if (showForm) {
              setShowForm(false)
              resetForm()
            } else {
              setShowForm(true)
            }
          }}
          style={{
            background: '#3b82f6',
            color: '#fff',
            border: 'none',
            borderRadius: 6,
            padding: '8px 16px',
            cursor: 'pointer',
            fontWeight: 500,
          }}
        >
          {showForm ? 'Cerrar' : '+ Nueva Cita'}
        </button>
      </div>

      {/* ── Form ── */}
      {showForm && (
        <form
          onSubmit={handleSubmit}
          style={{
            background: '#fff',
            border: '1px solid #e5e7eb',
            borderRadius: 10,
            padding: 20,
            marginBottom: 20,
          }}
        >
          <h3 style={{ marginTop: 0, marginBottom: 16 }}>
            {editingId ? 'Editar Cita' : 'Crear Cita'}
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            {/* Doctor */}
            <div>
              <label htmlFor="doctor-select" style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>
                Médico <span style={{ color: '#ef4444' }}>*</span>
              </label>
              <select
                id="doctor-select"
                value={form.doctor_id}
                onChange={(e) => setForm({ ...form, doctor_id: e.target.value })}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  borderRadius: 6,
                  border: `1px solid ${errors.doctor_id ? '#ef4444' : '#d1d5db'}`,
                  fontSize: 14,
                }}
              >
                <option value="">Seleccione médico...</option>
                {doctors.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.first_name} {d.last_name} — {d.specialty_main?.name || 'Sin especialidad'}
                  </option>
                ))}
              </select>
              {errors.doctor_id && <span style={{ color: '#ef4444', fontSize: 12 }}>{errors.doctor_id}</span>}
            </div>

            {/* Patient */}
            <div>
              <label htmlFor="patient-select" style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>
                Paciente <span style={{ color: '#ef4444' }}>*</span>
              </label>
              <select
                id="patient-select"
                value={form.patient_id}
                onChange={(e) => setForm({ ...form, patient_id: e.target.value })}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  borderRadius: 6,
                  border: `1px solid ${errors.patient_id ? '#ef4444' : '#d1d5db'}`,
                  fontSize: 14,
                }}
              >
                <option value="">Seleccione paciente...</option>
                {patients.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.first_name} {p.last_name} — {p.cedula}
                  </option>
                ))}
              </select>
              {errors.patient_id && <span style={{ color: '#ef4444', fontSize: 12 }}>{errors.patient_id}</span>}
            </div>

            {/* Start */}
            <div>
              <label htmlFor="start-at" style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>
                Inicio <span style={{ color: '#ef4444' }}>*</span>
              </label>
              <input
                id="start-at"
                type="datetime-local"
                value={form.start_at}
                onChange={(e) => setForm({ ...form, start_at: e.target.value })}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  borderRadius: 6,
                  border: `1px solid ${errors.start_at ? '#ef4444' : '#d1d5db'}`,
                  fontSize: 14,
                }}
              />
              {errors.start_at && <span style={{ color: '#ef4444', fontSize: 12 }}>{errors.start_at}</span>}
            </div>

            {/* End */}
            <div>
              <label htmlFor="end-at" style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>
                Fin <span style={{ color: '#ef4444' }}>*</span>
              </label>
              <input
                id="end-at"
                type="datetime-local"
                value={form.end_at}
                onChange={(e) => setForm({ ...form, end_at: e.target.value })}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  borderRadius: 6,
                  border: `1px solid ${errors.end_at ? '#ef4444' : '#d1d5db'}`,
                  fontSize: 14,
                }}
              />
              {errors.end_at && <span style={{ color: '#ef4444', fontSize: 12 }}>{errors.end_at}</span>}
            </div>

            {/* Type */}
            <div>
              <label htmlFor="appointment-type" style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>
                Tipo
              </label>
              <select
                id="appointment-type"
                value={form.appointment_type}
                onChange={(e) => setForm({ ...form, appointment_type: e.target.value as CreateAppointmentPayload['appointment_type'] })}
                style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid #d1d5db', fontSize: 14 }}
              >
                {APPOINTMENT_TYPES.map((t) => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </select>
            </div>

            {/* Reason */}
            <div>
              <label htmlFor="appointment-reason" style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>
                Motivo <span style={{ color: '#ef4444' }}>*</span>
              </label>
              <input
                id="appointment-reason"
                type="text"
                placeholder="Motivo de la visita..."
                value={form.reason}
                onChange={(e) => setForm({ ...form, reason: e.target.value })}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  borderRadius: 6,
                  border: `1px solid ${errors.reason ? '#ef4444' : '#d1d5db'}`,
                  fontSize: 14,
                  boxSizing: 'border-box',
                }}
              />
              {errors.reason && <span style={{ color: '#ef4444', fontSize: 12 }}>{errors.reason}</span>}
            </div>
          </div>

          {/* Notes */}
          <div style={{ marginTop: 16 }}>
            <label htmlFor="appointment-notes" style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>Notas</label>
            <textarea
              id="appointment-notes"
              value={form.notes}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
              rows={2}
              style={{
                width: '100%',
                padding: '8px 12px',
                borderRadius: 6,
                border: '1px solid #d1d5db',
                fontSize: 14,
                resize: 'vertical',
                boxSizing: 'border-box',
              }}
            />
          </div>

          {/* Submit */}
          <div style={{ marginTop: 16, display: 'flex', gap: 8 }}>
            <button
              type="submit"
              disabled={submitting}
              style={{
                background: submitting ? '#93c5fd' : '#3b82f6',
                color: '#fff',
                border: 'none',
                borderRadius: 6,
                padding: '8px 20px',
                cursor: submitting ? 'not-allowed' : 'pointer',
                fontWeight: 500,
              }}
            >
              {submitting ? (editingId ? 'Guardando...' : 'Creando...') : (editingId ? 'Guardar Cambios' : 'Crear')}
            </button>
            <button
              type="button"
              onClick={() => { setShowForm(false); resetForm() }}
              style={{
                background: '#f3f4f6',
                color: '#374151',
                border: '1px solid #d1d5db',
                borderRadius: 6,
                padding: '8px 20px',
                cursor: 'pointer',
                fontWeight: 500,
              }}
            >
              Cancelar
            </button>
          </div>
        </form>
      )}

      {/* ── List ── */}
      <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 10, overflow: 'hidden' }}>
        {appointments.length === 0 ? (
          <p style={{ padding: 24, margin: 0, color: '#6b7280', textAlign: 'center' }}>
            No hay citas. Haga clic en <strong>+ Nueva Cita</strong> para crear una.
          </p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
            <thead>
              <tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
                <th style={{ textAlign: 'left', padding: '12px 16px', fontWeight: 600, color: '#374151' }}>Paciente</th>
                <th style={{ textAlign: 'left', padding: '12px 16px', fontWeight: 600, color: '#374151' }}>Médico</th>
                <th style={{ textAlign: 'left', padding: '12px 16px', fontWeight: 600, color: '#374151' }}>Fecha</th>
                <th style={{ textAlign: 'left', padding: '12px 16px', fontWeight: 600, color: '#374151' }}>Tipo</th>
                <th style={{ textAlign: 'left', padding: '12px 16px', fontWeight: 600, color: '#374151' }}>Estado</th>
                <th style={{ textAlign: 'left', padding: '12px 16px', fontWeight: 600, color: '#374151' }}>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {appointments.map((a) => (
                <tr key={a.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                  <td style={{ padding: '12px 16px' }}>
                    {a.patient.first_name} {a.patient.last_name}
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    {a.doctor.first_name} {a.doctor.last_name}
                  </td>
                  <td style={{ padding: '12px 16px', whiteSpace: 'nowrap' }}>
                    {new Date(a.start_at).toLocaleString('es-DO')}
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    {APPOINTMENT_TYPES.find((t) => t.value === a.appointment_type)?.label || a.appointment_type}
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <span style={{
                      display: 'inline-block',
                      padding: '2px 10px',
                      borderRadius: 9999,
                      fontSize: 12,
                      fontWeight: 500,
                      color: '#fff',
                      background: statusColor(a.status),
                    }}>
                      {statusLabel(a.status)}
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <div style={{ display: 'flex', gap: 6 }}>
                      {a.status !== 'CANCELADA' && (
                        <button
                          onClick={() => handleCancel(a.id)}
                          style={{
                            background: 'none',
                            border: '1px solid #ef4444',
                            color: '#ef4444',
                            borderRadius: 4,
                            padding: '4px 10px',
                            cursor: 'pointer',
                            fontSize: 12,
                          }}
                        >
                          Cancelar
                        </button>
                      )}
                      <button
                        onClick={() => handleEdit(a)}
                        style={{
                          background: 'none',
                          border: '1px solid #3b82f6',
                          color: '#3b82f6',
                          borderRadius: 4,
                          padding: '4px 10px',
                          cursor: 'pointer',
                          fontSize: 12,
                        }}
                      >
                        Editar
                      </button>
                      <button
                        onClick={() => handleDelete(a.id)}
                        style={{
                          background: 'none',
                          border: '1px solid #6b7280',
                          color: '#6b7280',
                          borderRadius: 4,
                          padding: '4px 10px',
                          cursor: 'pointer',
                          fontSize: 12,
                        }}
                      >
                        Eliminar
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </PageContainer>
  )
}
