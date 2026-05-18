from django.db import models


class AuditLog(models.Model):
    """Auditoría de cambios y eventos críticos (append-only)."""

    organization = models.ForeignKey(
        'core_organizations.Organization',
        on_delete=models.PROTECT,
        db_column='organization_id',
    )
    user = models.ForeignKey(
        'core_users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='user_id',
    )
    entity_type = models.CharField(max_length=80)
    entity_id = models.UUIDField()
    action = models.CharField(max_length=40)  # CREATE, UPDATE, DELETE, SIGN
    before_data = models.JSONField(null=True, blank=True)
    after_data = models.JSONField(null=True, blank=True)
    reason = models.TextField(blank=True, null=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'core_audit_auditlog'
        ordering = ['-created_at']
        indexes = [
            models.Index(
                fields=['organization', 'created_at'],
                name='audit_org_created_idx',
            ),
            models.Index(
                fields=['entity_type', 'entity_id', 'created_at'],
                name='audit_entity_idx',
            ),
            models.Index(
                fields=['user', 'created_at'],
                name='audit_user_created_idx',
            ),
        ]

    def __str__(self):
        return f'{self.entity_type}:{self.entity_id} ({self.action})'
