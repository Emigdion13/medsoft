"""
Appointment app managers with domain-specific query methods.
"""

from django.db import models

from core.models import SoftDeleteQuerySet, SoftDeleteManager


class AppointmentQuerySet(SoftDeleteQuerySet):
    """Custom queryset for Appointment model with scheduling queries."""

    def by_date(self, date: models.Date):
        """Filter appointments for a specific date."""
        from datetime import datetime
        start = datetime.combine(date, datetime.min.time())
        end = datetime.combine(date, datetime.max.time())
        return self.filter(appointment_datetime__range=(start, end))

    def upcoming(self):
        """Return future appointments sorted by datetime."""
        from django.utils import timezone
        return (
            self.filter(appointment_datetime__gte=timezone.now())
            .order_by('appointment_datetime')
        )

    def today(self):
        """Return appointments scheduled for today."""
        from django.utils import timezone
        today = timezone.now().date()
        return self.by_date(today)

    def by_status(self, status: str):
        """Filter appointments by status."""
        return self.filter(status=status)

    def by_patient(self, patient_id: int):
        """Find appointments for a specific patient."""
        return self.filter(patient_id=patient_id)

    def by_doctor(self, doctor_id: int):
        """Find appointments for a specific doctor."""
        return self.filter(doctor_id=doctor_id)

    def confirmed(self):
        """Return confirmed appointments."""
        return self.by_status('CONFIRMADA')

    def pending(self):
        """Return pending appointments."""
        return self.by_status('PROGRAMADA')

    def with_patient_doctor(self):
        """Prefetch related patient and doctor data."""
        return self.prefetch_related('patient', 'doctor')


class AppointmentManager(SoftDeleteManager.from_queryset(AppointmentQuerySet)):
    """Manager for Appointment model."""
