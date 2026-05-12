import uuid

from django.db import models


class ServiceCode(models.Model):
    """Catálogo de servicios para v2 (facturación futura)."""

    CATEGORY_CHOICES = (
        ('CONSULTA', 'Consulta'),
        ('PROCEDIMIENTO', 'Procedimiento'),
        ('LAB', 'Laboratorio'),
        ('IMAGEN', 'Imagen'),
        ('INTERNAMIENTO', 'Internamiento'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    category = models.CharField(
        max_length=40, choices=CATEGORY_CHOICES
    )
    base_price = models.DecimalField(max_digits=12, decimal_places=2)
    ars_code = models.CharField(
        max_length=60, blank=True, null=True
    )
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['id']
        indexes = [
            models.Index(
                fields=['deleted_at'], name='service_deleted_at_idx'
            ),
        ]

    def __str__(self):
        return f'{self.code} — {self.name}'


class EncounterBilling(models.Model):
    """Preparación de facturación por encuentro (placeholder v1)."""

    BILLING_STATUS_CHOICES = (('PENDIENTE', 'Pendiente'),)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    encounter = models.ForeignKey(
        'encounters.Encounter',
        on_delete=models.PROTECT,
        db_column='encounter_id',
    )

    ncf_number = models.CharField(
        max_length=50, blank=True, null=True
    )
    ars_provider = models.CharField(
        max_length=120, blank=True, null=True
    )
    ars_affiliation_number = models.CharField(
        max_length=60, blank=True, null=True
    )

    billing_status = models.CharField(
        max_length=20, default='PENDIENTE', choices=BILLING_STATUS_CHOICES
    )
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )

    billed_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['ncf_number'],
                condition=models.Q(ncf_number__isnull=False),
                name='billing_ncf_unique',
            ),
        ]
        indexes = [
            models.Index(
                fields=['encounter'], name='billing_encounter_idx'
            ),
            models.Index(
                fields=['billing_status'], name='billing_status_idx'
            ),
            models.Index(
                fields=['deleted_at'], name='billing_deleted_at_idx'
            ),
        ]

    def __str__(self):
        return f'{self.encounter} — {self.billing_status}'
