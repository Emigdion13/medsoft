from django.db import models


class User(models.Model):
    """Identidad de usuarios del sistema (auth)."""

    organization = models.ForeignKey(
        'core_organizations.Organization',
        on_delete=models.PROTECT,
        db_column='organization_id',
    )
    username = models.CharField(max_length=150)
    email = models.EmailField(max_length=255)
    full_name = models.CharField(max_length=200)
    password_hash = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    last_login_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'username'],
                condition=models.Q(deleted_at__isnull=True),
                name='user_org_username_unique',
            ),
            models.UniqueConstraint(
                fields=['organization', 'email'],
                condition=models.Q(deleted_at__isnull=True),
                name='user_org_email_unique',
            ),
        ]
        indexes = [
            models.Index(fields=['organization'], name='user_org_idx'),
            models.Index(fields=['is_active'], name='user_is_active_idx'),
            models.Index(
                fields=['deleted_at'], name='user_deleted_at_idx'
            ),
        ]

    def __str__(self):
        return self.full_name
