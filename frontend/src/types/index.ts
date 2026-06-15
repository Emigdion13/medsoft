export type UserRole =
  | 'DOCTOR'
  | 'SECRETARY'
  | 'ADMINISTRATOR'
  | 'RECEPTIONIST'
  | 'NURSE'
  | 'LAB_TECHNICIAN'

export interface User {
  id: string // UUID as string
  username: string
  first_name: string
  last_name: string
  email: string
  role: UserRole
  is_active: boolean
}

export interface AuthTokens {
  access: string
  refresh: string
}

export interface AuthResponse extends AuthTokens {
  user: User
}

export interface LoginPayload {
  username: string
  password: string
}

export interface RegisterPayload {
  username: string
  email: string
  first_name: string
  last_name: string
  role: UserRole
  password: string
  confirm_password: string
}

export type ModuleKey =
  | 'dashboard'
  | 'appointments'
  | 'patients'
  | 'medical_records'
  | 'users'

export type ActionKey = 'view' | 'create' | 'edit' | 'delete' | 'sign'

export interface PermissionContext {
  isOwner?: boolean
  isAssigned?: boolean
}

export interface PermissionsMatrix {
  [module: string]: ActionKey[]
}

export interface ApiError {
  detail?: string
  message?: string
  [key: string]: unknown
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface UserListItem {
  id: string
  username: string
  first_name: string
  last_name: string
  email: string
  phone: string | null
  role: UserRole
  is_active: boolean
}

// ── Specialty ─────────────────────────────────────────────────────────

export interface Specialty {
  id: string
  code: string
  name: string
  description: string | null
  is_active: boolean
}

// ── Doctor ────────────────────────────────────────────────────────────

export interface Doctor {
  id: string
  cedula: string
  license_number: string
  medical_college_number: string
  first_name: string
  last_name: string
  specialty_main: Specialty | null
  specialty_main_id: string
  phone: string
  email: string
  office_room: string
  is_active: boolean
}

// ── Patient ───────────────────────────────────────────────────────────

export interface Patient {
  id: string
  identity_type: string
  cedula: string
  passport_number: string | null
  first_name: string
  last_name: string
  birth_date: string | null
  age: number | null
  sex: string
  nationality: string
  phone_primary: string
  phone_secondary: string | null
  email: string
  address: string
  province: string
  municipality: string
  blood_type: string
  allergies: string
  chronic_conditions: string
  emergency_contact_name: string
  emergency_contact_phone: string
  emergency_contact_relation: string
  ars_provider: string
  ars_affiliation_number: string
  status: string
}

// ── Appointment ───────────────────────────────────────────────────────

export type AppointmentType = 'CONSULTA' | 'CONTROL' | 'EMERGENCIA' | 'SEGUIMIENTO'
export type AppointmentStatus = 'PROGRAMADA' | 'CONFIRMADA' | 'EN_CURSO' | 'COMPLETADA' | 'CANCELADA' | 'NO_ASISTIO'

export interface Appointment {
  id: string
  doctor: Doctor
  doctor_id: string
  patient: Patient
  patient_id: string
  start_at: string
  end_at: string
  appointment_type: AppointmentType
  reason: string
  status: AppointmentStatus
  notes: string
  created_by: string
  created_at: string
  updated_at: string
}

export interface CreateAppointmentPayload {
  doctor_id: string
  patient_id: string
  start_at: string
  end_at: string
  appointment_type: AppointmentType
  reason: string
  notes?: string
}

// ── Clinical / Medical history ────────────────────────────────────────

export type EncounterType = 'AMBULATORIO' | 'INTERNAMIENTO' | 'EMERGENCIA' | 'TELECONSULTA'
export type EncounterStatus = 'ABIERTO' | 'CERRADO' | 'CANCELADO'
export type NoteType = 'EVOLUCION' | 'HISTORIA' | 'NOTA_ENFERMERIA' | 'NOTA_MEDICA'
export type NoteStatus = 'BORRADOR' | 'FIRMADA' | 'ANULADA'
export type DiagnosisType = 'PRINCIPAL' | 'SECUNDARIO' | 'COMORBILIDAD'
export type DiagnosisStatus = 'ACTIVO' | 'RESUELTO' | 'CANCELADO'
export type PrescriptionRoute =
  | 'ORAL' | 'IV' | 'IM' | 'TOPICA' | 'INHALADA' | 'NASAL' | 'OTICO' | 'OCULAR'
export type PrescriptionStatus = 'ACTIVA' | 'SUSPENDIDA' | 'COMPLETADA' | 'CANCELADA'

interface PatientLookup { id: string; first_name: string; last_name: string; cedula: string }
interface DoctorLookup { id: string; first_name: string; last_name: string; cedula: string }
interface AppointmentLookup { id: string; start_at: string; end_at: string | null; reason: string }

export interface Encounter {
  id: string
  patient: PatientLookup
  doctor: DoctorLookup
  appointment: AppointmentLookup | null
  encounter_type: EncounterType
  status: EncounterStatus
  start_at: string
  end_at: string | null
  chief_complaint: string | null
  room_number: string | null
  bed_number: string | null
  admission_source: string | null
  discharge_reason: string | null
  created_by_name: string | null
  updated_by_name: string | null
  created_at: string
  updated_at: string
}

export interface CreateEncounterPayload {
  patient_id: string
  doctor_id: string
  appointment_id?: string | null
  encounter_type: EncounterType
  status?: EncounterStatus
  start_at: string
  end_at?: string | null
  chief_complaint?: string | null
}

export interface VitalSign {
  id: string
  encounter: string
  recorded_by_name: string | null
  recorded_at: string
  temperature_c: string | null
  bp_systolic: number | null
  bp_diastolic: number | null
  heart_rate: number | null
  respiratory_rate: number | null
  oxygen_saturation: string | null
  weight_kg: string | null
  height_cm: string | null
  bmi: string | null
  glucose_mg_dl: string | null
  notes: string | null
}

export interface ClinicalNote {
  id: string
  encounter: string
  doctor: string
  note_type: NoteType
  content: string
  status: NoteStatus
  signed_by: string | null
  signed_by_name: string | null
  signed_at: string | null
  content_hash: string | null
  created_by_name: string | null
  created_at: string
  updated_at: string
}

export interface Diagnosis {
  id: string
  encounter: string
  icd10_code: string
  description: string
  diagnosis_type: DiagnosisType
  is_primary: boolean
  status: DiagnosisStatus
  recorded_by_name: string | null
  recorded_at: string
}

export interface Prescription {
  id: string
  encounter: string
  medication_name: string
  medication_code: string | null
  dose: string
  frequency: string
  route: PrescriptionRoute
  duration_days: number | null
  quantity: number | null
  instructions: string | null
  status: PrescriptionStatus
  prescribed_by_name: string | null
  prescribed_at: string
}
