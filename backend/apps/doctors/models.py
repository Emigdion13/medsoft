import uuid

from django.db import models


class Specialty(models.Model):
    """Catálogo de especialidades médicas."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    code = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['id']
        indexes = [
            models.Index(
                fields=['is_active'], name='specialty_is_active_idx'
            ),
        ]

    def __str__(self):
        return self.name


class Doctor(models.Model):
    """Profesionales médicos."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    organization = models.ForeignKey(
        'core_organizations.Organization',
        on_delete=models.PROTECT,
        db_column='organization_id',
    )
    user = models.ForeignKey(
        'core_users.User',
        on_delete=models.SET_NULL,
        db_column='user_id',
        blank=True,
        null=True,
    )
    cedula = models.CharField(max_length=20)
    license_number = models.CharField(max_length=60)
    medical_college_number = models.CharField(
        max_length=60, blank=True, null=True
    )
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    specialty_main = models.ForeignKey(
        'doctors.Specialty',
        on_delete=models.PROTECT,
        db_column='specialty_main_id',
    )
    phone = models.CharField(max_length=25, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    office_room = models.CharField(max_length=40, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'cedula'],
                condition=models.Q(deleted_at__isnull=True),
                name='doctor_org_cedula_unique',
            ),
            models.UniqueConstraint(
                fields=['organization', 'license_number'],
                condition=models.Q(deleted_at__isnull=True),
                name='doctor_org_license_unique',
            ),
        ]
        indexes = [
            models.Index(
                fields=['organization'], name='doctor_org_idx'
            ),
            models.Index(
                fields=['specialty_main'], name='doctor_specialty_idx'
            ),
            models.Index(
                fields=['is_active'], name='doctor_is_active_idx'
            ),
            models.Index(
                fields=['deleted_at'], name='doctor_deleted_at_idx'
            ),
        ]

    def __str__(self):
        return f'{self.last_name} {self.first_name}'


class DoctorSpecialty(models.Model):
    """Relación N:M doctor-especialidad."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.CASCADE,
        db_column='doctor_id',
    )
    specialty = models.ForeignKey(
        'doctors.Specialty',
        on_delete=models.CASCADE,
        db_column='specialty_id',
    )
    is_primary = models.BooleanField(default=False)

    class Meta:
        unique_together = ['doctor', 'specialty']

    def __str__(self):
        return f'{self.doctor} — {self.specialty}'


class SecretaryDoctor(models.Model):
    """Relación N:M secretaria/o → doctores asignados.
    Una secretaria puede estar asignada a uno o varios doctores.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    secretary = models.ForeignKey(
        'core_users.User',
        on_delete=models.CASCADE,
        db_column='secretary_id',
        related_name='assigned_doctors',
    )
    doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.CASCADE,
        db_column='doctor_id',
        related_name='assigned_secretaries',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['secretary', 'doctor'],
                name='secretary_doctor_unique',
            ),
        ]
        indexes = [
            models.Index(fields=['secretary'], name='sd_secretary_idx'),
            models.Index(fields=['doctor'], name='sd_doctor_idx'),
        ]

    def __str__(self):
        return f'{self.secretary.username} → Dr. {self.doctor.last_name}'
