import uuid

from django.db import models


class Appointment(models.Model):
    """Agenda médica."""

    APPOINTMENT_TYPE_CHOICES = (('CONSULTA', 'Consulta'),)
    STATUS_CHOICES = (
        ('PROGRAMADA', 'Programada'),
        ('CONFIRMADA', 'Confirmada'),
        ('EN_CURSO', 'En curso'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
        ('NO_ASISTIO', 'No asistió'),
    )

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

    start_at = models.DateTimeField(db_column='start_at')
    end_at = models.DateTimeField(db_column='end_at')
    appointment_type = models.CharField(
        max_length=40, default='CONSULTA'
    )
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20, default='PROGRAMADA', choices=STATUS_CHOICES
    )
    notes = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey(
        'core_users.User',
        on_delete=models.PROTECT,
        db_column='created_by',
        blank=True,
        null=True,
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
        ordering = ['start_at']
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_at__gt=models.F('start_at')),
                name='appt_end_after_start_check',
            ),
            models.CheckConstraint(
                check=models.Q(status__in=[c[0] for c in STATUS_CHOICES]),
                name='appt_status_check',
            ),
        ]
        indexes = [
            models.Index(
                fields=['doctor', 'start_at'], name='appt_doctor_start_idx'
            ),
            models.Index(
                fields=['patient', 'start_at'], name='appt_patient_start_idx'
            ),
            models.Index(
                fields=['status'], name='appt_status_idx'
            ),
            models.Index(
                fields=['deleted_at'], name='appt_deleted_at_idx'
            ),
        ]

    def __str__(self):
        return f'{self.doctor} — {self.start_at}'
