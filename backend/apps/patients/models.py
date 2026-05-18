import uuid

from django.db import models
from django.db.models.functions import TruncDate


class Patient(models.Model):
    """Registro maestro de pacientes."""

    SEX_CHOICES = (('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro'))
    IDENTITY_CHOICES = (('CEDULA', 'Cédula'), ('PASAPORTE', 'Pasaporte'), ('OTRO', 'Otro'))
    STATUS_CHOICES = (('ACTIVO', 'Activo'), ('INACTIVO', 'Inactivo'), ('FALLECIDO', 'Fallecido'))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    organization = models.ForeignKey(
        'core_organizations.Organization',
        on_delete=models.PROTECT,
        db_column='organization_id',
    )

    # Identity
    identity_type = models.CharField(max_length=20, default='CEDULA', choices=IDENTITY_CHOICES)
    cedula = models.CharField(max_length=20, blank=True, null=True)
    passport_number = models.CharField(max_length=40, blank=True, null=True)

    # Personal
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    birth_date = models.DateField()
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    nationality = models.CharField(max_length=80, default='DOMINICANA')

    # Contact
    phone_primary = models.CharField(max_length=25, blank=True, null=True)
    phone_secondary = models.CharField(max_length=25, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    province = models.CharField(max_length=120, blank=True, null=True)
    municipality = models.CharField(max_length=120, blank=True, null=True)

    # Medical
    blood_type = models.CharField(max_length=5, blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    chronic_conditions = models.TextField(blank=True, null=True)

    # Emergency contact
    emergency_contact_name = models.CharField(max_length=150, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=25, blank=True, null=True)
    emergency_contact_relation = models.CharField(max_length=60, blank=True, null=True)

    # ARS placeholders (v2)
    ars_provider = models.CharField(max_length=120, blank=True, null=True)
    ars_affiliation_number = models.CharField(max_length=60, blank=True, null=True)

    # Status
    status = models.CharField(max_length=20, default='ACTIVO', choices=STATUS_CHOICES)

    # Audit
    created_by = models.ForeignKey(
        'core_users.User',
        on_delete=models.PROTECT,
        db_column='created_by',
        related_name='patients_created',
        blank=True,
        null=True,
    )
    updated_by = models.ForeignKey(
        'core_users.User',
        on_delete=models.PROTECT,
        db_column='updated_by',
        related_name='patients_updated',
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['id']
        constraints = [
            models.CheckConstraint(
                check=models.Q(sex__in=['M', 'F', 'O']),
                name='patient_sex_check',
            ),
            models.CheckConstraint(
                check=models.Q(identity_type__in=['CEDULA', 'PASAPORTE', 'OTRO']),
                name='patient_identity_type_check',
            ),
            models.CheckConstraint(
                check=models.Q(status__in=['ACTIVO', 'INACTIVO', 'FALLECIDO']),
                name='patient_status_check',
            ),
            # Temporarily disabled for SQLite compatibility
            # models.CheckConstraint(
            #     check=models.Q(birth_date__lte=TruncDate(models.functions.Now())),
            #     name='patient_birth_date_past_check',
            # ),
            models.UniqueConstraint(
                fields=['organization', 'cedula'],
                name='patient_org_cedula_unique',
            ),
            models.UniqueConstraint(
                fields=['organization', 'passport_number'],
                name='patient_org_passport_unique',
            ),
        ]
        indexes = [
            models.Index(fields=['organization'], name='patient_org_idx'),
            models.Index(
                fields=['last_name', 'first_name'], name='patient_name_idx'
            ),
            models.Index(
                fields=['phone_primary'], name='patient_phone_idx'
            ),
            models.Index(
                fields=['deleted_at'], name='patient_deleted_at_idx'
            ),
        ]

    def __str__(self):
        return f'{self.last_name} {self.first_name}'
