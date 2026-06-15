import type { ActionKey, ModuleKey, PermissionContext, User } from '../../types'
import { hasRolePermission } from './permissions'

export function can(user: User | null, action: ActionKey, module: ModuleKey, context?: PermissionContext): boolean {
  if (!user) return false

  if (user.role === 'ADMINISTRATOR') return hasRolePermission(user.role, module, action)

  if (!hasRolePermission(user.role, module, action)) return false

  if (module === 'appointments' || module === 'patients' || module === 'medical_records') {
    // Viewing is allowed for any role holding the permission (checked above);
    // ownership/assignment is only enforced for editing.
    if (action === 'edit') {
      if (context?.isOwner === true || context?.isAssigned === true) return true
      if (user.role === 'SECRETARY' || user.role === 'RECEPTIONIST') return true
      return false
    }
  }

  return true
}

export function canAccessRoute(user: User | null, module: ModuleKey): boolean {
  return can(user, 'view', module)
}
