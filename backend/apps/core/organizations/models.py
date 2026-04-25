from django.db import models


class Organization(models.Model):
    """Datos de la clínica (1 registro en v1)."""

    name = models.CharField(max_length=160)
    trade_name = models.CharField(max_length=160, blank=True, null=True)
    rnc = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=25, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    province = models.CharField(max_length=120, blank=True, null=True)
    municipality = models.CharField(max_length=120, blank=True, null=True)
    timezone = models.CharField(
        max_length=64, default='America/Santo_Domingo'
    )
    language_code = models.CharField(max_length=10, default='es-DO')
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        indexes = [
            models.Index(
                fields=['is_active'],
                name='org_is_active_idx',
            ),
            models.UniqueConstraint(
                fields=['rnc'],
                condition=models.Q(rnc__isnull=False),
                name='org_rnc_unique',
            ),
        ]

    def __str__(self):
        return self.name
