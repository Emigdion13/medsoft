from django.db import models


class UserRole(models.Model):
    """Relación usuarios-roles."""

    user = models.ForeignKey(
        'core_users.User',
        on_delete=models.CASCADE,
        db_column='user_id',
        related_name='role_assignments',
    )
    role = models.ForeignKey(
        'core_roles.Role', 
        on_delete=models.CASCADE, 
        db_column='role_id'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        'core_users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='assigned_by_user_id',
        related_name='role_assignments_given',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'role'],
                name='user_role_unique',
            ),
        ]

    def __str__(self):
        return f'{self.user} -> {self.role}'
