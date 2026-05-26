import React, { useEffect, useState } from 'react'
import { UserList } from './UserList'
import { UserForm } from './UserForm'
import { usersService, secretaryDoctorService, type SecretaryDoctorAssignment } from '../../services/authService'
import { doctorsService, specialtiesService } from '../../services/resourceServices'
import type { UserListItem, UserRole, Doctor, Specialty } from '../../types'

const defaultForm: {
  first_name: string
  last_name: string
  username: string
  email: string
  phone: string
  role: UserRole
  is_active: boolean
} = {
  first_name: '',
  last_name: '',
  username: '',
  email: '',
  phone: '',
  role: 'RECEPTIONIST',
  is_active: true,
}

// Doctor-specific fields
interface DoctorFields {
  cedula: string
  license_number: string
  medical_college_number: string
  specialty_main_id: string
  office_room: string
}

const emptyDoctor: DoctorFields = {
  cedula: '', license_number: '', medical_college_number: '',
  specialty_main_id: '', office_room: '',
}

export default function AdminUsersPage() {
  const [editing, setEditing] = useState<UserListItem | null>(null)
  const [form, setForm] = useState(defaultForm)
  const [refreshKey, setRefreshKey] = useState(0)

  // ── Doctor fields (visible when role is DOCTOR) ──
  const [doctorForm, setDoctorForm] = useState<DoctorFields>(emptyDoctor)
  const [specialties, setSpecialties] = useState<Specialty[]>([])
  const [existingDoctor, setExistingDoctor] = useState<Doctor | null>(null)

  // ── Secretary-Doctor assignment state ──
  const [assignments, setAssignments] = useState<SecretaryDoctorAssignment[]>([])
  const [allDoctors, setAllDoctors] = useState<Doctor[]>([])
  const [selectedDoctorId, setSelectedDoctorId] = useState('')

  const isDoctor = form.role === 'DOCTOR'
  const isSecretary = form.role === 'SECRETARY'

  // Load reference data
  useEffect(() => {
    if (isSecretary) {
      doctorsService.list({ page: 1, search: '' }).then(r => setAllDoctors(r.results ?? []))
    }
    if (isDoctor) {
      specialtiesService.list({ page: 1 }).then(r => setSpecialties(r.results ?? []))
    }
  }, [isSecretary, isDoctor])

  const loadAssignments = (secretaryId: string) => {
    secretaryDoctorService.list(secretaryId)
      .then(r => setAssignments(r.results ?? []))
      .catch(err => console.error('Error loading assignments:', err))
  }

  const onSelectEdit = (u: UserListItem) => {
    setEditing(u)
    setForm({
      first_name: u.first_name,
      last_name: u.last_name,
      username: u.username,
      email: u.email,
      phone: u.phone || '',
      role: u.role,
      is_active: u.is_active,
    })
    setDoctorForm(emptyDoctor)
    setExistingDoctor(null)
    if (u.role === 'SECRETARY') {
      loadAssignments(u.id)
    } else {
      setAssignments([])
    }
    // If editing a doctor, load their doctor record
    if (u.role === 'DOCTOR') {
      doctorsService.list({ page: 1, search: u.email }).then(r => {
        const doc = (r.results ?? []).find((d: Doctor) => d.email === u.email || d.first_name === u.first_name)
        if (doc) {
          setExistingDoctor(doc)
          setDoctorForm({
            cedula: doc.cedula,
            license_number: doc.license_number,
            medical_college_number: doc.medical_college_number || '',
            specialty_main_id: doc.specialty_main?.id || doc.specialty_main_id || '',
            office_room: doc.office_room || '',
          })
        }
      })
    }
  }

  // When role changes in form (e.g., selecting SECRETARY during creation)
  const handleFormChange = (next: typeof form) => {
    setForm(next)
    if (next.role === 'SECRETARY' && editing) {
      loadAssignments(editing.id)
    } else if (next.role !== 'SECRETARY') {
      setAssignments([])
    }
  }

  const onSubmit = async () => {
    let savedUser: UserListItem | undefined
    if (editing) {
      savedUser = await usersService.update(editing.id, form as any)
    } else {
      savedUser = await usersService.create(form as any)
    }

    // If role is DOCTOR and doctor fields are filled, create/update doctor record
    if (form.role === 'DOCTOR' && doctorForm.cedula && doctorForm.license_number && doctorForm.specialty_main_id) {
      const docPayload = {
        ...doctorForm,
        first_name: form.first_name,
        last_name: form.last_name,
        email: form.email,
        phone: form.phone,
        organization: '',
      }
      if (existingDoctor) {
        await doctorsService.update(existingDoctor.id, docPayload as any)
      } else if (savedUser) {
        // Link: we need the user ID. For new users, create doctor with user link
        await doctorsService.create(docPayload as any)
      }
    }

    setEditing(null)
    setForm(defaultForm)
    setDoctorForm(emptyDoctor)
    setExistingDoctor(null)
    setAssignments([])
    setRefreshKey(k => k + 1)
  }

  const addDoctorAssignment = async () => {
    if (!editing || !selectedDoctorId) return
    await secretaryDoctorService.create(editing.id, selectedDoctorId)
    setSelectedDoctorId('')
    loadAssignments(editing.id)
  }

  const removeDoctorAssignment = async (assignmentId: string) => {
    if (!editing) return
    await secretaryDoctorService.delete(assignmentId)
    loadAssignments(editing.id)
  }

  // Get doctors not yet assigned
  const assignedDoctorIds = new Set(assignments.map(a => a.doctor_id).filter(Boolean))
  const availableDoctors = allDoctors.filter(d => !assignedDoctorIds.has(d.id))

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: 12 }}>
      <UserList onSelectEdit={onSelectEdit} refreshKey={refreshKey} />

      <div>
        <UserForm value={form} onChange={handleFormChange} onSubmit={() => void onSubmit()} submitLabel={editing ? 'Actualizar usuario' : 'Crear usuario'} />

        {/* Doctor Fields — visible when role is DOCTOR */}
        {isDoctor && (
          <div style={{
            marginTop: 16, background: '#fff', border: '1px solid #e5e7eb',
            borderRadius: 12, padding: 20, boxShadow: 'var(--shadow)',
          }}>
            <h3 style={{ margin: '0 0 4px', fontSize: 16, fontWeight: 600 }}>
              👨‍⚕️ Datos del Médico
            </h3>
            <p style={{ margin: '0 0 14px', fontSize: 13, color: '#6b7280' }}>
              {existingDoctor ? 'Datos profesionales del médico' : 'Complete los datos profesionales para crear el registro médico'}
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 12 }}>
              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#374151', marginBottom: 4 }}>Cédula</label>
                <input placeholder="000-0000000-0" value={doctorForm.cedula}
                  onChange={e => setDoctorForm({ ...doctorForm, cedula: e.target.value })}
                  style={{ width: '100%', padding: '8px 12px', fontSize: 13, border: '1px solid #d1d5db', borderRadius: 6, outline: 'none', boxSizing: 'border-box' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#374151', marginBottom: 4 }}>Exequátur</label>
                <input placeholder="RM-001-2024" value={doctorForm.license_number}
                  onChange={e => setDoctorForm({ ...doctorForm, license_number: e.target.value })}
                  style={{ width: '100%', padding: '8px 12px', fontSize: 13, border: '1px solid #d1d5db', borderRadius: 6, outline: 'none', boxSizing: 'border-box' }} />
              </div>
            </div>

            <div style={{ marginBottom: 12 }}>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#374151', marginBottom: 4 }}>Especialidad</label>
              <select value={doctorForm.specialty_main_id}
                onChange={e => setDoctorForm({ ...doctorForm, specialty_main_id: e.target.value })}
                style={{ width: '100%', padding: '8px 12px', fontSize: 13, border: '1px solid #d1d5db', borderRadius: 6, outline: 'none', boxSizing: 'border-box', background: '#fff' }}>
                <option value="">Seleccionar especialidad...</option>
                {specialties.map(s => (
                  <option key={s.id} value={s.id}>{s.code} — {s.name}</option>
                ))}
              </select>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#374151', marginBottom: 4 }}>Colegio Médico #</label>
                <input placeholder="MC-001" value={doctorForm.medical_college_number}
                  onChange={e => setDoctorForm({ ...doctorForm, medical_college_number: e.target.value })}
                  style={{ width: '100%', padding: '8px 12px', fontSize: 13, border: '1px solid #d1d5db', borderRadius: 6, outline: 'none', boxSizing: 'border-box' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#374151', marginBottom: 4 }}>Consultorio</label>
                <input placeholder="301" value={doctorForm.office_room}
                  onChange={e => setDoctorForm({ ...doctorForm, office_room: e.target.value })}
                  style={{ width: '100%', padding: '8px 12px', fontSize: 13, border: '1px solid #d1d5db', borderRadius: 6, outline: 'none', boxSizing: 'border-box' }} />
              </div>
            </div>
          </div>
        )}

        {/* Doctor Assignment Section — visible when role is SECRETARY */}
        {isSecretary && (
          <div style={{
            marginTop: 16, background: '#fff', border: '1px solid #e5e7eb',
            borderRadius: 12, padding: 20, boxShadow: 'var(--shadow)',
          }}>
            <h3 style={{ margin: '0 0 4px', fontSize: 16, fontWeight: 600 }}>
              🩺 Médicos Asignados
            </h3>
            <p style={{ margin: '0 0 14px', fontSize: 13, color: '#6b7280' }}>
              {editing
                ? 'Esta secretaria verá las citas de los médicos asignados'
                : 'Guarde el usuario primero para poder asignar médicos'}
            </p>

            {/* Assignments table — only when editing */}
            {editing && (
              <>
                {assignments.length === 0 ? (
                  <div style={{
                    background: '#f9fafb', border: '1px dashed #d1d5db',
                    borderRadius: 8, padding: '20px', textAlign: 'center',
                    marginBottom: 14,
                  }}>
                    <div style={{ fontSize: 28, marginBottom: 4 }}>📭</div>
                    <p style={{ margin: 0, color: '#9ca3af', fontSize: 13 }}>
                      Sin médicos asignados
                    </p>
                  </div>
                ) : (
                  <div style={{ marginBottom: 14 }}>
                    <div style={{
                      display: 'flex', alignItems: 'center', gap: 8,
                      marginBottom: 8, fontSize: 13, fontWeight: 600, color: '#374151',
                    }}>
                      <span style={{
                        background: '#dbeafe', color: '#1d4ed8',
                        borderRadius: 20, padding: '2px 10px', fontSize: 12,
                      }}>
                        {assignments.length} asignado{assignments.length !== 1 ? 's' : ''}
                      </span>
                    </div>
                    <table style={{
                      width: '100%', borderCollapse: 'collapse',
                      fontSize: 13, borderRadius: 8, overflow: 'hidden',
                      border: '1px solid #e5e7eb',
                    }}>
                      <thead>
                        <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e5e7eb' }}>
                          <th style={{ padding: '8px 12px', textAlign: 'left', fontWeight: 600 }}>Médico</th>
                          <th style={{ padding: '8px 12px', textAlign: 'center', fontWeight: 600, width: 70 }}>Acción</th>
                        </tr>
                      </thead>
                      <tbody>
                        {assignments.map(a => (
                          <tr key={a.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                            <td style={{ padding: '8px 12px' }}>
                              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                <span style={{
                                  width: 28, height: 28, borderRadius: '50%',
                                  background: '#dbeafe', display: 'flex',
                                  alignItems: 'center', justifyContent: 'center',
                                  fontSize: 13,
                                }}>👨‍⚕️</span>
                                {a.doctor_name}
                              </div>
                            </td>
                            <td style={{ padding: '8px 12px', textAlign: 'center' }}>
                              <button onClick={() => removeDoctorAssignment(a.id)}
                                title="Quitar médico"
                                style={{
                                  background: '#fef2f2', border: '1px solid #fecaca',
                                  color: '#dc2626', borderRadius: 6,
                                  padding: '3px 10px', cursor: 'pointer', fontSize: 12,
                                  fontWeight: 500,
                                }}>
                                Quitar
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {/* Add doctor dropdown */}
                {availableDoctors.length > 0 && (
                  <div style={{ display: 'flex', gap: 8 }}>
                    <select value={selectedDoctorId}
                      onChange={e => setSelectedDoctorId(e.target.value)}
                      style={{
                        flex: 1, padding: '8px 12px', borderRadius: 8,
                        border: '1px solid #d1d5db', fontSize: 14,
                      }}>
                      <option value="">Seleccionar médico...</option>
                      {availableDoctors.map(d => (
                        <option key={d.id} value={d.id}>{d.first_name} {d.last_name}</option>
                      ))}
                    </select>
                    <button onClick={addDoctorAssignment}
                      disabled={!selectedDoctorId}
                      style={{
                        padding: '8px 16px', borderRadius: 8, border: 'none',
                        background: selectedDoctorId ? '#2563eb' : '#d1d5db',
                        color: '#fff', fontWeight: 600,
                        cursor: selectedDoctorId ? 'pointer' : 'not-allowed',
                        whiteSpace: 'nowrap',
                      }}>
                      + Asignar
                    </button>
                  </div>
                )}
                {availableDoctors.length === 0 && assignments.length > 0 && (
                  <p style={{ color: '#9ca3af', fontSize: 13, margin: 0 }}>
                    ✅ Todos los médicos están asignados.
                  </p>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
