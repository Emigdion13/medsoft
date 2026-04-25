import uuid

from django.db import models

from utils.constants import (
    ENCOUNTER_TYPES,
    ENCOUNTER_STATUS,
)


class Encounter(models.Model):
    """Episodio clínico (ambulatorio/internamiento/emergencia/teleconsulta)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    organization = models.ForeignKey(
        'core_organizations.Organization',
        on_delete=models.PROTECT,
        db_column='organization_id',
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
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        db_column='appointment_id',
        blank=True,
        null=True,
    )

    encounter_type = models.CharField(
        max_length=20, choices=ENCOUNTER_TYPES
    )
    status = models.CharField(
        max_length=20, default='ABIERTO', choices=ENCOUNTER_STATUS
    )
    start_at = models.DateTimeField(db_column='start_at')
    end_at = models.DateTimeField(blank=True, null=True)

    chief_complaint = models.TextField(blank=True, null=True)
    room_number = models.CharField(max_length=40, blank=True, null=True)
    bed_number = models.CharField(max_length=40, blank=True, null=True)
    admission_source = models.CharField(
        max_length=80, blank=True, null=True
    )
    discharge_reason = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey(
        'core_users.User',
        on_delete=models.PROTECT,
        db_column='created_by',
        related_name='encounters_created',
        blank=True,
        null=True,
    )
    updated_by = models.ForeignKey(
        'core_users.User',
        on_delete=models.PROTECT,
        db_column='updated_by',
        related_name='encounters_updated',
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['start_at']
        constraints = [
            models.CheckConstraint(
                check=models.Q(encounter_type__in=[c[0] for c in ENCOUNTER_TYPES]),
                name='enc_type_check',
            ),
            models.CheckConstraint(
                check=models.Q(status__in=[c[0] for c in ENCOUNTER_STATUS]),
                name='enc_status_check',
            ),
            models.CheckConstraint(
                check=models.Q(
                    models.Q(end_at__isnull=True)
                    | models.Q(end_at__gt=models.F('start_at'))
                ),
                name='enc_end_after_start_check',
            ),
        ]
        indexes = [
            models.Index(
                fields=['patient', 'start_at'], name='enc_patient_start_idx'
            ),
            models.Index(
                fields=['doctor', 'start_at'], name='enc_doctor_start_idx'
            ),
            models.Index(
                fields=['status'], name='enc_status_idx'
            ),
            models.Index(
                fields=['encounter_type'], name='enc_type_idx'
            ),
        ]

    def __str__(self):
        return f'{self.patient} — {self.encounter_type}'


class VitalSign(models.Model):
    """Mediciones de enfermería por encuentro."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    encounter = models.ForeignKey(
        'encounters.Encounter',
        on_delete=models.CASCADE,
        db_column='encounter_id',
    )
    recorded_by = models.ForeignKey(
        'core_users.User',
        on_delete=models.PROTECT,
        db_column='recorded_by',
    )
    recorded_at = models.DateTimeField(
        db_column='recorded_at', auto_now_add=True
    )

    temperature_c = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    bp_systolic = models.IntegerField(blank=True, null=True)
    bp_diastolic = models.IntegerField(blank=True, null=True)
    heart_rate = models.IntegerField(blank=True, null=True)
    respiratory_rate = models.IntegerField(blank=True, null=True)
    oxygen_saturation = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    weight_kg = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True
    )
    height_cm = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True
    )
    bmi = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True
    )
    glucose_mg_dl = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True
    )
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-recorded_at']
        indexes = [
            models.Index(
                fields=['encounter', 'recorded_at'],
                name='vitals_encounter_idx',
            ),
            models.Index(
                fields=['recorded_by'], name='vitals_recorded_by_idx'
            ),
        ]

    def __str__(self):
        return f'{self.encounter} — {self.recorded_at}'
