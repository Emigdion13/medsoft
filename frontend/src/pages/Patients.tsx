import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { PageContainer } from '../components/common/SharedComponents'
import { patientsService } from '../services/resourceServices'
import type { Patient } from '../types'

type FormErrors = Record<string, string>

interface PatientFormData {
  first_name: string; last_name: string; identity_type: string
  cedula: string; passport_number: string; birth_date: string
  sex: string; nationality: string; phone_primary: string
  phone_secondary: string; email: string; address: string
  province: string; municipality: string; blood_type: string
  allergies: string; chronic_conditions: string
  emergency_contact_name: string; emergency_contact_phone: string
  emergency_contact_relation: string; ars_provider: string
  ars_affiliation_number: string; status: string
}

const emptyForm: PatientFormData = {
  first_name: '', last_name: '', identity_type: 'CEDULA', cedula: '',
  passport_number: '', birth_date: '', sex: 'F', nationality: 'DOMINICANA',
  phone_primary: '', phone_secondary: '', email: '', address: '',
  province: '', municipality: '', blood_type: '', allergies: '',
  chronic_conditions: '', emergency_contact_name: '', emergency_contact_phone: '',
  emergency_contact_relation: '', ars_provider: '', ars_affiliation_number: '',
  status: 'ACTIVO',
}

const sColor = (s: string) => ({ ACTIVO: '#10b981', INACTIVO: '#6b7280', FALLECIDO: '#ef4444' }[s] || '#6b7280')
const sLabel = (s: string) => ({ ACTIVO: 'Activo', INACTIVO: 'Inactivo', FALLECIDO: 'Fallecido' }[s] || s)

