import uuid

from django.db import models


class ImagingTypeCatalog(models.Model):
    """Catálogo de estudios de imagen."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    code = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=180)
    modality = models.CharField(max_length=40)  # RX, US, CT, MRI, etc.
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.code} — {self.name}'


class ImagingOrder(models.Model):
    """Órdenes de imágenes."""

    PRIORITY_CHOICES = (('NORMAL', 'Normal'), ('URGENTE', 'Urgente'))
    STATUS_CHOICES = (
        ('PENDIENTE', 'Pendiente'),
        ('REALIZADA', 'Realizada'),
        ('EN_PROCESO', 'En proceso'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    )

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
    imaging_type = models.ForeignKey(
        'imaging.ImagingTypeCatalog',
        on_delete=models.PROTECT,
        db_column='imaging_type_id',
    )

    order_number = models.CharField(max_length=50)
    priority = models.CharField(
        max_length=20, default='NORMAL', choices=PRIORITY_CHOICES
    )
    status = models.CharField(
        max_length=20, default='PENDIENTE', choices=STATUS_CHOICES
    )
    clinical_indication = models.TextField()
    ordered_at = models.DateTimeField(
        db_column='ordered_at', auto_now_add=True
    )
    expected_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

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
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-ordered_at']
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'order_number'],
                condition=models.Q(deleted_at__isnull=True),
                name='img_order_org_number_unique',
            ),
            models.CheckConstraint(
                check=models.Q(priority__in=[c[0] for c in PRIORITY_CHOICES]),
                name='img_order_priority_check',
            ),
            models.CheckConstraint(
                check=models.Q(status__in=[c[0] for c in STATUS_CHOICES]),
                name='img_order_status_check',
            ),
        ]
        indexes = [
            models.Index(
                fields=['encounter'], name='img_order_encounter_idx'
            ),
            models.Index(
                fields=['patient'], name='img_order_patient_idx'
            ),
            models.Index(
                fields=['status'], name='img_order_status_idx'
            ),
            models.Index(
                fields=['-ordered_at'], name='img_order_ordered_at_idx'
            ),
        ]

    def __str__(self):
        return f'{self.order_number} — {self.patient}'


class ImagingReport(models.Model):
    """Informe de estudio de imagen (firmable)."""

    STATUS_CHOICES = (
        ('BORRADOR', 'Borrador'),
        ('FIRMADA', 'Firmada'),
        ('ANULADA', 'Anulada'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    imaging_order = models.ForeignKey(
        'imaging.ImagingOrder',
        on_delete=models.CASCADE,
        db_column='imaging_order_id',
    )

    technician_user = models.ForeignKey(
        'core_users.User',
        on_delete=models.PROTECT,
        db_column='technician_user_id',
    )
    radiologist_user = models.ForeignKey(
        'core_users.User',
        on_delete=models.SET_NULL,
        db_column='radiologist_user_id',
        blank=True,
        null=True,
    )

    performed_at = models.DateTimeField(
        db_column='performed_at', auto_now_add=True
    )

    findings = models.TextField()
    impression = models.TextField()
    recommendations = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=20, default='BORRADOR', choices=STATUS_CHOICES
    )
    signed_at = models.DateTimeField(blank=True, null=True)

    content_hash = models.CharField(max_length=64, blank=True, null=True)
    signature_blob = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-performed_at']
        constraints = [
            models.CheckConstraint(
                check=models.Q(status__in=[c[0] for c in STATUS_CHOICES]),
                name='img_report_status_check',
            ),
            models.CheckConstraint(
                check=models.Q(
                    models.Q(status='FIRMADA', signed_at__isnull=False)
                    & models.Q(radiologist_user__isnull=False)
                    | models.Q(status__ne='FIRMADA')
                ),
                name='img_report_signed_check',
            ),
        ]
        indexes = [
            models.Index(
                fields=['imaging_order'], name='img_report_order_idx'
            ),
            models.Index(
                fields=['status'], name='img_report_status_idx'
            ),
            models.Index(
                fields=['-performed_at'], name='img_report_performed_idx'
            ),
        ]

    def __str__(self):
        return f'{self.imaging_order} — {self.status}'


class ImagingFile(models.Model):
    """Metadatos de archivos (DICOM/PDF/JPG)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    imaging_order = models.ForeignKey(
        'imaging.ImagingOrder',
        on_delete=models.CASCADE,
        db_column='imaging_order_id',
    )

    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=30)
    storage_uri = models.TextField()
    size_bytes = models.BigIntegerField()
    sha256 = models.CharField(max_length=64)

    uploaded_by = models.ForeignKey(
        'core_users.User',
        on_delete=models.PROTECT,
        db_column='uploaded_by',
    )

    uploaded_at = models.DateTimeField(
        db_column='uploaded_at', auto_now_add=True
    )

    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(
                fields=['imaging_order'], name='img_file_order_idx'
            ),
            models.Index(
                fields=['-uploaded_at'], name='img_file_uploaded_idx'
            ),
        ]

    def __str__(self):
        return self.file_name
