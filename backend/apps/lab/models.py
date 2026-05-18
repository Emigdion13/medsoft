import uuid

from django.db import models


class LabTestCatalog(models.Model):
    """Catálogo de pruebas de laboratorio."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    sample_type = models.CharField(max_length=40)
    unit = models.CharField(max_length=30, blank=True, null=True)
    reference_min = models.DecimalField(
        max_digits=12, decimal_places=4, blank=True, null=True
    )
    reference_max = models.DecimalField(
        max_digits=12, decimal_places=4, blank=True, null=True
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.code}: {self.name}'


# Module-level constants for LabOrder
LAB_ORDER_PRIORITY_CHOICES = (('NORMAL', 'Normal'), ('URGENTE', 'Urgente'))
LAB_ORDER_STATUS_CHOICES = (
    ('PENDIENTE', 'Pendiente'),
    ('RECOLECTADA', 'Recolectada'),
    ('EN_PROCESO', 'En proceso'),
    ('COMPLETADA', 'Completada'),
    ('CANCELADA', 'Cancelada'),
)


class LabOrder(models.Model):
    """Orden de laboratorio emitida por médico."""

    PRIORITY_CHOICES = LAB_ORDER_PRIORITY_CHOICES
    STATUS_CHOICES = LAB_ORDER_STATUS_CHOICES

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    organization = models.ForeignKey(
        'core_organizations.Organization',
        on_delete=models.PROTECT,
        db_column='organization_id',
    )
    encounter = models.ForeignKey(
        'encounters.Encounter',
        on_delete=models.PROTECT,
        db_column='encounter_id',
    )
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.PROTECT,
        db_column='patient_id',
    )
    doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.PROTECT,
        db_column='doctor_id',
    )

    order_number = models.CharField(max_length=50)
    priority = models.CharField(
        max_length=20, default='NORMAL', choices=PRIORITY_CHOICES
    )
    status = models.CharField(
        max_length=20, default='PENDIENTE', choices=STATUS_CHOICES
    )
    ordered_at = models.DateTimeField(
        db_column='ordered_at', auto_now_add=True
    )
    expected_collection_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey(
        'core_users.User',
        on_delete=models.PROTECT,
        db_column='created_by',
        related_name='lab_orders_created',
    )
    updated_by = models.ForeignKey(
        'core_users.User',
        on_delete=models.PROTECT,
        db_column='updated_by',
        blank=True,
        null=True,
        related_name='lab_orders_updated',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-ordered_at']
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'order_number'],
                condition=models.Q(deleted_at__isnull=True),
                name='lab_order_org_number_unique',
            ),
            models.CheckConstraint(
                check=models.Q(priority__in=[c[0] for c in LAB_ORDER_PRIORITY_CHOICES]),
                name='lab_order_priority_check',
            ),
            models.CheckConstraint(
                check=models.Q(status__in=[c[0] for c in LAB_ORDER_STATUS_CHOICES]),
                name='lab_order_status_check',
            ),
        ]
        indexes = [
            models.Index(
                fields=['encounter'], name='lab_order_encounter_idx'
            ),
            models.Index(
                fields=['patient'], name='lab_order_patient_idx'
            ),
            models.Index(
                fields=['status'], name='lab_order_status_idx'
            ),
            models.Index(
                fields=['ordered_at'], name='lab_order_ordered_at_idx'
            ),
        ]

    def __str__(self):
        return f'{self.order_number} — {self.patient}'


class LabOrderItem(models.Model):
    """Pruebas incluidas en una orden de laboratorio."""

    STATUS_CHOICES = (('PENDIENTE', 'Pendiente'),)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    lab_order = models.ForeignKey(
        'lab.LabOrder',
        on_delete=models.CASCADE,
        db_column='lab_order_id',
    )
    lab_test = models.ForeignKey(
        'lab.LabTestCatalog',
        on_delete=models.PROTECT,
        db_column='lab_test_id',
    )
    status = models.CharField(
        max_length=20, default='PENDIENTE', choices=STATUS_CHOICES
    )

    class Meta:
        unique_together = ['lab_order', 'lab_test']

    def __str__(self):
        return f'{self.lab_order} — {self.lab_test}'


class LabResult(models.Model):
    """Resultados de laboratorio por item."""

    RESULT_FLAG_CHOICES = (
        ('NORMAL', 'Normal'),
        ('ANORMAL', 'Anormal'),
        ('CRITICO', 'Crítico'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    lab_order_item = models.ForeignKey(
        'lab.LabOrderItem',
        on_delete=models.CASCADE,
        db_column='lab_order_item_id',
    )

    result_text = models.CharField(max_length=255, blank=True, null=True)
    result_numeric = models.DecimalField(
        max_digits=14, decimal_places=4, blank=True, null=True
    )
    unit = models.CharField(max_length=30, blank=True, null=True)
    ref_min = models.DecimalField(
        max_digits=14, decimal_places=4, blank=True, null=True
    )
    ref_max = models.DecimalField(
        max_digits=14, decimal_places=4, blank=True, null=True
    )

    result_flag = models.CharField(
        max_length=20, default='NORMAL', choices=RESULT_FLAG_CHOICES
    )

    processed_by = models.ForeignKey(
        'core_users.User',
        on_delete=models.PROTECT,
        db_column='processed_by',
        related_name='lab_results_processed',
    )
    reviewed_by = models.ForeignKey(
        'core_users.User',
        on_delete=models.SET_NULL,
        db_column='reviewed_by',
        blank=True,
        null=True,
        related_name='lab_results_reviewed',
    )

    processed_at = models.DateTimeField(
        db_column='processed_at', auto_now_add=True
    )
    reviewed_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-processed_at']
        indexes = [
            models.Index(
                fields=['lab_order_item'], name='lab_result_item_idx'
            ),
            models.Index(
                fields=['processed_at'], name='lab_result_processed_idx'
            ),
            models.Index(
                fields=['result_flag'], name='lab_result_flag_idx'
            ),
        ]

    def __str__(self):
        return f'{self.lab_order_item} — {self.result_flag}'
