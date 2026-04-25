import uuid

from django.db import models


class ClinicalNote(models.Model):
    """Notas médicas con firma e inmutabilidad."""

    NOTE_TYPE_CHOICES = (('EVOLUCION', 'Evolución'),)
    STATUS_CHOICES = (
        ('BORRADOR', 'Borrador'),
        ('FIRMADA', 'Firmada'),
        ('ANULADA', 'Anulada'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    encounter = models.ForeignKey(
        'encounters.Encounter',
        on_delete=models.CASCADE,
        db_column='encounter_id',
    )
    doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.PROTECT,
        db_column='doctor_id',
    )

    note_type = models.CharField(
        max_length=40, default='EVOLUCION'
    )
    content = models.TextField()
    status = models.CharField(
        max_length=20, default='BORRADOR', choices=STATUS_CHOICES
    )

    signed_by = models.ForeignKey(
        'core_users.User',
        on_delete=models.SET_NULL,
        db_column='signed_by',
        blank=True,
        null=True,
    )
    signed_at = models.DateTimeField(blank=True, null=True)

    content_hash = models.CharField(max_length=64, blank=True, null=True)
    signature_blob = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey(
        'core_users.User',
        on_delete=models.PROTECT,
        db_column='created_by',
    )
    updated_by = models.ForeignKey(
        'core_users.User',
        on_delete=models.PROTECT,
        db_column='updated_by',
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=models.Q(status__in=[c[0] for c in STATUS_CHOICES]),
                name='note_status_check',
            ),
            models.CheckConstraint(
                check=models.Q(
                    models.Q(status='FIRMADA', signed_by__isnull=False, signed_at__isnull=False)
                    | models.Q(status__ne='FIRMADA')
                ),
                name='note_signed_check',
            ),
        ]
        indexes = [
            models.Index(
                fields=['encounter', '-created_at'], name='note_encounter_idx'
            ),
            models.Index(
                fields=['doctor', '-created_at'], name='note_doctor_idx'
            ),
            models.Index(
                fields=['status'], name='note_status_idx'
            ),
        ]

    def __str__(self):
        return f'{self.doctor} — {self.encounter} [{self.status}]'


class Diagnosis(models.Model):
    """Diagnósticos por encuentro (ICD-10)."""

    DIAGNOSIS_TYPE_CHOICES = (
        ('PRINCIPAL', 'Principal'),
        ('SECUNDARIO', 'Secundario'),
        ('COMORBILIDAD', 'Comorbilidad'),
    )
    STATUS_CHOICES = (
        ('ACTIVO', 'Activo'),
        ('RESUELTO', 'Resuelto'),
        ('CANCELADO', 'Cancelado'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    encounter = models.ForeignKey(
        'encounters.Encounter',
        on_delete=models.CASCADE,
        db_column='encounter_id',
    )

    icd10_code = models.CharField(max_length=10)
    description = models.CharField(max_length=255)

    diagnosis_type = models.CharField(
        max_length=20, default='PRINCIPAL', choices=DIAGNOSIS_TYPE_CHOICES
    )
    is_primary = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20, default='ACTIVO', choices=STATUS_CHOICES
    )

    recorded_by = models.ForeignKey(
        'core_users.User',
        on_delete=models.PROTECT,
        db_column='recorded_by',
    )
    recorded_at = models.DateTimeField(
        db_column='recorded_at', auto_now_add=True
    )

    class Meta:
        ordering = ['-recorded_at']
        constraints = [
            models.CheckConstraint(
                check=models.Q(diagnosis_type__in=[c[0] for c in DIAGNOSIS_TYPE_CHOICES]),
                name='diag_type_check',
            ),
            models.CheckConstraint(
                check=models.Q(status__in=[c[0] for c in STATUS_CHOICES]),
                name='diag_status_check',
            ),
        ]
        indexes = [
            models.Index(
                fields=['encounter'], name='diag_encounter_idx'
            ),
            models.Index(
                fields=['icd10_code'], name='diag_icd10_idx'
            ),
            models.Index(
                fields=['status'], name='diag_status_idx'
            ),
        ]

    def __str__(self):
        return f'{self.icd10_code} — {self.description}'


class Prescription(models.Model):
    """Indicaciones farmacológicas por encuentro."""

    ROUTE_CHOICES = (
        ('ORAL', 'Oral'),
        ('IV', 'Intravenoso'),
        ('IM', 'Intramuscular'),
        ('TOPICA', 'Tópica'),
        ('INHALADA', 'Inhalada'),
    )
    STATUS_CHOICES = (
        ('ACTIVA', 'Activa'),
        ('SUSPENDIDA', 'Suspendida'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    encounter = models.ForeignKey(
        'encounters.Encounter',
        on_delete=models.CASCADE,
        db_column='encounter_id',
    )

    prescribed_by = models.ForeignKey(
        'core_users.User',
        on_delete=models.PROTECT,
        db_column='prescribed_by',
    )

    medication_name = models.CharField(max_length=255)
    medication_code = models.CharField(max_length=60, blank=True, null=True)

    dose = models.CharField(max_length=80)
    frequency = models.CharField(max_length=120)
    route = models.CharField(max_length=30, choices=ROUTE_CHOICES)

    duration_days = models.IntegerField(blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    instructions = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=20, default='ACTIVA', choices=STATUS_CHOICES
    )
    prescribed_at = models.DateTimeField(
        db_column='prescribed_at', auto_now_add=True
    )

    class Meta:
        ordering = ['-prescribed_at']
        constraints = [
            models.CheckConstraint(
                check=models.Q(status__in=[c[0] for c in STATUS_CHOICES]),
                name='rx_status_check',
            ),
            models.CheckConstraint(
                check=models.Q(
                    models.Q(duration_days__isnull=True)
                    | models.Q(duration_days__gt=0)
                ),
                name='rx_duration_check',
            ),
        ]
        indexes = [
            models.Index(
                fields=['encounter', '-prescribed_at'], name='rx_encounter_idx'
            ),
            models.Index(
                fields=['status'], name='rx_status_idx'
            ),
        ]

    def __str__(self):
        return f'{self.medication_name} — {self.encounter}'
