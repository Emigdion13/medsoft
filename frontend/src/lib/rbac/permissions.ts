import type { ActionKey, ModuleKey, PermissionsMatrix, UserRole } from '../../types'

export const ROLE_PERMISSIONS: Record<UserRole, PermissionsMatrix> = {
  DOCTOR: {
    dashboard: ['view'],
    appointments: ['view', 'edit'],
    patients: ['view'],
    medical_records: ['view', 'create', 'edit', 'sign'],
    users: [],
  },
  NURSE: {
    dashboard: ['view'],
    appointments: ['view', 'edit'],
    patients: ['view'],
    medical_records: ['view', 'create', 'edit'],
    users: [],
  },
  SECRETARY: {
    dashboard: ['view'],
    appointments: ['view', 'create', 'edit', 'delete'],
    patients: ['view', 'create', 'edit'],
    medical_records: [],
    users: [],
  },
  RECEPTIONIST: {
    dashboard: ['view'],
    appointments: ['view', 'create', 'edit'],
    patients: ['view', 'create', 'edit'],
    medical_records: [],
    users: [],
  },
  LAB_TECHNICIAN: {
    dashboard: ['view'],
    appointments: ['view'],
    patients: ['view'],
    medical_records: ['view'],
    users: [],
  },
  ADMINISTRATOR: {
    dashboard: ['view'],
    appointments: ['view', 'create', 'edit', 'delete'],
    patients: ['view', 'create', 'edit', 'delete'],
    medical_records: ['view', 'create', 'edit', 'delete', 'sign'],
    users: ['view', 'create', 'edit', 'delete'],
  },
}

export function hasRolePermission(role: UserRole, module: ModuleKey, action: ActionKey): boolean {
  return ROLE_PERMISSIONS[role][module]?.includes(action) ?? false
}
