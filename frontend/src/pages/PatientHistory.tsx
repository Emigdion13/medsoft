import React, { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { PageContainer } from '../components/common/SharedComponents'
import { CanAccess } from '../lib/rbac/guards'
import { patientsService, doctorsService } from '../services/resourceServices'
import {
  encountersService,
  vitalSignsService,
  clinicalNotesService,
  diagnosesService,
  prescriptionsService,
} from '../services/clinicalServices'
import type {
  Patient,
  Doctor,
  Encounter,
  VitalSign,
  ClinicalNote,
  Diagnosis,
  Prescription,
} from '../types'

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

const NOTE_TYPES = [
  ['EVOLUCION', 'Evolución Clínica'],
  ['HISTORIA', 'Historia Clínica'],
  ['NOTA_ENFERMERIA', 'Nota de Enfermería'],
  ['NOTA_MEDICA', 'Nota Médica'],
]

const DIAGNOSIS_TYPES = [
  ['PRINCIPAL', 'Principal'],
  ['SECUNDARIO', 'Secundario'],
  ['COMORBILIDAD', 'Comorbilidad'],
]

const ROUTES = [
  ['ORAL', 'Oral'], ['IV', 'Intravenoso'], ['IM', 'Intramuscular'], ['TOPICA', 'Tópica'],
  ['INHALADA', 'Inhalada'], ['NASAL', 'Nasal'], ['OTICO', 'Ótico'], ['OCULAR', 'Ocular'],
]

const fmtDateTime = (s: string) =>
  new Date(s).toLocaleString('es-DO', {
    year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit',
  })

// Local datetime string for <input type="datetime-local"> default value (now).
const nowLocal = () => {
  const d = new Date()
  d.setMinutes(d.getMinutes() - d.getTimezoneOffset())
  return d.toISOString().slice(0, 16)
}

export default function PatientHistory() {
  const { patientId } = useParams<{ patientId: string }>()
  const navigate = useNavigate()

  const [patient, setPatient] = useState<Patient | null>(null)
  const [doctors, setDoctors] = useState<Doctor[]>([])
  const [encounters, setEncounters] = useState<Encounter[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showNewEncounter, setShowNewEncounter] = useState(false)

  const loadEncounters = async () => {
    if (!patientId) return
    const data = await encountersService.list({ patient_id: patientId, page_size: 200 })
    setEncounters(data?.results ?? [])
  }

  useEffect(() => {
    if (!patientId) return
    Promise.all([
      patientsService.get(patientId),
      doctorsService.list({ page: 1 }),
      encountersService.list({ patient_id: patientId, page_size: 200 }),
    ])
      .then(([p, docs, encs]) => {
        setPatient(p)
        setDoctors(docs?.results ?? [])
        setEncounters(encs?.results ?? [])
      })
      .catch(err => setError(err instanceof Error ? err.message : 'Error al cargar historial'))
      .finally(() => setLoading(false))
  }, [patientId])

  if (loading) {
    return <PageContainer title="Historial del Paciente"><p style={{ color: '#6b7280' }}>Cargando...</p></PageContainer>
  }

  return (
    <PageContainer title="Historial del Paciente">
      <button onClick={() => navigate(-1)} style={backBtn}>← Volver</button>

      {error && <ErrorBox message={error} />}

      {patient && <PatientHeader patient={patient} />}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', margin: '20px 0 12px' }}>
        <h3 style={{ margin: 0, fontSize: 16, color: '#1e293b' }}>
          Encuentros clínicos ({encounters.length})
        </h3>
        <CanAccess module="medical_records" action="create">
          <button onClick={() => setShowNewEncounter(v => !v)} style={primaryBtn}>
            {showNewEncounter ? 'Cancelar' : '+ Nueva consulta'}
          </button>
        </CanAccess>
      </div>

      {showNewEncounter && patientId && (
        <NewEncounterForm
          patientId={patientId}
          doctors={doctors}
          onCreated={() => { setShowNewEncounter(false); void loadEncounters() }}
        />
      )}

      {encounters.length === 0 ? (
        <div style={{ ...card, padding: 40, textAlign: 'center', color: '#6b7280' }}>
          <div style={{ fontSize: 36, marginBottom: 8 }}>📋</div>
          No hay encuentros registrados para este paciente.
        </div>
      ) : (
        encounters.map(enc => <EncounterCard key={enc.id} encounter={enc} doctors={doctors} />)
      )}
    </PageContainer>
  )
}

// ── Patient header ────────────────────────────────────────────────────

function PatientHeader({ patient }: { patient: Patient }) {
  return (
    <div style={card}>
      <div style={{ padding: '16px 20px', display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <div style={{ fontSize: 18, fontWeight: 700, color: '#0f172a' }}>
            {patient.first_name} {patient.last_name}
          </div>
          <div style={{ fontSize: 13, color: '#64748b', marginTop: 2 }}>
            {patient.cedula || patient.passport_number || '—'}
            {patient.age != null && ` · ${patient.age} años`}
            {patient.sex && ` · ${patient.sex}`}
          </div>
        </div>
      </div>
      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', padding: '0 20px 16px' }}>
        <MedBadge label="Tipo de sangre" value={patient.blood_type} accent="#0ea5e9" />
        <MedBadge label="Alergias" value={patient.allergies} accent="#dc2626" wide />
        <MedBadge label="Condiciones crónicas" value={patient.chronic_conditions} accent="#d97706" wide />
      </div>
    </div>
  )
}

function MedBadge({ label, value, accent, wide }: { label: string; value: string; accent: string; wide?: boolean }) {
  const has = value && value.trim().length > 0
  return (
    <div style={{
      flex: wide ? '1 1 240px' : '0 0 auto', minWidth: wide ? 200 : 120,
      borderLeft: `3px solid ${has ? accent : '#e2e8f0'}`,
      background: has ? '#fafafa' : 'transparent', padding: '6px 12px', borderRadius: 4,
    }}>
      <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#94a3b8', fontWeight: 600 }}>{label}</div>
      <div style={{ fontSize: 14, color: has ? '#0f172a' : '#cbd5e1', fontWeight: has ? 600 : 400 }}>
        {has ? value : 'Ninguna'}
      </div>
    </div>
  )
}

// ── New encounter form ────────────────────────────────────────────────

function NewEncounterForm({ patientId, doctors, onCreated }: { patientId: string; doctors: Doctor[]; onCreated: () => void }) {
  const [doctorId, setDoctorId] = useState('')
  const [encType, setEncType] = useState('AMBULATORIO')
  const [startAt, setStartAt] = useState(nowLocal())
  const [chiefComplaint, setChiefComplaint] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [err, setErr] = useState<string | null>(null)

  const submit = async () => {
    if (!doctorId) { setErr('Seleccione un médico'); return }
    setSubmitting(true); setErr(null)
    try {
      await encountersService.create({
        patient_id: patientId,
        doctor_id: doctorId,
        encounter_type: encType as Encounter['encounter_type'],
        start_at: new Date(startAt).toISOString(),
        chief_complaint: chiefComplaint || null,
      })
      onCreated()
    } catch (e) {
      setErr(e instanceof Error ? e.message : 'Error al crear el encuentro')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ ...card, padding: 16, marginBottom: 16 }}>
      {err && <ErrorBox message={err} />}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        <Field label="Médico">
          <select value={doctorId} onChange={e => setDoctorId(e.target.value)} style={input}>
            <option value="">Seleccione...</option>
            {doctors.map(d => <option key={d.id} value={d.id}>{d.first_name} {d.last_name}</option>)}
          </select>
        </Field>
        <Field label="Tipo">
          <select value={encType} onChange={e => setEncType(e.target.value)} style={input}>
            {Object.entries(ENCOUNTER_TYPES).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
          </select>
        </Field>
        <Field label="Inicio">
          <input type="datetime-local" value={startAt} onChange={e => setStartAt(e.target.value)} style={input} />
        </Field>
        <Field label="Motivo de consulta">
          <input value={chiefComplaint} onChange={e => setChiefComplaint(e.target.value)} style={input} placeholder="Opcional" />
        </Field>
      </div>
      <button onClick={submit} disabled={submitting} style={{ ...primaryBtn, marginTop: 12 }}>
        {submitting ? 'Guardando...' : 'Crear encuentro'}
      </button>
    </div>
  )
}

// ── Encounter card (expandable) ───────────────────────────────────────

function EncounterCard({ encounter, doctors }: { encounter: Encounter; doctors: Doctor[] }) {
  const [open, setOpen] = useState(false)
  const [loaded, setLoaded] = useState(false)
  const [vitals, setVitals] = useState<VitalSign[]>([])
  const [notes, setNotes] = useState<ClinicalNote[]>([])
  const [diagnoses, setDiagnoses] = useState<Diagnosis[]>([])
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([])

  const reload = async () => {
    const [v, n, d, p] = await Promise.all([
      vitalSignsService.list({ encounter_id: encounter.id, page_size: 100 }),
      clinicalNotesService.list({ encounter_id: encounter.id, page_size: 100 }),
      diagnosesService.list({ encounter_id: encounter.id, page_size: 100 }),
      prescriptionsService.list({ encounter_id: encounter.id, page_size: 100 }),
    ])
    setVitals(v?.results ?? [])
    setNotes(n?.results ?? [])
    setDiagnoses(d?.results ?? [])
    setPrescriptions(p?.results ?? [])
    setLoaded(true)
  }

  const toggle = () => {
    const next = !open
    setOpen(next)
    if (next && !loaded) void reload()
  }

  const st = ENCOUNTER_STATUS[encounter.status] || { label: encounter.status, color: '#6b7280', bg: '#f3f4f6' }

  return (
    <div style={{ ...card, marginBottom: 12 }}>
      <div onClick={toggle} style={{ padding: '14px 18px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}>
        <div>
          <div style={{ fontWeight: 600, color: '#0f172a' }}>
            {ENCOUNTER_TYPES[encounter.encounter_type] || encounter.encounter_type}
            <span style={{ fontWeight: 400, color: '#64748b', marginLeft: 8, fontSize: 13 }}>{fmtDateTime(encounter.start_at)}</span>
          </div>
          <div style={{ fontSize: 13, color: '#64748b', marginTop: 2 }}>
            Dr. {encounter.doctor?.first_name} {encounter.doctor?.last_name}
            {encounter.chief_complaint && ` · ${encounter.chief_complaint}`}
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ padding: '3px 12px', borderRadius: 20, fontSize: 12, fontWeight: 600, color: st.color, background: st.bg }}>{st.label}</span>
          <span style={{ color: '#94a3b8' }}>{open ? '▲' : '▼'}</span>
        </div>
      </div>

      {open && (
        <div style={{ borderTop: '1px solid #f1f5f9', padding: 18, background: '#fcfcfd' }}>
          {!loaded ? <p style={{ color: '#94a3b8' }}>Cargando...</p> : (
            <>
              <Section title="Diagnósticos">
                {diagnoses.length === 0 ? <Empty /> : diagnoses.map(d => (
                  <Row key={d.id}>
                    <strong>{d.icd10_code}</strong> — {d.description}
                    <span style={tag}>{d.diagnosis_type}{d.is_primary ? ' · Principal' : ''}</span>
                  </Row>
                ))}
                <CanAccess module="medical_records" action="create">
                  <DiagnosisForm encounterId={encounter.id} onCreated={reload} />
                </CanAccess>
              </Section>

              <Section title="Prescripciones">
                {prescriptions.length === 0 ? <Empty /> : prescriptions.map(p => (
                  <Row key={p.id}>
                    <strong>{p.medication_name}</strong> · {p.dose} · {p.frequency} · {p.route}
                    <span style={tag}>{p.status}</span>
                  </Row>
                ))}
                <CanAccess module="medical_records" action="create">
                  <PrescriptionForm encounterId={encounter.id} onCreated={reload} />
                </CanAccess>
              </Section>

              <Section title="Notas clínicas">
                {notes.length === 0 ? <Empty /> : notes.map(n => (
                  <div key={n.id} style={{ ...rowStyle, flexDirection: 'column', alignItems: 'flex-start' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
                      <span><strong>{n.note_type}</strong> <span style={tag}>{n.status}</span></span>
                      {n.status === 'BORRADOR' && (
                        <CanAccess module="medical_records" action="sign">
                          <SignButton noteId={n.id} onSigned={reload} />
                        </CanAccess>
                      )}
                    </div>
                    <div style={{ color: '#475569', marginTop: 4, whiteSpace: 'pre-wrap' }}>{n.content}</div>
                    {n.signed_by_name && <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 4 }}>Firmada por {n.signed_by_name} · {n.signed_at && fmtDateTime(n.signed_at)}</div>}
                  </div>
                ))}
                <CanAccess module="medical_records" action="create">
                  <NoteForm encounter={encounter} doctors={doctors} onCreated={reload} />
                </CanAccess>
              </Section>

              <Section title="Signos vitales">
                {vitals.length === 0 ? <Empty /> : vitals.map(v => (
                  <Row key={v.id}>
                    {[
                      v.temperature_c && `T ${v.temperature_c}°C`,
                      (v.bp_systolic && v.bp_diastolic) && `PA ${v.bp_systolic}/${v.bp_diastolic}`,
                      v.heart_rate && `FC ${v.heart_rate}`,
                      v.oxygen_saturation && `SpO₂ ${v.oxygen_saturation}%`,
                      v.weight_kg && `${v.weight_kg}kg`,
                      v.bmi && `IMC ${v.bmi}`,
                    ].filter(Boolean).join(' · ') || '—'}
                    <span style={{ ...tag, fontSize: 11 }}>{fmtDateTime(v.recorded_at)}</span>
                  </Row>
                ))}
                <CanAccess module="medical_records" action="create">
                  <VitalsForm encounterId={encounter.id} onCreated={reload} />
                </CanAccess>
              </Section>
            </>
          )}
        </div>
      )}
    </div>
  )
}

// ── Per-section forms ─────────────────────────────────────────────────

function DiagnosisForm({ encounterId, onCreated }: { encounterId: string; onCreated: () => void }) {
  const [code, setCode] = useState('')
  const [desc, setDesc] = useState('')
  const [type, setType] = useState('PRINCIPAL')
  const [busy, setBusy] = useState(false)
  const submit = async () => {
    if (!code.trim() || !desc.trim()) return
    setBusy(true)
    try {
      await diagnosesService.create({ encounter: encounterId, icd10_code: code, description: desc, diagnosis_type: type, is_primary: type === 'PRINCIPAL' })
      setCode(''); setDesc(''); onCreated()
    } finally { setBusy(false) }
  }
  return (
    <InlineForm>
      <input value={code} onChange={e => setCode(e.target.value)} placeholder="CIE-10" style={{ ...input, width: 90 }} />
      <input value={desc} onChange={e => setDesc(e.target.value)} placeholder="Descripción" style={{ ...input, flex: 1 }} />
      <select value={type} onChange={e => setType(e.target.value)} style={{ ...input, width: 140 }}>
        {DIAGNOSIS_TYPES.map(([k, v]) => <option key={k} value={k}>{v}</option>)}
      </select>
      <button onClick={submit} disabled={busy} style={addBtn}>Agregar</button>
    </InlineForm>
  )
}

function PrescriptionForm({ encounterId, onCreated }: { encounterId: string; onCreated: () => void }) {
  const [med, setMed] = useState('')
  const [dose, setDose] = useState('')
  const [freq, setFreq] = useState('')
  const [route, setRoute] = useState('ORAL')
  const [busy, setBusy] = useState(false)
  const submit = async () => {
    if (!med.trim() || !dose.trim() || !freq.trim()) return
    setBusy(true)
    try {
      await prescriptionsService.create({ encounter: encounterId, medication_name: med, dose, frequency: freq, route })
      setMed(''); setDose(''); setFreq(''); onCreated()
    } finally { setBusy(false) }
  }
  return (
    <InlineForm>
      <input value={med} onChange={e => setMed(e.target.value)} placeholder="Medicamento" style={{ ...input, flex: 1 }} />
      <input value={dose} onChange={e => setDose(e.target.value)} placeholder="Dosis" style={{ ...input, width: 90 }} />
      <input value={freq} onChange={e => setFreq(e.target.value)} placeholder="Frecuencia" style={{ ...input, width: 120 }} />
      <select value={route} onChange={e => setRoute(e.target.value)} style={{ ...input, width: 120 }}>
        {ROUTES.map(([k, v]) => <option key={k} value={k}>{v}</option>)}
      </select>
      <button onClick={submit} disabled={busy} style={addBtn}>Agregar</button>
    </InlineForm>
  )
}

function NoteForm({ encounter, doctors, onCreated }: { encounter: Encounter; doctors: Doctor[]; onCreated: () => void }) {
  const [type, setType] = useState('EVOLUCION')
  const [content, setContent] = useState('')
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState<string | null>(null)
  // Default the note's doctor to the encounter's doctor.
  const doctorId = encounter.doctor?.id || doctors[0]?.id
  const submit = async () => {
    if (!content.trim()) return
    if (!doctorId) { setErr('No hay médico disponible para la nota'); return }
    setBusy(true); setErr(null)
    try {
      await clinicalNotesService.create({ encounter: encounter.id, doctor: doctorId, note_type: type, content })
      setContent(''); onCreated()
    } catch (e) {
      setErr(e instanceof Error ? e.message : 'Error al crear la nota')
    } finally { setBusy(false) }
  }
  return (
    <div style={{ marginTop: 10 }}>
      {err && <ErrorBox message={err} />}
      <div style={{ display: 'flex', gap: 8, marginBottom: 6 }}>
        <select value={type} onChange={e => setType(e.target.value)} style={{ ...input, width: 200 }}>
          {NOTE_TYPES.map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
      </div>
      <textarea value={content} onChange={e => setContent(e.target.value)} placeholder="Contenido de la nota..." rows={3} style={{ ...input, width: '100%', resize: 'vertical' }} />
      <button onClick={submit} disabled={busy} style={{ ...addBtn, marginTop: 6 }}>Guardar nota</button>
    </div>
  )
}

function VitalsForm({ encounterId, onCreated }: { encounterId: string; onCreated: () => void }) {
  const [f, setF] = useState({ temperature_c: '', bp_systolic: '', bp_diastolic: '', heart_rate: '', oxygen_saturation: '', weight_kg: '', height_cm: '' })
  const [busy, setBusy] = useState(false)
  const set = (k: keyof typeof f) => (e: React.ChangeEvent<HTMLInputElement>) => setF({ ...f, [k]: e.target.value })
  const submit = async () => {
    const payload: Record<string, unknown> = { encounter: encounterId }
    Object.entries(f).forEach(([k, v]) => { if (v !== '') payload[k] = v })
    if (Object.keys(payload).length === 1) return
    setBusy(true)
    try {
      await vitalSignsService.create(payload as never)
      setF({ temperature_c: '', bp_systolic: '', bp_diastolic: '', heart_rate: '', oxygen_saturation: '', weight_kg: '', height_cm: '' })
      onCreated()
    } finally { setBusy(false) }
  }
  return (
    <InlineForm>
      <input value={f.temperature_c} onChange={set('temperature_c')} placeholder="T °C" style={{ ...input, width: 70 }} />
      <input value={f.bp_systolic} onChange={set('bp_systolic')} placeholder="PA sis" style={{ ...input, width: 70 }} />
      <input value={f.bp_diastolic} onChange={set('bp_diastolic')} placeholder="PA dia" style={{ ...input, width: 70 }} />
      <input value={f.heart_rate} onChange={set('heart_rate')} placeholder="FC" style={{ ...input, width: 60 }} />
      <input value={f.oxygen_saturation} onChange={set('oxygen_saturation')} placeholder="SpO₂" style={{ ...input, width: 70 }} />
      <input value={f.weight_kg} onChange={set('weight_kg')} placeholder="Peso kg" style={{ ...input, width: 80 }} />
      <input value={f.height_cm} onChange={set('height_cm')} placeholder="Talla cm" style={{ ...input, width: 80 }} />
      <button onClick={submit} disabled={busy} style={addBtn}>Agregar</button>
    </InlineForm>
  )
}

function SignButton({ noteId, onSigned }: { noteId: string; onSigned: () => void }) {
  const [busy, setBusy] = useState(false)
  const sign = async () => {
    setBusy(true)
    try { await clinicalNotesService.sign(noteId); onSigned() } finally { setBusy(false) }
  }
  return <button onClick={sign} disabled={busy} style={{ ...addBtn, background: '#047857' }}>{busy ? '...' : 'Firmar'}</button>
}

// ── Small presentational helpers ──────────────────────────────────────

const Section = ({ title, children }: { title: string; children: React.ReactNode }) => (
  <div style={{ marginBottom: 18 }}>
    <div style={{ fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#64748b', marginBottom: 6 }}>{title}</div>
    {children}
  </div>
)
const Row = ({ children }: { children: React.ReactNode }) => <div style={rowStyle}>{children}</div>
const Empty = () => <div style={{ color: '#cbd5e1', fontSize: 13, padding: '4px 0' }}>Sin registros</div>
const InlineForm = ({ children }: { children: React.ReactNode }) => (
  <div style={{ display: 'flex', gap: 8, marginTop: 8, flexWrap: 'wrap', alignItems: 'center' }}>{children}</div>
)
const Field = ({ label, children }: { label: string; children: React.ReactNode }) => (
  <label style={{ display: 'flex', flexDirection: 'column', gap: 4, fontSize: 13, color: '#475569' }}>{label}{children}</label>
)
const ErrorBox = ({ message }: { message: string }) => (
  <div style={{ background: '#fef2f2', border: '1px solid #fecaca', color: '#991b1b', padding: '10px 14px', borderRadius: 8, marginBottom: 12, fontSize: 14 }}>{message}</div>
)

// ── Styles ────────────────────────────────────────────────────────────

const card: React.CSSProperties = { background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, overflow: 'hidden' }
const rowStyle: React.CSSProperties = { display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8, padding: '6px 0', borderBottom: '1px solid #f1f5f9', fontSize: 14, color: '#334155' }
const input: React.CSSProperties = { padding: '8px 10px', borderRadius: 6, border: '1px solid #d1d5db', fontSize: 14 }
const tag: React.CSSProperties = { marginLeft: 8, fontSize: 11, color: '#64748b', background: '#f1f5f9', padding: '2px 8px', borderRadius: 12 }
const primaryBtn: React.CSSProperties = { padding: '8px 16px', borderRadius: 8, border: 'none', background: '#2563eb', color: '#fff', fontWeight: 600, fontSize: 14, cursor: 'pointer' }
const addBtn: React.CSSProperties = { padding: '8px 14px', borderRadius: 6, border: 'none', background: '#2563eb', color: '#fff', fontWeight: 600, fontSize: 13, cursor: 'pointer' }
const backBtn: React.CSSProperties = { background: 'none', border: 'none', color: '#2563eb', cursor: 'pointer', fontSize: 14, padding: 0, marginBottom: 12 }