export default function Patients() {
  const navigate = useNavigate()
  const [patients, setPatients] = useState<Patient[]>([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [errors, setErrors] = useState<FormErrors>({})
  const [editingId, setEditingId] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [initError, setInitError] = useState<string | null>(null)
  const [form, setForm] = useState<PatientFormData>(emptyForm)

  const load = (s?: string) => patientsService.list({ page: 1, search: s ?? search }).then(r => setPatients(r.results ?? [])).catch(() => {})

  useEffect(() => {
    load('').then(() => setLoading(false)).catch((err: Error) => {
      setInitError(err.message || 'Error al cargar')
      setLoading(false)
    })
  }, [])

  const reset = () => { setForm(emptyForm); setErrors({}); setEditingId(null); setShowForm(false) }

  const validate = (): boolean => {
    const e: FormErrors = {}
    if (!form.first_name.trim()) e.first_name = 'El nombre es obligatorio'
    if (!form.last_name.trim()) e.last_name = 'El apellido es obligatorio'
    if (!form.birth_date) e.birth_date = 'La fecha de nacimiento es obligatoria'
    setErrors(e); return Object.keys(e).length === 0
  }

  const submit = async (ev: React.FormEvent) => {
    ev.preventDefault()
    if (!validate()) return
    setSubmitting(true)
    try {
      const p: Record<string, unknown> = {
        first_name: form.first_name, last_name: form.last_name,
        identity_type: form.identity_type,
        cedula: form.cedula || undefined, passport_number: form.passport_number || undefined,
        birth_date: form.birth_date, sex: form.sex, nationality: form.nationality,
        phone_primary: form.phone_primary || undefined, phone_secondary: form.phone_secondary || undefined,
        email: form.email || undefined, address: form.address || undefined,
        province: form.province || undefined, municipality: form.municipality || undefined,
        blood_type: form.blood_type || undefined, allergies: form.allergies || undefined,
        chronic_conditions: form.chronic_conditions || undefined,
        emergency_contact_name: form.emergency_contact_name || undefined,
        emergency_contact_phone: form.emergency_contact_phone || undefined,
        emergency_contact_relation: form.emergency_contact_relation || undefined,
        ars_provider: form.ars_provider || undefined,
        ars_affiliation_number: form.ars_affiliation_number || undefined,
        status: form.status,
      }
      let r: Patient
      if (editingId) {
        r = await patientsService.update(editingId, p as Partial<Patient>)
        setPatients(prev => prev.map(x => x.id === editingId ? r : x))
      } else {
        r = await patientsService.create(p as Partial<Patient>)
        setPatients(prev => [r, ...prev])
      }
      reset()
    } catch (err: unknown) {
      const apiErr = err as { response?: { data?: Record<string, string[]> } }
      if (apiErr.response?.data) {
        const e: FormErrors = {}
        for (const [k, v] of Object.entries(apiErr.response.data)) e[k] = v[0]
        setErrors(e)
      } else {
        setErrors({ _general: err instanceof Error ? err.message : 'Error al guardar' })
      }
    } finally { setSubmitting(false) }
  }

  const edit = (p: Patient) => {
    setEditingId(p.id)
    setForm({
      first_name: p.first_name || '', last_name: p.last_name || '',
      identity_type: p.identity_type || 'CEDULA',
      cedula: p.cedula || '', passport_number: p.passport_number || '',
      birth_date: p.birth_date ? p.birth_date.split('T')[0] : '',
      sex: p.sex || 'F', nationality: p.nationality || 'DOMINICANA',
      phone_primary: p.phone_primary || '', phone_secondary: p.phone_secondary || '',
      email: p.email || '', address: p.address || '',
      province: p.province || '', municipality: p.municipality || '',
      blood_type: p.blood_type || '', allergies: p.allergies || '',
      chronic_conditions: p.chronic_conditions || '',
      emergency_contact_name: p.emergency_contact_name || '',
      emergency_contact_phone: p.emergency_contact_phone || '',
      emergency_contact_relation: p.emergency_contact_relation || '',
      ars_provider: p.ars_provider || '', ars_affiliation_number: p.ars_affiliation_number || '',
      status: p.status || 'ACTIVO',
    })
    setErrors({})
    setShowForm(true)
  }

  const del = async (id: string) => {
    if (!window.confirm('¿Está seguro de eliminar este paciente?')) return
    try {
      const { api } = await import('../utils/api')
      await api.delete('/patients/' + id + '/')
      setPatients(prev => prev.filter(x => x.id !== id))
    } catch {}
  }

  if (loading) return <PageContainer title="Pacientes"><p>Cargando...</p></PageContainer>

  return (
    <PageContainer title="Pacientes">
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16, gap: 12, flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <input type="text" placeholder="Buscar por nombre o cédula..." value={search}
            onChange={e => { setSearch(e.target.value); load(e.target.value) }}
            style={{ padding: '8px 12px', borderRadius: 6, border: '1px solid #d1d5db', fontSize: 14, width: 280 }} />
          <span style={{ color: '#6b7280', fontSize: 13 }}>{patients.length} paciente{patients.length !== 1 ? 's' : ''}</span>
        </div>
        <button type="button" onClick={() => showForm ? reset() : setShowForm(true)}
          style={{ background: '#3b82f6', color: '#fff', border: 'none', borderRadius: 6, padding: '8px 16px', cursor: 'pointer', fontWeight: 500 }}>
          {showForm ? 'Cerrar' : '+ Nuevo Paciente'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={submit} style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 10, padding: 20, marginBottom: 20 }}>
          <h3 style={{ marginTop: 0, marginBottom: 16 }}>{editingId ? 'Editar Paciente' : 'Nuevo Paciente'}</h3>
          {errors._general && <div style={{ background: '#fef2f2', border: '1px solid #fecaca', color: '#991b1b', padding: '8px 12px', borderRadius: 6, marginBottom: 12 }}>{errors._general}</div>}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16, marginBottom: 16 }}>
            <Field label="Tipo de Documento">
              <Select value={form.identity_type} onChange={v => setForm({ ...form, identity_type: v })}
                options={[{ v: 'CEDULA', l: 'Cédula' }, { v: 'PASAPORTE', l: 'Pasaporte' }, { v: 'OTRO', l: 'Otro' }]} />
            </Field>
            <Field label="Cédula / Pasaporte" error={errors.cedula}>
              <input type="text" placeholder={form.identity_type === 'CEDULA' ? '00112345678' : 'Número'}
                value={form.identity_type === 'CEDULA' ? form.cedula : form.passport_number}
                onChange={e => form.identity_type === 'CEDULA' ? setForm({ ...form, cedula: e.target.value }) : setForm({ ...form, passport_number: e.target.value })}
                style={inputStyle(!!errors.cedula)} />
            </Field>
            <Field label="Nacionalidad">
              <input type="text" value={form.nationality} onChange={e => setForm({ ...form, nationality: e.target.value })} style={inputStyle()} />
            </Field>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
            <Field label="Nombre" required error={errors.first_name}>
              <input type="text" value={form.first_name} onChange={e => setForm({ ...form, first_name: e.target.value })} style={inputStyle(!!errors.first_name)} />
            </Field>
            <Field label="Apellido" required error={errors.last_name}>
              <input type="text" value={form.last_name} onChange={e => setForm({ ...form, last_name: e.target.value })} style={inputStyle(!!errors.last_name)} />
            </Field>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16, marginBottom: 16 }}>
            <Field label="Fecha de Nacimiento" required error={errors.birth_date}>
              <input type="date" value={form.birth_date} onChange={e => setForm({ ...form, birth_date: e.target.value })} style={inputStyle(!!errors.birth_date)} />
            </Field>
            <Field label="Sexo">
              <Select value={form.sex} onChange={v => setForm({ ...form, sex: v })}
                options={[{ v: 'F', l: 'Femenino' }, { v: 'M', l: 'Masculino' }, { v: 'O', l: 'Otro' }]} />
            </Field>
            <Field label="Estado">
              <Select value={form.status} onChange={v => setForm({ ...form, status: v })}
                options={[{ v: 'ACTIVO', l: 'Activo' }, { v: 'INACTIVO', l: 'Inactivo' }, { v: 'FALLECIDO', l: 'Fallecido' }]} />
            </Field>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16, marginBottom: 16 }}>
            <Field label="Teléfono Principal"><input type="text" value={form.phone_primary} onChange={e => setForm({ ...form, phone_primary: e.target.value })} style={inputStyle()} /></Field>
            <Field label="Teléfono Secundario"><input type="text" value={form.phone_secondary} onChange={e => setForm({ ...form, phone_secondary: e.target.value })} style={inputStyle()} /></Field>
            <Field label="Correo Electrónico"><input type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} style={inputStyle()} /></Field>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: 16, marginBottom: 16 }}>
            <Field label="Dirección"><input type="text" value={form.address} onChange={e => setForm({ ...form, address: e.target.value })} style={inputStyle()} /></Field>
            <Field label="Provincia"><input type="text" value={form.province} onChange={e => setForm({ ...form, province: e.target.value })} style={inputStyle()} /></Field>
            <Field label="Municipio"><input type="text" value={form.municipality} onChange={e => setForm({ ...form, municipality: e.target.value })} style={inputStyle()} /></Field>
          </div>

          <div style={{ display: 'flex', gap: 8 }}>
            <button type="submit" disabled={submitting}
              style={{ background: submitting ? '#93c5fd' : '#3b82f6', color: '#fff', border: 'none', borderRadius: 6, padding: '8px 20px', cursor: submitting ? 'not-allowed' : 'pointer', fontWeight: 500 }}>
              {submitting ? (editingId ? 'Guardando...' : 'Creando...') : (editingId ? 'Guardar Cambios' : 'Crear Paciente')}
            </button>
            <button type="button" onClick={reset}
              style={{ background: '#f3f4f6', color: '#374151', border: '1px solid #d1d5db', borderRadius: 6, padding: '8px 20px', cursor: 'pointer', fontWeight: 500 }}>Cerrar</button>
          </div>
        </form>
      )}

      <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 10, overflow: 'hidden' }}>
        {patients.length === 0 ? (
          <p style={{ padding: 24, margin: 0, color: '#6b7280', textAlign: 'center' }}>No hay pacientes. Haga clic en <strong>+ Nuevo Paciente</strong> para registrar uno.</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
            <thead><tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
              <Th>Nombre</Th><Th>Documento</Th><Th>Teléfono</Th><Th>Sexo</Th><Th>Estado</Th><Th>Acciones</Th>
            </tr></thead>
            <tbody>
              {patients.map(p => (
                <tr key={p.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                  <td style={{ padding: '12px 16px', fontWeight: 500 }}>{p.first_name} {p.last_name}</td>
                  <td style={{ padding: '12px 16px', color: '#6b7280', fontSize: 13 }}>{p.identity_type === 'CEDULA' ? p.cedula : p.passport_number || '—'}</td>
                  <td style={{ padding: '12px 16px', color: '#6b7280', fontSize: 13 }}>{p.phone_primary || '—'}</td>
                  <td style={{ padding: '12px 16px', fontSize: 13 }}>{p.sex === 'F' ? 'Femenino' : p.sex === 'M' ? 'Masculino' : 'Otro'}</td>
                  <td style={{ padding: '12px 16px' }}>
                    <span style={{ display: 'inline-block', padding: '2px 10px', borderRadius: 9999, fontSize: 12, fontWeight: 500, color: '#fff', background: sColor(p.status) }}>{sLabel(p.status)}</span>
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <div style={{ display: 'flex', gap: 6 }}>
                      <Btn color="#10b981" onClick={() => navigate(`/pacientes/${p.id}/historial`)}>Ver Historial</Btn>
                      <Btn color="#3b82f6" onClick={() => edit(p)}>Editar</Btn>
                      <Btn color="#ef4444" onClick={() => del(p.id)}>Eliminar</Btn>
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

// ── tiny helpers ──

const inputStyle = (err?: boolean): React.CSSProperties => ({
  width: '100%', padding: '8px 12px', borderRadius: 6,
  border: `1px solid ${err ? '#ef4444' : '#d1d5db'}`, fontSize: 14, boxSizing: 'border-box',
})

const Field: React.FC<{ label: string; required?: boolean; error?: string; children: React.ReactNode }> = ({ label, required, error, children }) => (
  <div>
    <label style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>{label}{required && <span style={{ color: '#ef4444' }}> *</span>}</label>
    {children}
    {error && <span style={{ color: '#ef4444', fontSize: 12 }}>{error}</span>}
  </div>
)

const Th: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <th style={{ textAlign: 'left', padding: '12px 16px', fontWeight: 600, color: '#374151' }}>{children}</th>
)

const Select: React.FC<{ value: string; onChange: (v: string) => void; options: { v: string; l: string }[] }> = ({ value, onChange, options }) => (
  <select value={value} onChange={e => onChange(e.target.value)}
    style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid #d1d5db', fontSize: 14 }}>
    {options.map(o => <option key={o.v} value={o.v}>{o.l}</option>)}
  </select>
)

const Btn: React.FC<{ color: string; onClick: () => void; children: React.ReactNode }> = ({ color, onClick, children }) => (
  <button onClick={onClick}
    style={{ background: 'none', border: `1px solid ${color}`, color, borderRadius: 4, padding: '4px 10px', cursor: 'pointer', fontSize: 12 }}>{children}</button>
)
