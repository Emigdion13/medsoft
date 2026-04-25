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
