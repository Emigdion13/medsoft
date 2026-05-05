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
