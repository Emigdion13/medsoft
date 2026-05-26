import React, { useEffect, useState } from 'react'
import { doctorsService, specialtiesService } from '../../services/resourceServices'
import type { Doctor, Specialty } from '../../types'

interface DoctorForm {
  first_name: string; last_name: string; cedula: string
  license_number: string; medical_college_number: string
  specialty_main_id: string; phone: string; email: string
  office_room: string
}

const emptyForm: DoctorForm = {
  first_name: '', last_name: '', cedula: '',
  license_number: '', medical_college_number: '',
  specialty_main_id: '', phone: '', email: '', office_room: '',
}

export default function DoctorsPage() {
  const [doctors, setDoctors] = useState<Doctor[]>([])
  const [specialties, setSpecialties] = useState<Specialty[]>([])
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState<DoctorForm>(emptyForm)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    Promise.all([
      doctorsService.list({ page: 1, search: '' }),
      specialtiesService.list({ page: 1 }),
    ]).then(([d, s]) => {
      setDoctors(d.results ?? [])
      setSpecialties(s.results ?? [])
    }).finally(() => setLoading(false))
  }, [refreshKey])

  const reset = () => { setForm(emptyForm); setEditingId(null) }

  const edit = (d: Doctor) => {
    setEditingId(d.id)
    setForm({
      first_name: d.first_name, last_name: d.last_name,
      cedula: d.cedula, license_number: d.license_number,
      medical_college_number: d.medical_college_number || '',
      specialty_main_id: d.specialty_main?.id || d.specialty_main_id || '',
      phone: d.phone || '', email: d.email || '',
      office_room: d.office_room || '',
    })
  }

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.first_name || !form.last_name || !form.cedula || !form.license_number || !form.specialty_main_id) return
    setSaving(true)
    try {
      const payload = {
        ...form,
        specialty_main_id: form.specialty_main_id,
      }
      if (editingId) {
        await doctorsService.update(editingId, payload as any)
      } else {
        await doctorsService.create(payload as any)
      }
      reset()
      setRefreshKey(k => k + 1)
    } finally { setSaving(false) }
  }

  const remove = async (id: string) => {
    if (!window.confirm('¿Eliminar este médico?')) return
    await doctorsService.delete(id)
    setRefreshKey(k => k + 1)
  }

  const isValid = form.first_name && form.last_name && form.cedula && form.license_number && form.specialty_main_id

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 420px', gap: 20, alignItems: 'start' }}>
        {/* List */}
        <div style={cardStyle}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <h2 style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>Médicos</h2>
            <span style={badgeStyle}>{doctors.length} médico{doctors.length !== 1 ? 's' : ''}</span>
          </div>

          {loading ? (
            <div style={{ textAlign: 'center', padding: 40, color: '#9ca3af' }}>Cargando...</div>
          ) : doctors.length === 0 ? (
            <div style={{ textAlign: 'center', padding: 40 }}>
              <div style={{ fontSize: 40, marginBottom: 8 }}>👨‍⚕️</div>
              <p style={{ color: '#9ca3af', margin: 0 }}>No hay médicos registrados</p>
            </div>
          ) : (
            <div style={{ borderRadius: 10, overflow: 'hidden', border: '1px solid #e5e7eb' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
                <thead>
                  <tr style={{ background: '#f8fafc', borderBottom: '2px solid #e5e7eb' }}>
                    <th style={thStyle}>Nombre</th>
                    <th style={thStyle}>Cédula</th>
                    <th style={thStyle}>Especialidad</th>
                    <th style={thStyle}>Licencia</th>
                    <th style={{ ...thStyle, textAlign: 'center', width: 120 }}>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {doctors.map((d, i) => (
                    <tr key={d.id} style={{
                      background: i % 2 === 0 ? '#fff' : '#fafbfc',
                      borderBottom: '1px solid #f1f5f9',
                    }}>
                      <td style={tdStyle}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                          <div style={{
                            width: 32, height: 32, borderRadius: '50%',
                            background: '#dbeafe', color: '#2563eb',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            fontSize: 13, fontWeight: 600,
                          }}>
                            {d.first_name.charAt(0)}{d.last_name.charAt(0)}
                          </div>
                          <div>
                            <div style={{ fontWeight: 600 }}>{d.first_name} {d.last_name}</div>
                            {d.email && <div style={{ fontSize: 12, color: '#94a3b8' }}>{d.email}</div>}
                          </div>
                        </div>
                      </td>
                      <td style={{ ...tdStyle, fontFamily: 'monospace', fontSize: 13 }}>{d.cedula}</td>
                      <td style={tdStyle}>
                        {d.specialty_main ? (
                          <span style={{
                            background: '#eff6ff', color: '#2563eb',
                            padding: '3px 10px', borderRadius: 20, fontSize: 12, fontWeight: 500,
                          }}>
                            {d.specialty_main.name}
                          </span>
                        ) : '—'}
                      </td>
                      <td style={{ ...tdStyle, fontSize: 13, color: '#64748b', fontFamily: 'monospace' }}>
                        {d.license_number}
                      </td>
                      <td style={{ ...tdStyle, textAlign: 'center' }}>
                        <div style={{ display: 'flex', gap: 6, justifyContent: 'center' }}>
                          <button onClick={() => edit(d)} style={btnSm}>Editar</button>
                          <button onClick={() => remove(d.id)} style={{ ...btnSm, color: '#dc2626', borderColor: '#fecaca' }}>
                            Eliminar
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Form */}
        <form onSubmit={submit} style={{ ...cardStyle, position: 'sticky', top: 24 }}>
          <h2 style={{ margin: '0 0 4px', fontSize: 18, fontWeight: 700 }}>
            {editingId ? 'Editar Médico' : 'Nuevo Médico'}
          </h2>
          <p style={{ margin: '0 0 20px', fontSize: 13, color: '#6b7280' }}>
            {editingId ? 'Modifique los datos del médico' : 'Registre un nuevo profesional médico'}
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginBottom: 14 }}>
            <div>
              <label style={lbl}>Nombre</label>
              <input placeholder="Ej: Carlos" value={form.first_name}
                onChange={e => setForm({ ...form, first_name: e.target.value })} style={inp} />
            </div>
            <div>
              <label style={lbl}>Apellido</label>
              <input placeholder="Ej: Mendez" value={form.last_name}
                onChange={e => setForm({ ...form, last_name: e.target.value })} style={inp} />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginBottom: 14 }}>
            <div>
              <label style={lbl}>Cédula</label>
              <input placeholder="000-0000000-0" value={form.cedula}
                onChange={e => setForm({ ...form, cedula: e.target.value })} style={inp} />
            </div>
            <div>
              <label style={lbl}>Licencia (Exequátur)</label>
              <input placeholder="Ej: RM-001-2024" value={form.license_number}
                onChange={e => setForm({ ...form, license_number: e.target.value })} style={inp} />
            </div>
          </div>

          <div style={{ marginBottom: 14 }}>
            <label style={lbl}>Especialidad Principal</label>
            <select value={form.specialty_main_id}
              onChange={e => setForm({ ...form, specialty_main_id: e.target.value })}
              style={{ ...inp, cursor: 'pointer', background: '#fff' }}>
              <option value="">Seleccionar especialidad...</option>
              {specialties.map(s => (
                <option key={s.id} value={s.id}>{s.code} — {s.name}</option>
              ))}
            </select>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginBottom: 14 }}>
            <div>
              <label style={lbl}>Colegio Médico #</label>
              <input placeholder="MC-001" value={form.medical_college_number}
                onChange={e => setForm({ ...form, medical_college_number: e.target.value })} style={inp} />
            </div>
            <div>
              <label style={lbl}>Consultorio</label>
              <input placeholder="Ej: 301" value={form.office_room}
                onChange={e => setForm({ ...form, office_room: e.target.value })} style={inp} />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginBottom: 20 }}>
            <div>
              <label style={lbl}>Teléfono</label>
              <input placeholder="+1-809-555-0000" value={form.phone}
                onChange={e => setForm({ ...form, phone: e.target.value })} style={inp} />
            </div>
            <div>
              <label style={lbl}>Email</label>
              <input type="email" placeholder="doctor@clinica.com" value={form.email}
                onChange={e => setForm({ ...form, email: e.target.value })} style={inp} />
            </div>
          </div>

          <div style={{ display: 'flex', gap: 8 }}>
            <button type="submit" disabled={saving || !isValid} style={{
              flex: 1, padding: '10px 0', fontSize: 14, fontWeight: 600, border: 'none', borderRadius: 8,
              background: (saving || !isValid) ? '#d1d5db' :
                editingId ? 'linear-gradient(135deg, #2563eb, #1d4ed8)' : '#059669',
              color: '#fff', cursor: (saving || !isValid) ? 'not-allowed' : 'pointer',
            }}>
              {saving ? 'Guardando...' : editingId ? 'Actualizar' : 'Crear Médico'}
            </button>
            {editingId && (
              <button type="button" onClick={reset} style={btnOutline}>
                Cancelar
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  )
}

