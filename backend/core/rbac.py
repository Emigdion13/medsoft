"""
Role-Based Access Control (RBAC) utilities for MediSoft.

Provides permission checking functions and decorators.
"""

from functools import wraps

from django.core.exceptions import PermissionDenied

# Predefined permissions as constants
PERMISSIONS = {
    # Patient management
    'patient.view': 'Can view patient records',
    'patient.create': 'Can create patient records',
    'patient.update': 'Can update patient records',
    'patient.delete': 'Can soft-delete patient records',
    'patient.import': 'Can import patients (CSV/batch)',
    
    # Doctor management
    'doctor.view': 'Can view doctor profiles',
    'doctor.create': 'Can create doctor profiles',
    'doctor.update': 'Can update doctor profiles',
    
    # Appointment management
    'appointment.view': 'Can view appointments',
    'appointment.create': 'Can create appointments',
    'appointment.update': 'Can update appointments',
    'appointment.cancel': 'Can cancel appointments',
    
    # Encounter management
    'encounter.view': 'Can view patient encounters',
    'encounter.create': 'Can create encounters',
    'encounter.update': 'Can update encounters',
    'encounter.close': 'Can close encounters',
    
    # Clinical records
    'clinical.note.view': 'Can view clinical notes',
    'clinical.note.create': 'Can create clinical notes',
    'clinical.note.sign': 'Can sign clinical notes (legal)',
    'clinical.note.edit_signed': 'Can edit signed notes',
    
    # Diagnosis management
    'diagnosis.view': 'Can view diagnoses',
    'diagnosis.create': 'Can add diagnoses',
    'diagnosis.update': 'Can update diagnoses',
    
    # Prescription management
    'prescription.view': 'Can view prescriptions',
    'prescription.create': 'Can create prescriptions',
    'prescription.edit': 'Can edit prescriptions',
    'prescription.dispense': 'Can mark prescriptions as dispensed',
    
    # Lab orders
    'lab.order.view': 'Can view lab orders',
    'lab.order.create': 'Can create lab orders',
    'lab.order.cancel': 'Can cancel lab orders',
    'lab.result.view': 'Can view lab results',
    'lab.result.enter': 'Can enter lab results',
    
    # Imaging orders
    'imaging.order.view': 'Can view imaging orders',
    'imaging.order.create': 'Can create imaging orders',
    'imaging.report.view': 'Can view imaging reports',
    'imaging.report.sign': 'Can sign imaging reports (radiologist)',
    
    # Billing/finance
    'billing.view': 'Can view billing records',
    'billing.create': 'Can create billing records',
    'billing.update': 'Can update billing records',
    'billing.see_full_amounts': 'Can see full pricing information',
    
    # Admin/system
    'admin.user_management': 'Can manage users and roles',
    'admin.role_management': 'Can manage roles and permissions',
    'admin.system_config': 'Can change system configuration',
    'admin.audit_view': 'Can view audit logs',
    
    # Sensitive data access
    'sensitive.patient_history': 'Can view complete patient history',
    'sensitive.financial_data': 'Can view financial records',
}


def check_permission(user, permission: str) -> bool:
    """
    Check if a user has a specific permission.
    
    This function checks permissions through the role hierarchy:
    1. Direct user permissions
    2. Role-based permissions
    
    Args:
        user: Django User instance (must have RBAC fields)
        permission: Permission code string (e.g., 'patient.create')
    
    Returns:
        True if user has permission, False otherwise
    
    Raises:
        ValueError: If permission code is not in predefined list
    """
    # Validate permission exists
    if permission not in PERMISSIONS:
        raise ValueError(f"Unknown permission: {permission}")
    
    # Superusers have all permissions
    if hasattr(user, 'is_superuser') and user.is_superuser:
        return True
    
    # Direct user permissions (if implemented)
    if hasattr(user, 'permissions') and permission in user.permissions:
        return True
    
    # Role-based permissions check
    if hasattr(user, 'role_assignments'):
        for assignment in user.role_assignments.all():
            role = assignment.role
            if hasattr(role, 'permissions') and permission in role.permissions.values_list('code', flat=True):
                return True
    
    return False


def has_permission(user, permission: str) -> bool:
    """
    Alias for check_permission for Django-style naming.
    
    Args:
        user: Django User instance
        permission: Permission code string
    
    Returns:
        True if user has permission
    """
    return check_permission(user, permission)


def require_permission(permission_code: str):
    """
    Decorator to require a specific permission for a view/function.
    
    Usage:
        @require_permission('patient.create')
        def create_patient_view(request):
            ...
    
    Raises:
        PermissionDenied: If user lacks the required permission
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = getattr(request, 'user', None)
            
            if not user or not user.is_authenticated:
                raise PermissionDenied("Authentication required")
            
            if not check_permission(user, permission_code):
                raise PermissionDenied(
                    f"Permission '{permission_code}' required"
                )
            
            return view_func(request, *args, **kwargs)
        
        return _wrapped_view
    
    return decorator


def has_any_permission(user, permissions: list) -> bool:
    """
    Check if user has ANY of the given permissions.
    
    Args:
        user: Django User instance
        permissions: List of permission code strings
    
    Returns:
        True if user has at least one permission
    """
    return any(check_permission(user, perm) for perm in permissions)


def has_all_permissions(user, permissions: list) -> bool:
    """
    Check if user has ALL of the given permissions.
    
    Args:
        user: Django User instance
        permissions: List of permission code strings
    
    Returns:
        True if user has all permissions
    """
    return all(check_permission(user, perm) for perm in permissions)


def get_user_permissions(user) -> set:
    """
    Get all permissions for a user (including role-based).
    
    Args:
        user: Django User instance
    
    Returns:
        Set of permission code strings
    """
    permissions = set()
    
    if hasattr(user, 'is_superuser') and user.is_superuser:
        return set(PERMISSIONS.keys())
    
    # Direct user permissions
    if hasattr(user, 'permissions'):
        permissions.update(
            user.permissions.values_list('code', flat=True)
        )
    
    # Role-based permissions
    if hasattr(user, 'role_assignments'):
        for assignment in user.role_assignments.all():
            role_perms = assignment.role.permissions.values_list('code', flat=True)
            permissions.update(role_perms)
    
    return permissions


def get_role_permissions(role) -> set:
    """
    Get all permissions assigned to a role.
    
    Args:
        role: Role instance
    
    Returns:
        Set of permission code strings
    """
    if hasattr(role, 'permissions'):
        return set(role.permissions.values_list('code', flat=True))
    return set()


def get_role_hierarchy_permissions(role) -> set:
    """
    Get permissions including any inherited permissions.
    
    Args:
        role: Role instance (with potential parent roles)
    
    Returns:
        Set of all effective permission codes
    """
    permissions = get_role_permissions(role)
    
    # If role has inheritance (parent roles), add those too
    if hasattr(role, 'inherits_from') and role.inherits_from:
        permissions.update(
            get_role_hierarchy_permissions(role.inherits_from)
        )
    
    return permissions
