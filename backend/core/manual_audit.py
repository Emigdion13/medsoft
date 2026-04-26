"""
Simplified audit logging utilities for MediSoft Django application.

Provides context managers and decorators for manual audit log creation.
"""

from datetime import datetime

try:
    from core.models import AuditLog
except ImportError:
    # Fallback when models aren't loaded yet
    AuditLog = None


def log_audit_event(
    user,
    action: str,
    model: str,
    object_id: str = None,
    description: str = None,
    changes: dict = None,
    snapshot: dict = None,
    ip_address: str = None,
):
    """
    Log an audit event directly without signals.
    
    This is useful when you want to log actions that don't fit
    the standard create/update/delete pattern.
    
    Args:
        user: User instance or None for system actions
        action: Action type (e.g., 'LOGIN', 'LOGOUT', 'CONFIG_CHANGE')
        model: Model name affected by the action
        object_id: ID of the specific record affected
        description: Detailed description of what happened
        changes: Dictionary of field changes for updates
        snapshot: Snapshot of data at time of action
        ip_address: Client IP address where action occurred
    
    Returns:
        The created AuditLog instance (or None if model not loaded)
    """
    if AuditLog is None:
        return None
    
    try:
        return AuditLog.objects.create(
            user=user,
            action=action,
            model=model,
            object_id=str(object_id) if object_id else '',
            description=description or f'{action} {model}',
            changes=changes or {},
            snapshot=snapshot or {},
            ip_address=ip_address,
        )
    except Exception:
        # Don't fail the operation if logging fails
        return None


class AuditContextManager:
    """
    Context manager for grouping related audit events.
    
    Usage:
        with AuditContextManager(user, 'PATIENT_UPDATE', 'Patient: 123') as ctx:
            patient.save()
            log_audit_event(ctx.user, 'UPDATE_FIELD', 'Patient', changes={'name': old_name})
            
            # All events share the same context
    
    Args:
        user: User performing the actions
        group_name: Name for this audit group
        description: Description of the overall action
    """
    
    def __init__(
        self,
        user,
        group_name: str = None,
        description: str = None,
    ):
        self.user = user
        self.group_name = group_name or f'Audit_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        self.description = description
        self.events = []
        self.start_time = datetime.now()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Log the overall group completion
        if exc_type is None:
            # Success - log group completion
            self._log_group_event('COMPLETED', 'Audit group completed successfully')
        else:
            # Error - log failure
            self._log_group_event(
                'FAILED',
                f'Audit group failed: {str(exc_val)}'
            )
        
        return False  # Don't suppress exceptions
    
    def _log_group_event(
        self,
        action: str,
        description: str,
        **kwargs,
    ):
        """Log an event within the audit context."""
        event = log_audit_event(
            user=self.user,
            action=action,
            model='AUDIT_GROUP',
            object_id=self.group_name,
            description=f'{self.description}: {description}' if self.description else description,
            **kwargs,
        )
        if event:
            self.events.append(event)
    
    def log(
        self,
        action: str,
        model: str,
        object_id: str = None,
        description: str = None,
        **kwargs,
    ):
        """
        Log an audit event within this context.
        
        Args:
            action: Action type
            model: Model affected
            object_id: ID of record affected
            description: Event description
            **kwargs: Additional log_audit_event arguments
        
        Returns:
            Created AuditLog instance or None
        """
        return self._log_group_event(action, description or f'{action} {model}', kwargs)


def audit_action(
    user,
    action: str,
    model: str,
    object_id: str = None,
):
    """
    Decorator for logging specific actions.
    
    Usage:
        @audit_action(user, 'EXPORT', 'PATIENT_LIST')
        def export_patients(request):
            ...
    
    Args:
        user: User performing the action
        action: Type of action being performed
        model: Model or resource being acted upon
        object_id: ID of specific record (optional)
    
    Returns:
        Decorated function wrapper
    """
    def decorator(view_func):
        from functools import wraps
        
        @wraps(view_func)
        def _wrapped_view(*args, **kwargs):
            log_audit_event(
                user=user,
                action=action,
                model=model,
                object_id=str(object_id) if object_id else None,
                description=f'{action} on {model}',
            )
            return view_func(*args, **kwargs)
        
        return _wrapped_view
    
    return decorator


def track_model_changes(model_class):
    """
    Decorator to automatically log all changes to a model.
    
    This wraps the save() and delete() methods to create audit logs.
    
    Usage:
        @track_model_changes(Patient)
        class Patient(models.Model):
            ...
    
    Args:
        model_class: The model class to track
    
    Returns:
        Modified model class with audited methods
    """
    original_save = model_class.save
    original_delete = model_class.delete
    
    def audited_save(self, *args, **kwargs):
        is_new = self.pk is None
        
        # Call original save
        result = original_save(self, *args, **kwargs)
        
        # Log the action
        if is_new:
            action = 'CREATE'
            description = f'Created {model_class.__name__}'
        else:
            action = 'UPDATE'
            description = f'Updated {model_class.__name__}'
        
        log_audit_event(
            user=getattr(self, '_audit_user', None),
            action=action,
            model=model_class.__name__,
            object_id=str(self.pk) if self.pk else '',
            description=description,
        )
        
        return result
    
    def audited_delete(self, *args, **kwargs):
        # Log before deletion
        log_audit_event(
            user=getattr(self, '_audit_user', None),
            action='DELETE',
            model=model_class.__name__,
            object_id=str(self.pk) if self.pk else '',
            description=f'Deleted {model_class.__name__}',
        )
        
        return original_delete(self, *args, **kwargs)
    
    model_class.save = audited_save
    model_class.delete = audited_delete
    
    return model_class
