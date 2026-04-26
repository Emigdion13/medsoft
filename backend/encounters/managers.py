"""
Encounter app managers with domain-specific query methods.
"""

from django.db import models

from core.models import SoftDeleteQuerySet, SoftDeleteManager


class EncounterQuerySet(SoftDeleteQuerySet):
    """Custom queryset for Encounter model with clinical queries."""

    def by_patient(self, patient_id: int):
        """Find encounters for a specific patient."""
        return self.filter(patient_id=patient_id)

    def by_doctor(self, doctor_id: int):
        """Find encounters managed by a specific doctor."""
        return self.filter(doctor_id=doctor_id)

    def active_encounters(self):
        """Return open encounters (most recent)."""
        return self.filter(status='ABIERTO')

    def by_status(self, status: str):
        """Filter encounters by status."""
        return self.filter(status=status)

    def by_type(self, encounter_type: str):
        """Filter encounters by type."""
        return self.filter(encounter_type=encounter_type)

    def with_vitals(self):
        """Prefetch vital signs for encounters."""
        return self.prefetch_related('vitalsign_set')

    def with_notes(self):
        """Prefetch clinical notes for encounters."""
        return self.prefetch_related('clinicalnote_set')

    def date_range(self, start_date, end_date):
        """Filter encounters within a date range."""
        return self.filter(
            start_at__date__range=(start_date, end_date)
        )

    def without_billing(self):
        """Find encounters not yet billed."""
        from billing.models import EncounterBilling
        return self.exclude(billing_encounter__isnull=False)


class VitalSignQuerySet(SoftDeleteQuerySet):
    """Custom queryset for VitalSign model with measurement queries."""

    def latest_per_patient(self, patient_id: int):
        """Get the most recent vital signs for a patient."""
        from django.db.models import Subquery, Max

        latest_ids = (
            VitalSign.objects.filter(encounter__patient_id=patient_id)
            .values('encounter__patient')
            .annotate(max_id=Max('id'))
            .values('max_id')[:1]
        )

        return self.filter(id__in=Subquery(latest_ids))

    def by_encounter(self, encounter_id: int):
        """Get vital signs for a specific encounter."""
        return self.filter(encounter_id=encounter_id)

    def date_range(self, start_datetime, end_datetime):
        """Filter vital signs within a datetime range."""
        return self.filter(
            recorded_at__range=(start_datetime, end_datetime)
        )

    def with_recorded_by(self):
        """Prefetch user who recorded the vitals."""
        return self.prefetch_related('recorded_by')

    def abnormal_values(self):
        """Find vital signs with potentially abnormal values."""
        # Temperature: <35 or >42
        temp_abnormal = models.Q(temperature_c__lt=35) | models.Q(temperature_c__gt=42)
        # Heart rate: <30 or >220
        hr_abnormal = models.Q(heart_rate__lt=30) | models.Q(heart_rate__gt=220)
        # Respiratory rate: <8 or >60
        rr_abnormal = models.Q(respiratory_rate__lt=8) | models.Q(respiratory_rate__gt=60)
        # SpO2: <90
        spo2_abnormal = models.Q(oxygen_saturation__lt=90)

        return self.filter(
            temp_abnormal | hr_abnormal | rr_abnormal | spo2_abnormal
        )


class VitalSignManager(SoftDeleteManager.from_queryset(VitalSignQuerySet)):
    """Manager for VitalSign model."""
