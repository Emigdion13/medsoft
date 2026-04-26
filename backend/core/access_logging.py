"""
Access logging utilities for MediSoft Django application.

Provides decorators and helpers for tracking access to sensitive resources.
"""

from functools import wraps

from core.models import AccessLog


def log_access(
    resource_type: str,
    access_type: str = 'VIEW',
    description: str = None
):
    """
    Decorator to log access to sensitive resources.
    
    Usage:
        @log_access(resource_type='PATIENT_RECORD', access_type='VIEW')
        def view_patient(request, patient_id):
            ...
        
        @log_access(resource_type='PRESCRIPTION', access_type='EDIT')
        def edit_prescription(request, prescription_id):
            ...
    
    Args:
        resource_type: Type of sensitive resource (from AccessLog choices)
        access_type: Type of access being performed
        description: Optional description for the log entry
    
    Returns:
        Decorated function wrapper
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = getattr(request, 'user', None)
            
            # Get resource ID if available from kwargs
            resource_id = kwargs.get('patient_id') or kwargs.get('id')
            if not resource_id:
                resource_id = kwargs.get('pk')
            
            # Try to get IP address
            ip_address = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            try:
                # Log the access before calling view
                AccessLog.create_access_log(
                    user=user,
                    access_type=access_type,
                    resource_type=resource_type,
                    resource_id=str(resource_id) if resource_id else None,
                    description=description or f"{access_type} {resource_type}",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    successful=True,
                )
            except Exception:
                # Don't fail the request if logging fails
                pass
            
            return view_func(request, *args, **kwargs)
        
        return _wrapped_view
    
    return decorator


def log_sensitive_access(
    resource_type: str,
    access_type: str = 'VIEW'
):
    """
    Decorator for sensitive data access with enhanced logging.
    
    Logs both successful and failed access attempts.
    Used for HIPAA-compliant applications where access tracking is critical.
    
    Args:
        resource_type: Type of sensitive resource
        access_type: Type of access being performed
    
    Returns:
        Decorated function wrapper
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = getattr(request, 'user', None)
            
            # Check authentication before proceeding
            if not user or not user.is_authenticated:
                AccessLog.create_access_log(
                    user=None,
                    access_type=access_type,
                    resource_type=resource_type,
                    successful=False,
                    description="Access denied: Not authenticated",
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                )
                from django.core.exceptions import PermissionDenied
                raise PermissionDenied("Authentication required")
            
            # Check permissions if RBAC is implemented
            # (This would integrate with your permission system)
            
            resource_id = kwargs.get('patient_id') or kwargs.get('id')
            ip_address = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            try:
                AccessLog.create_access_log(
                    user=user,
                    access_type=access_type,
                    resource_type=resource_type,
                    resource_id=str(resource_id) if resource_id else None,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    successful=True,
                )
            except Exception:
                pass
            
            return view_func(request, *args, **kwargs)
        
        return _wrapped_view
    
    return decorator


def log_view_access(model_class):
    """
    Decorator for model detail views to log viewing of records.
    
    Usage:
        @log_view_access(Patient)
        def patient_detail(request, pk):
            ...
    
    Args:
        model_class: The model class being accessed
    
    Returns:
        Decorated view function
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, pk, *args, **kwargs):
            user = getattr(request, 'user', None)
            ip_address = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            try:
                AccessLog.create_access_log(
                    user=user,
                    access_type='VIEW',
                    resource_type=f'{model_class.__name__.upper()}_RECORD',
                    resource_id=str(pk),
                    ip_address=ip_address,
                    user_agent=user_agent,
                    successful=True,
                )
            except Exception:
                pass
            
            return view_func(request, pk, *args, **kwargs)
        
        return _wrapped_view
    
    return decorator


def log_export_access(resource_type: str):
    """
    Decorator to log data export operations.
    
    Usage:
        @log_export_access(resource_type='PATIENT_RECORD')
        def export_patients(request):
            ...
    
    Args:
        resource_type: Type of resource being exported
    
    Returns:
        Decorated function wrapper
    """
    return log_sensitive_access(
        resource_type=resource_type,
        access_type='EXPORT'
    )


def track_access_in_view(view_func):
    """
    Track access in any view without arguments.
    
    This is a simpler decorator that just ensures the AccessLog model
    receives an entry when the view is called.
    
    Usage:
        @track_access_in_view
        def some_view(request):
            ...
    
    Args:
        view_func: The view function to decorate
    
    Returns:
        Decorated function wrapper
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = getattr(request, 'user', None)
        
        if user and user.is_authenticated:
            try:
                AccessLog.create_access_log(
                    user=user,
                    access_type='VIEW',
                    resource_type='GENERIC_VIEW',
                    description=f"View accessed: {view_func.__name__}",
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    successful=True,
                )
            except Exception:
                pass
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view
