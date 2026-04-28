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
  { value: 'CONSULTATION', label: 'Consultation' },
  { value: 'PRESCRIPTION', label: 'Prescription' },
  { value: 'EMERGENCY', label: 'Emergency' },
  { value: 'LAB', label: 'Lab' },
  { value: 'VACCINE', label: 'Vaccine' },
  { value: 'OTHER', label: 'Other' },
]

export default function Appointments() {
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [doctors, setDoctors] = useState<Doctor[]>([])
  const [patients, setPatients] = useState<Patient[]>([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [errors, setErrors] = useState<FormErrors>({})

  const [form, setForm] = useState<Omit<CreateAppointmentPayload, 'notes'> & { notes: string }>({
    doctor_id: '',
    patient_id: '',
    start_at: '',
    end_at: '',
    appointment_type: 'CONSULTATION',
    reason: '',
    notes: '',
  })

  useEffect(() => {
    Promise.all([
      appointmentsService.list({ page: 1 }).catch(() => ({ data: { results: [] } })),
      doctorsService.list({ page: 1, search: '' }).catch(() => ({ data: { results: [] } })),
      patientsService.list({ page: 1, search: '' }).catch(() => ({ data: { results: [] } })),
    ]).then(([apptRes, docRes, patRes]) => {
      setAppointments((apptRes.data as PaginatedResponse<Appointment>)?.results ?? [])
      setDoctors((docRes.data as PaginatedResponse<Doctor>)?.results ?? [])
      setPatients((patRes.data as PaginatedResponse<Patient>)?.results ?? [])
      setLoading(false)
    })
  }, [])

  const validate = (): boolean => {
    const errs: FormErrors = {}
    if (!form.doctor_id) errs.doctor_id = 'Select a doctor'
    if (!form.patient_id) errs.patient_id = 'Select a patient'
    if (!form.start_at) errs.start_at = 'Start date/time is required'
    if (!form.end_at) errs.end_at = 'End date/time is required'
    if (form.start_at && form.end_at && form.end_at <= form.start_at) {
      errs.end_at = 'End time must be after start time'
    }
    if (!form.reason.trim()) errs.reason = 'Reason is required'
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
      const res = await appointmentsService.create(payload)
      setAppointments((prev) => [res.data as Appointment, ...prev])
      setForm({
        doctor_id: '',
        patient_id: '',
        start_at: '',
        end_at: '',
        appointment_type: 'CONSULTATION',
        reason: '',
        notes: '',
      })
      setErrors({})
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

  const handleCancel = async (id: string) => {
    try {
      await appointmentsService.cancel(id)
      setAppointments((prev) =>
        prev.map((a) => (a.id === id ? { ...a, status: 'CANCELLED' as const } : a))
      )
    } catch {
      // ignore
    }
  }

  const statusColor = (status: string) => {
    switch (status) {
      case 'SCHEDULED': return '#3b82f6'
      case 'IN_PROGRESS': return '#f59e0b'
      case 'COMPLETED': return '#10b981'
      case 'CANCELLED': return '#ef4444'
      case 'NO_SHOW': return '#6b7280'
      default: return '#6b7280'
    }
  }

  if (loading) return <PageContainer title="Appointments"><p>Loading...</p></PageContainer>

  return (
    <PageContainer title="Appointments">
      {/* ── Toolbar ── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <span style={{ color: '#6b7280' }}>
          {appointments.length} appointment{appointments.length !== 1 ? 's' : ''}
        </span>
        <button
          type="button"
          onClick={() => setShowForm(!showForm)}
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
          {showForm ? 'Close' : '+ New Appointment'}
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
          <h3 style={{ marginTop: 0, marginBottom: 16 }}>Create Appointment</h3>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            {/* Doctor */}
            <div>
              <label style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>
                Doctor <span style={{ color: '#ef4444' }}>*</span>
              </label>
              <select
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
                <option value="">Select doctor...</option>
                {doctors.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.first_name} {d.last_name} — {d.specialty_main?.name || 'No specialty'}
                  </option>
                ))}
              </select>
              {errors.doctor_id && <span style={{ color: '#ef4444', fontSize: 12 }}>{errors.doctor_id}</span>}
            </div>

            {/* Patient */}
            <div>
              <label style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>
                Patient <span style={{ color: '#ef4444' }}>*</span>
              </label>
              <select
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
                <option value="">Select patient...</option>
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
              <label style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>
                Start <span style={{ color: '#ef4444' }}>*</span>
              </label>
              <input
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
              <label style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>
                End <span style={{ color: '#ef4444' }}>*</span>
              </label>
              <input
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
              <label style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>
                Type
              </label>
              <select
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
              <label style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>
                Reason <span style={{ color: '#ef4444' }}>*</span>
              </label>
              <input
                type="text"
                placeholder="Reason for visit..."
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
            <label style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>Notes</label>
            <textarea
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
              {submitting ? 'Creating...' : 'Create'}
            </button>
            <button
              type="button"
              onClick={() => { setShowForm(false); setErrors({}) }}
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
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* ── List ── */}
      <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 10, overflow: 'hidden' }}>
        {appointments.length === 0 ? (
          <p style={{ padding: 24, margin: 0, color: '#6b7280', textAlign: 'center' }}>
            No appointments yet. Click <strong>+ New Appointment</strong> to create one.
          </p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
            <thead>
              <tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
                <th style={{ textAlign: 'left', padding: '12px 16px', fontWeight: 600, color: '#374151' }}>Patient</th>
                <th style={{ textAlign: 'left', padding: '12px 16px', fontWeight: 600, color: '#374151' }}>Doctor</th>
                <th style={{ textAlign: 'left', padding: '12px 16px', fontWeight: 600, color: '#374151' }}>Date</th>
                <th style={{ textAlign: 'left', padding: '12px 16px', fontWeight: 600, color: '#374151' }}>Type</th>
                <th style={{ textAlign: 'left', padding: '12px 16px', fontWeight: 600, color: '#374151' }}>Status</th>
                <th style={{ textAlign: 'left', padding: '12px 16px', fontWeight: 600, color: '#374151' }}>Action</th>
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
                    {new Date(a.start_at).toLocaleString()}
                  </td>
                  <td style={{ padding: '12px 16px' }}>{a.appointment_type}</td>
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
                      {a.status}
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    {a.status !== 'CANCELLED' && (
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
                        Cancel
                      </button>
                    )}
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
