from django.db import models


class AccessLog(models.Model):
    """Trazabilidad de acceso a recursos sensibles."""

    organization = models.ForeignKey(
        'core_organizations.Organization',
        on_delete=models.PROTECT,
        db_column='organization_id',
    )
    user = models.ForeignKey(
        'core_users.User', on_delete=models.PROTECT, db_column='user_id'
    )
    resource_type = models.CharField(max_length=80)
    resource_id = models.UUIDField()
    access_type = models.CharField(max_length=40)  # VIEW, EXPORT, PRINT, DOWNLOAD
    granted = models.BooleanField(default=True)
    denied_reason = models.TextField(blank=True, null=True)
    ip = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(
                fields=['organization', '-created_at'],
                name='access_org_created_idx',
            ),
            models.Index(
                fields=['resource_type', 'resource_id', '-created_at'],
                name='access_resource_idx',
            ),
            models.Index(
                fields=['user', '-created_at'],
                name='access_user_created_idx',
            ),
        ]

    def __str__(self):
        return f'{self.user} -> {self.resource_type}:{self.resource_id}'
