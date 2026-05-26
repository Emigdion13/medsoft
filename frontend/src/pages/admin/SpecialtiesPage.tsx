import React, { useEffect, useState } from 'react'
import { specialtiesService } from '../../services/resourceServices'
import type { Specialty } from '../../types'

const emptyForm = { code: '', name: '', description: '' }

export default function SpecialtiesPage() {
  const [specialties, setSpecialties] = useState<Specialty[]>([])
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState(emptyForm)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    specialtiesService.list({ page: 1 })
      .then(r => setSpecialties(r.results ?? []))
      .finally(() => setLoading(false))
  }, [refreshKey])

  const reset = () => { setForm(emptyForm); setEditingId(null) }

  const edit = (s: Specialty) => {
    setEditingId(s.id)
    setForm({ code: s.code, name: s.name, description: s.description || '' })
  }

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.code.trim() || !form.name.trim()) return
    setSaving(true)
    try {
      if (editingId) {
        await specialtiesService.update(editingId, form)
      } else {
        await specialtiesService.create(form)
      }
      reset()
      setRefreshKey(k => k + 1)
    } finally { setSaving(false) }
  }

  const remove = async (id: string) => {
    if (!window.confirm('¿Eliminar esta especialidad?')) return
    await specialtiesService.delete(id)
    setRefreshKey(k => k + 1)
  }

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gap: 20, alignItems: 'start' }}>
        {/* List */}
        <div style={{
          background: '#fff', border: '1px solid #e5e7eb',
          borderRadius: 14, padding: 20, boxShadow: 'var(--shadow)',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <h2 style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>Especialidades Médicas</h2>
            <span style={{
              background: '#f1f5f9', color: '#475569', borderRadius: 20,
              padding: '3px 12px', fontSize: 13, fontWeight: 500,
            }}>
              {specialties.length} especialidad{specialties.length !== 1 ? 'es' : ''}
            </span>
          </div>

          {loading ? (
            <div style={{ textAlign: 'center', padding: 40, color: '#9ca3af' }}>Cargando...</div>
          ) : specialties.length === 0 ? (
            <div style={{ textAlign: 'center', padding: 40 }}>
              <div style={{ fontSize: 40, marginBottom: 8 }}>🏥</div>
              <p style={{ color: '#9ca3af', margin: 0 }}>No hay especialidades registradas</p>
            </div>
          ) : (
            <div style={{ borderRadius: 10, overflow: 'hidden', border: '1px solid #e5e7eb' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
                <thead>
                  <tr style={{ background: '#f8fafc', borderBottom: '2px solid #e5e7eb' }}>
                    <th style={thStyle}>Código</th>
                    <th style={thStyle}>Nombre</th>
                    <th style={thStyle}>Descripción</th>
                    <th style={{ ...thStyle, textAlign: 'center', width: 70 }}>Activo</th>
                    <th style={{ ...thStyle, textAlign: 'center', width: 120 }}>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {specialties.map((s, i) => (
                    <tr key={s.id} style={{
                      background: i % 2 === 0 ? '#fff' : '#fafbfc',
                      borderBottom: '1px solid #f1f5f9',
                    }}>
                      <td style={tdStyle}>
                        <span style={{
                          background: '#eff6ff', color: '#2563eb',
                          padding: '2px 8px', borderRadius: 4,
                          fontSize: 13, fontWeight: 600, fontFamily: 'monospace',
                        }}>{s.code}</span>
                      </td>
                      <td style={{ ...tdStyle, fontWeight: 500 }}>{s.name}</td>
                      <td style={{ ...tdStyle, color: '#64748b', fontSize: 13 }}>
                        {s.description || '—'}
                      </td>
                      <td style={{ ...tdStyle, textAlign: 'center' }}>
                        <span style={{
                          display: 'inline-block', width: 8, height: 8, borderRadius: '50%',
                          background: s.is_active ? '#10b981' : '#ef4444',
                        }} />
                      </td>
                      <td style={{ ...tdStyle, textAlign: 'center' }}>
                        <div style={{ display: 'flex', gap: 6, justifyContent: 'center' }}>
                          <button onClick={() => edit(s)} style={btnSm}>Editar</button>
                          <button onClick={() => remove(s.id)} style={{ ...btnSm, color: '#dc2626', borderColor: '#fecaca' }}>
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
        <form onSubmit={submit} style={{
          background: '#fff', border: '1px solid #e5e7eb',
          borderRadius: 14, padding: 24, boxShadow: 'var(--shadow)',
          position: 'sticky', top: 24,
        }}>
          <h2 style={{ margin: '0 0 4px', fontSize: 18, fontWeight: 700 }}>
            {editingId ? 'Editar Especialidad' : 'Nueva Especialidad'}
          </h2>
          <p style={{ margin: '0 0 20px', fontSize: 13, color: '#6b7280' }}>
            {editingId ? 'Modifique los datos de la especialidad' : 'Registre una nueva especialidad médica'}
          </p>

          <div style={{ marginBottom: 14 }}>
            <label style={labelStyle}>Código</label>
            <input
              placeholder="Ej: CARD, PED, NEUR"
              value={form.code}
              onChange={e => setForm({ ...form, code: e.target.value.toUpperCase() })}
              style={inputStyle}
              maxLength={20}
            />
          </div>

          <div style={{ marginBottom: 14 }}>
            <label style={labelStyle}>Nombre</label>
            <input
              placeholder="Ej: Cardiología"
              value={form.name}
              onChange={e => setForm({ ...form, name: e.target.value })}
              style={inputStyle}
            />
          </div>

          <div style={{ marginBottom: 20 }}>
            <label style={labelStyle}>Descripción (opcional)</label>
            <textarea
              placeholder="Breve descripción de la especialidad..."
              value={form.description}
              onChange={e => setForm({ ...form, description: e.target.value })}
              rows={3}
              style={{ ...inputStyle, resize: 'vertical' }}
            />
          </div>

          <div style={{ display: 'flex', gap: 8 }}>
            <button type="submit" disabled={saving || !form.code || !form.name} style={{
              flex: 1, padding: '10px 0', fontSize: 14, fontWeight: 600, border: 'none', borderRadius: 8,
              background: (saving || !form.code || !form.name) ? '#d1d5db' :
                editingId ? 'linear-gradient(135deg, #2563eb, #1d4ed8)' : '#059669',
              color: '#fff', cursor: (saving || !form.code || !form.name) ? 'not-allowed' : 'pointer',
            }}>
              {saving ? 'Guardando...' : editingId ? 'Actualizar' : 'Crear Especialidad'}
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

const thStyle: React.CSSProperties = {
  textAlign: 'left', padding: '10px 14px', fontWeight: 600,
  fontSize: 12, color: '#64748b', textTransform: 'uppercase', letterSpacing: '.5px',
}
const tdStyle: React.CSSProperties = { padding: '12px 14px' }
const labelStyle: React.CSSProperties = {
  display: 'block', fontSize: 13, fontWeight: 600, color: '#374151', marginBottom: 5,
}
const inputStyle: React.CSSProperties = {
  width: '100%', padding: '10px 14px', fontSize: 14,
  border: '1px solid #d1d5db', borderRadius: 8,
  outline: 'none', boxSizing: 'border-box',
}
const btnSm: React.CSSProperties = {
  padding: '4px 12px', borderRadius: 6, border: '1px solid #d1d5db',
  background: '#fff', color: '#374151', cursor: 'pointer',
  fontSize: 12, fontWeight: 500,
}
const btnOutline: React.CSSProperties = {
  padding: '10px 20px', borderRadius: 8, border: '1px solid #d1d5db',
  background: '#fff', color: '#374151', cursor: 'pointer',
  fontSize: 14, fontWeight: 500,
}
