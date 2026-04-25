from django.db import models


class RolePermission(models.Model):
    """Relación roles-permisos."""

    role = models.ForeignKey(
        'core_roles.Role', on_delete=models.CASCADE, db_column='role_id'
    )
    permission = models.ForeignKey(
        'core_permissions.Permission',
        on_delete=models.CASCADE,
        db_column='permission_id',
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['role', 'permission'],
                name='role_perm_unique',
            ),
        ]

    def __str__(self):
        return f'{self.role} -> {self.permission}'
