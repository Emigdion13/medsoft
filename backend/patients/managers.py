"""
Patient app managers with domain-specific query methods.
"""

from django.db import models

from core.models import SoftDeleteQuerySet, SoftDeleteManager


class PatientQuerySet(SoftDeleteQuerySet):
    """Custom queryset for Patient model with clinical queries."""

    def by_name(self, name: str):
        """Filter patients by partial name match (case-insensitive)."""
        return self.filter(
            models.Q(first_name__icontains=name)
            | models.Q(last_name__icontains=name)
        )

    def by_cedula(self, cedula: str):
        """Find patient by Cédula number."""
        return self.filter(cedula=cedula)

    def active_patients(self):
        """Return patients with active status."""
        return self.filter(status='ACTIVO')

    def recently_added(self, days: int = 7):
        """Return patients added in the last N days."""
        from django.utils import timezone
        from datetime import timedelta

        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff)

    def with_encounters(self):
        """Prefetch encounters for patients."""
        return self.prefetch_related('encounter_set')

    def without_primary_care physician(self):
        """Find patients without assigned primary care physician."""
        return self.filter(primary_physician__isnull=True)


class PatientManager(SoftDeleteManager.from_queryset(PatientQuerySet)):
    """Manager for Patient model."""
