from django.db import models


class Permission(models.Model):
    """Permisos granulares por módulo/recurso/acción."""

    code = models.CharField(max_length=120, unique=True)
    module = models.CharField(max_length=60)
    resource = models.CharField(max_length=80)
    action = models.CharField(max_length=40)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['id']
        indexes = [
            models.Index(
                fields=['module'], name='perm_module_idx'
            ),
            models.Index(
                fields=['resource', 'action'],
                name='perm_res_action_idx',
            ),
        ]

    def __str__(self):
        return self.code
