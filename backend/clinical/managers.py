"""
Clinical app managers with domain-specific query methods.
"""

from django.db import models

from core.models import SoftDeleteQuerySet, SoftDeleteManager


class ClinicalNoteQuerySet(SoftDeleteQuerySet):
    """Custom queryset for ClinicalNote model."""

    def by_encounter(self, encounter_id: int):
        """Find notes for a specific encounter."""
        return self.filter(encounter_id=encounter_id)

    def by_status(self, status: str):
        """Filter notes by status."""
        return self.filter(status=status)

    def signed(self):
        """Return signed clinical notes."""
        return self.filter(status='FIRMADA')

    def draft(self):
        """Return draft clinical notes."""
        return self.filter(status='BORRADOR')

    def by_type(self, note_type: str):
        """Filter notes by type (EVOLUCION, HISTORIA, etc.)."""
        return self.filter(note_type=note_type)

    def recent(self, limit: int = 10):
        """Get most recent clinical notes."""
        return self.order_by('-created_at')[:limit]

    def by_patient(self, patient_id: int):
        """Find notes for a specific patient through encounter."""
        return self.filter(encounter__patient_id=patient_id)

    def with_singer(self):
        """Prefetch user who signed the note."""
        return self.prefetch_related('signed_by')


class DiagnosisQuerySet(SoftDeleteQuerySet):
    """Custom queryset for Diagnosis model."""

    def by_encounter(self, encounter_id: int):
        """Find diagnoses for a specific encounter."""
        return self.filter(encounter_id=encounter_id)

    def primary(self):
        """Return primary diagnoses only."""
        return self.filter(is_primary=True)

    def by_type(self, diagnosis_type: str):
        """Filter diagnoses by type (PRINCIPAL, SECUNDARIO, etc.)."""
        return self.filter(diagnosis_type=diagnosis_type)

    def by_status(self, status: str):
        """Filter diagnoses by status."""
        return self.filter(status=status)

    def active(self):
        """Return active diagnoses."""
        return self.filter(status='ACTIVO')

    def resolved(self):
        """Return resolved diagnoses."""
        return self.filter(status='RESUELTO')

    def icd10_code(self, code: str):
        """Find diagnosis by ICD-10 code."""
        return self.filter(icd10_code=code)


class PrescriptionQuerySet(SoftDeleteQuerySet):
    """Custom queryset for Prescription model."""

    def by_encounter(self, encounter_id: int):
        """Find prescriptions for a specific encounter."""
        return self.filter(encounter_id=encounter_id)

    def active_prescriptions(self):
        """Return active (not cancelled) prescriptions."""
        return self.exclude(status='CANCELADA')

    def by_status(self, status: str):
        """Filter prescriptions by status."""
        return self.filter(status=status)

    def due_today(self):
        """Find prescriptions that should be taken today."""
        from django.utils import timezone
        # Note: This is a simplified version; real implementation would need
        # more complex logic with frequency/duration fields
        return self.active_prescriptions()

    def by_medication(self, medication_name: str):
        """Find prescriptions for a specific medication."""
        return self.filter(medication_name__icontains=medication_name)

    def by_route(self, route: str):
        """Filter prescriptions by administration route."""
        return self.filter(route=route)


class ClinicalNoteManager(SoftDeleteManager.from_queryset(ClinicalNoteQuerySet)):
    """Manager for ClinicalNote model."""


class DiagnosisManager(SoftDeleteManager.from_queryset(DiagnosisQuerySet)):
    """Manager for Diagnosis model."""


class PrescriptionManager(SoftDeleteManager.from_queryset(PrescriptionQuerySet)):
    """Manager for Prescription model."""
