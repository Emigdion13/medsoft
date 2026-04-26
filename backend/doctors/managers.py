"""
Doctor app managers with domain-specific query methods.
"""

from django.db import models

from core.models import SoftDeleteQuerySet, SoftDeleteManager


class DoctorQuerySet(SoftDeleteQuerySet):
    """Custom queryset for Doctor model with clinical queries."""

    def by_specialty(self, specialty_id: int):
        """Find doctors specialized in a specific field."""
        return self.filter(specialty_main_id=specialty_id)

    def by_name(self, name: str):
        """Filter doctors by partial name match (case-insensitive)."""
        return self.filter(
            models.Q(first_name__icontains=name)
            | models.Q(last_name__icontains=name)
        )

    def available(self):
        """Return active and available doctors."""
        return self.filter(is_active=True)

    def with_specialties(self):
        """Prefetch doctor specialties."""
        return (
            self.prefetch_related('doctorspecialty_set')
            .prefetch_related('specialty_main')
        )

    def by_office_room(self, room: str):
        """Find doctors in a specific office room."""
        return self.filter(office_room=room)

    def with_patients_count(self):
        """Annotate doctors with their patient count."""
        return self.annotate(
            patients_count=models.Count('encounter__patient', distinct=True)
        )


class DoctorManager(SoftDeleteManager.from_queryset(DoctorQuerySet)):
    """Manager for Doctor model."""
