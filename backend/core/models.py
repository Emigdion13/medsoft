"""
Core utilities for MediSoft Django application.

Provides:
- Soft delete manager and queryset classes
- Base model with common fields
- Audit log model for tracking changes
"""

from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    """
    Custom QuerySet that excludes soft-deleted records by default.
    
    Models using this queryset will filter out records where `deleted_at`
    is not null, unless explicitly requested via `.with_deleted()` or `.only_deleted()`.
    """

    def active(self):
        """Return only non-soft-deleted records."""
        return self.filter(deleted_at__isnull=True)

    def with_deleted(self):
        """Include soft-deleted records in the queryset."""
        return self

    def only_deleted(self):
        """Return only soft-deleted records."""
        return self.exclude(deleted_at__isnull=True)


class SoftDeleteManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    """
    Manager that uses SoftDeleteQuerySet.
    
    Usage:
        class MyModel(models.Model):
            deleted_at = models.DateTimeField(null=True, blank=True)
            
            objects = SoftDeleteManager()  # Excludes deleted by default
            all_objects = models.Manager()  # Includes all records
    """

    def get_queryset(self):
        return super().get_queryset().active()

    def with_deleted(self):
        """Return queryset including soft-deleted records."""
        return self.get_queryset().with_deleted()


class SoftDeleteModel(models.Model):
    """
    Abstract base model implementing soft delete pattern.
    
    Adds:
        - `deleted_at` field for marking records as deleted
        - SoftDeleteManager to exclude deleted records by default
        - `restore()` method to undelete a record
    
    Usage:
        class MyModel(SoftDeleteModel):
            # Your fields here
            
            objects = SoftDeleteManager()  # Excludes deleted
            all_objects = models.Manager()  # All records including deleted
    
    Note: This model should NOT be inherited from directly if you have
    multiple inheritance. Instead, use the manager pattern.
    """

    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """
        Soft delete: sets deleted_at to current timestamp instead of deleting.
        """
        self.deleted_at = timezone.now()
        self.save(using=using)

    def restore(self):
        """Restore a soft-deleted record."""
        self.deleted_at = None
        self.save()


class AuditLog(models.Model):
    """
    Audit log model for tracking all model changes.
    
    This model records:
    - User who performed the action
    - Action type (CREATE, UPDATE, DELETE, SOFT_DELETE, M2M_CHANGE)
    - Model affected and object ID
    - Description of the change
    - Old/new values for updates
    - Client IP address
    """
    
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete (hard)'),
        ('SOFT_DELETE', 'Soft Delete'),
        ('M2M_CHANGE', 'Many-to-Many Change'),
        ('VIEW', 'View (access log)'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('FAILED_LOGIN', 'Failed Login'),
    ]
    
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='audit_logs',
        help_text="User who performed the action"
    )
    
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        db_index=True,
        verbose_name="Action Type"
    )
    
    model = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name="Model Name",
        help_text="Name of the affected model"
    )
    
    object_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="Primary key of the affected record"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Description of the action performed"
    )
    
    changes = models.JSONField(
        default=dict,
        blank=True,
        help_text="Dictionary of field changes (old -> new)"
    )
    
    snapshot = models.JSONField(
        default=dict,
        blank=True,
        help_text="Snapshot of record at time of deletion"
    )
    
    related_object_ids = models.JSONField(
        default=list,
        blank=True,
        help_text="List of related object IDs for M2M changes"
    )
    
    ip_address = models.GenericIPAddressField(
        null=True, blank=True,
        verbose_name="IP Address",
        help_text="Client IP address where the action originated"
    )
    
    user_agent = models.TextField(
        blank=True,
        help_text="Browser/user agent string"
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When the action occurred"
    )
    
    class Meta:
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['action', 'model']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.action} {self.model} ({self.object_id})"
    
    @classmethod
    def create_log(
        cls,
        user,
        action: str,
        model: str,
        object_id: str = None,
        description: str = None,
        changes: dict = None,
        snapshot: dict = None,
        ip_address: str = None,
        user_agent: str = None
    ):
        """
        Create an audit log entry.
        
        Args:
            user: User instance or None
            action: Action type string (from ACTION_CHOICES)
            model: Model name that was affected
            object_id: Primary key of affected record (optional)
            description: Description of the change (optional)
            changes: Dictionary of field changes {field: {'old': val, 'new': val}} (optional)
            snapshot: Snapshot of record at time of deletion (optional)
            ip_address: Client IP address (optional)
            user_agent: Browser/user agent string (optional)
        
        Returns:
            The created AuditLog instance
        """
        return cls.objects.create(
            user=user,
            action=action,
            model=model,
            object_id=str(object_id) if object_id else None,
            description=description or f"{action} {model}",
            changes=changes or {},
            snapshot=snapshot or {},
            ip_address=ip_address,
            user_agent=user_agent or '',
        )