const cardStyle: React.CSSProperties = {
  background: '#fff', border: '1px solid #e5e7eb',
  borderRadius: 14, padding: 24, boxShadow: 'var(--shadow)',
}
const badgeStyle: React.CSSProperties = {
  background: '#f1f5f9', color: '#475569', borderRadius: 20,
  padding: '3px 12px', fontSize: 13, fontWeight: 500,
}
const thStyle: React.CSSProperties = {
  textAlign: 'left', padding: '10px 14px', fontWeight: 600,
  fontSize: 12, color: '#64748b', textTransform: 'uppercase', letterSpacing: '.5px',
}
const tdStyle: React.CSSProperties = { padding: '12px 14px' }
const lbl: React.CSSProperties = {
  display: 'block', fontSize: 13, fontWeight: 600, color: '#374151', marginBottom: 5,
}
const inp: React.CSSProperties = {
  width: '100%', padding: '10px 14px', fontSize: 14,
  border: '1px solid #d1d5db', borderRadius: 8,
  outline: 'none', boxSizing: 'border-box',
}
const btnSm: React.CSSProperties = {
  padding: '4px 12px', borderRadius: 6, border: '1px solid #d1d5db',
  background: '#fff', color: '#374151', cursor: 'pointer', fontSize: 12, fontWeight: 500,
}
const btnOutline: React.CSSProperties = {
  padding: '10px 20px', borderRadius: 8, border: '1px solid #d1d5db',
  background: '#fff', color: '#374151', cursor: 'pointer', fontSize: 14, fontWeight: 500,
}
