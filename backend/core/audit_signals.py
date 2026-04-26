"""
Audit signal handlers for MediSoft Django application.

These signals automatically create audit log entries when models are created,
updated, or soft-deleted.

Usage: Add to INSTALLED_APPS and connect signals in apps.py
"""

from django.db.models.signals import (
    pre_save, post_save, post_delete, m2m_changed
)
from django.dispatch import receiver
from django.utils import timezone

# Import after model definitions to avoid circular imports
try:
    from core.models import AuditLog
except ImportError:
    # Fallback for when models aren't loaded yet
    def setup_audit_signals():
        """Lazily connect signals when models are ready."""
        pass
else:

    @receiver(pre_save)
    def track_model_changes(sender, instance, **kwargs):
        """
        Track model changes before save.
        
        This signal is sent to all models. It captures:
        - Original values for updates
        - Creates audit log entry on save
        
        Args:
            sender: The model class
            instance: The model instance being saved
            kwargs: Additional arguments
        """
        if not hasattr(instance, '_original_values'):
            # Store original values for comparison
            instance._original_values = {}
            
            # Get all non-foreign key fields to track
            for field in sender._meta.get_fields():
                if hasattr(field, 'attname') and not field.many_to_many:
                    try:
                        instance._original_values[field.attname] = getattr(
                            instance, field.attname, None
                        )
                    except AttributeError:
                        pass

    @receiver(post_save)
    def create_audit_on_save(sender, instance, created, **kwargs):
        """
        Create audit log entry on model save.
        
        Creates different log types based on the action:
        - 'CREATE': New record created
        - 'UPDATE': Existing record modified
        """
        # Skip audit for AuditLog itself to prevent recursion
        if sender.__name__ == 'AuditLog':
            return
        
        # Skip soft delete tracking (handled in pre_delete)
        if hasattr(instance, 'deleted_at') and instance.deleted_at:
            return
        
        user = getattr(instance, '_audit_user', None)
        if user and not user.is_authenticated:
            user = None
        
        if created:
            action = 'CREATE'
            description = f"Created {sender.__name__}: {str(instance)}"
        else:
            action = 'UPDATE'
            description = f"Updated {sender.__name__}: {str(instance)}"
        
        # Get changed fields
        old_values = getattr(instance, '_original_values', {})
        changes = {}
        
        if not created and old_values:
            for field in sender._meta.get_fields():
                if hasattr(field, 'attname'):
                    new_val = getattr(instance, field.attname, None)
                    old_val = old_values.get(field.attname)
                    
                    if old_val != new_val:
                        changes[field.name] = {
                            'old': str(old_val) if old_val is not None else None,
                            'new': str(new_val) if new_val is not None else None
                        }
        
        AuditLog.objects.create(
            user=user,
            action=action,
            model=sender.__name__,
            object_id=str(instance.pk),
            description=description,
            changes=changes,
            ip_address=getattr(instance, '_audit_ip', None),
        )

    @receiver(post_delete)
    def create_audit_on_delete(sender, instance, **kwargs):
        """
        Create audit log entry on model soft-delete or hard delete.
        
        Creates a 'DELETE' log with details of the deleted record.
        """
        if sender.__name__ == 'AuditLog':
            return
        
        user = getattr(instance, '_audit_user', None)
        if user and not user.is_authenticated:
            user = None
        
        # Check if this was a soft delete (deleted_at is set)
        is_soft_delete = (
            hasattr(instance, 'deleted_at') 
            and instance.deleted_at is not None
        )
        
        action = 'SOFT_DELETE' if is_soft_delete else 'DELETE'
        description = f"{action} {sender.__name__}: {str(instance)}"
        
        # Capture record state before deletion
        record_snapshot = {}
        for field in sender._meta.get_fields():
            if hasattr(field, 'attname'):
                try:
                    value = getattr(instance, field.attname, None)
                    record_snapshot[field.name] = str(value) if value is not None else None
                except AttributeError:
                    pass
        
        AuditLog.objects.create(
            user=user,
            action=action,
            model=sender.__name__,
            object_id=str(instance.pk),
            description=description,
            snapshot=record_snapshot,
            ip_address=getattr(instance, '_audit_ip', None),
        )

    @receiver(m2m_changed)
    def track_m2m_changes(sender, instance, action, reverse, pk_set, **kwargs):
        """
        Track many-to-many relationship changes.
        
        Logs changes to many-to-many relationships for audit purposes.
        """
        if 'core.AuditLog' in str(sender) or 'AuditLog' in sender.__name__:
            return
        
        # Only log specific actions
        if action not in ['post_add', 'post_remove', 'post_clear']:
            return
        
        user = getattr(instance, '_audit_user', None)
        if user and not user.is_authenticated:
            user = None
        
        model_name = instance.__class__.__name__
        object_id = str(instance.pk)
        
        # Determine the related model
        if reverse:
            related_model = sender.__name__.split('_')[0]  # Simplified
            action_desc = f"Added to {model_name}" if action == 'post_add' else \
                         f"Removed from {model_name}"
        else:
            related_model = model_name
            action_desc = f"M2M change in {model_name}"
        
        pk_list = list(pk_set or [])
        
        AuditLog.objects.create(
            user=user,
            action='M2M_CHANGE',
            model=model_name,
            object_id=object_id,
            description=f"{action_desc}: {related_model} ({len(pk_list)} items)",
            related_object_ids=pk_list,
            ip_address=getattr(instance, '_audit_ip', None),
        )


def setup_audit_signals():
    """Connect all audit signals."""
    # Import and connect handlers
    pass


def get_current_user():
    """
    Get the current user from thread-local storage.
    
    This is typically used when no request object is available.
    
    Returns:
        User instance or None
    """
    try:
        from django.contrib.auth import get_user_model
        
        # Thread-local storage would be implemented here
        # For now, return None as placeholder
        return None
    except ImportError:
        return None


def set_audit_context(user=None, ip_address=None):
    """
    Set audit context for the current operation.
    
    Usage in views:
        def my_view(request):
            set_audit_context(
                user=request.user,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            ...
    
    Args:
        user: User instance performing the action
        ip_address: Client IP address as string
    """
    # This would be implemented with thread-local storage
    pass