class AccessLog(models.Model):
    """
    Log model for tracking access to sensitive resources.
    
    Records access to:
    - Patient records (viewed/edited)
    - Financial information
    - Prescription data
    - Lab results
    - Imaging reports
    
    Used for:
    - HIPAA compliance tracking
    - Access pattern analysis
    - Security auditing
    """
    
    ACCESS_TYPE_CHOICES = [
        ('VIEW', 'View'),
        ('EDIT', 'Edit'),
        ('EXPORT', 'Export'),
        ('PRINT', 'Print'),
        ('DOWNLOAD', 'Download'),
    ]
    
    SENSITIVE_RESOURCE_CHOICES = [
        ('PATIENT_RECORD', 'Patient Record'),
        ('FINANCIAL_DATA', 'Financial Data'),
        ('PRESCRIPTION', 'Prescription'),
        ('LAB_RESULT', 'Lab Result'),
        ('IMAGING_REPORT', 'Imaging Report'),
        ('ADMIN_SETTINGS', 'Admin Settings'),
    ]
    
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='access_logs',
        help_text="User who accessed the resource"
    )
    
    access_type = models.CharField(
        max_length=20,
        choices=ACCESS_TYPE_CHOICES,
        db_index=True,
        verbose_name="Access Type"
    )
    
    resource_type = models.CharField(
        max_length=30,
        choices=SENSITIVE_RESOURCE_CHOICES,
        db_index=True,
        verbose_name="Resource Type"
    )
    
    resource_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="ID of the accessed resource"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Description of access (optional)"
    )
    
    ip_address = models.GenericIPAddressField(
        null=True, blank=True,
        verbose_name="IP Address",
        help_text="Client IP address where access originated"
    )
    
    user_agent = models.TextField(
        blank=True,
        help_text="Browser/user agent string"
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When the access occurred"
    )
    
    successful = models.BooleanField(
        default=True,
        verbose_name="Access Granted",
        help_text="Whether the access request was granted or denied"
    )
    
    class Meta:
        verbose_name = "Access Log"
        verbose_name_plural = "Access Logs"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['resource_type', 'access_type']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]
    
    def __str__(self):
        status = "GRANTED" if self.successful else "DENIED"
        return f"{status}: {self.access_type} {self.resource_type} ({self.resource_id})"
    
    @classmethod
    def create_access_log(
        cls,
        user,
        access_type: str,
        resource_type: str,
        resource_id: str = None,
        description: str = None,
        ip_address: str = None,
        user_agent: str = None,
        successful: bool = True,
    ):
        """
        Create an access log entry.
        
        Args:
            user: User instance or None
            access_type: Type of access (VIEW, EDIT, etc.)
            resource_type: Type of sensitive resource accessed
            resource_id: ID of the specific resource (optional)
            description: Description of the access (optional)
            ip_address: Client IP address (optional)
            user_agent: Browser/user agent string (optional)
            successful: Whether access was granted (default: True)
        
        Returns:
            The created AccessLog instance
        """
        return cls.objects.create(
            user=user,
            access_type=access_type,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            description=description or f"{access_type} {resource_type}",
            ip_address=ip_address,
            user_agent=user_agent or '',
            successful=successful,
        )


class SystemConfig(models.Model):
    """
    System-wide configuration settings stored in database.
    
    Allows runtime configuration changes without code deployment.
    Uses JSONField for flexible key-value storage with validation.
    """
    
    key = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Configuration Key",
        help_text="Unique identifier for the config setting"
    )
    
    value = models.JSONField(
        blank=True,
        default=dict,
        verbose_name="Configuration Value",
        help_text="JSON value for the configuration (can be string, number, bool, or object)"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Description of what this config does"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Enabled",
        help_text="Whether this configuration is active"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Updated"
    )
    
    class Meta:
        verbose_name = "System Configuration"
        verbose_name_plural = "System Configurations"
        ordering = ['key']
    
    def __str__(self):
        return f"{self.key}: {self.value}"
