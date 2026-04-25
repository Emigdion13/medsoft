from django.db import models


class Role(models.Model):
    """Roles RBAC."""

    organization = models.ForeignKey(
        'core_organizations.Organization',
        on_delete=models.PROTECT,
        db_column='organization_id',
    )
    code = models.CharField(max_length=50)  # DOCTOR, NURSE, etc.
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'code'],
                name='role_org_code_unique',
            ),
        ]
        indexes = [
            models.Index(fields=['organization'], name='role_org_idx'),
            models.Index(
                fields=['is_active'], name='role_is_active_idx'
            ),
        ]

    def __str__(self):
        return self.name
