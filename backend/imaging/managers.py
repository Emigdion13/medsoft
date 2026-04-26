"""
Imaging app managers with domain-specific query methods.
"""

from django.db import models

from core.models import SoftDeleteQuerySet, SoftDeleteManager


class ImagingTypeCatalogQuerySet(SoftDeleteQuerySet):
    """Custom queryset for ImagingTypeCatalog model."""

    def active_types(self):
        """Return active imaging types."""
        return self.filter(is_active=True)

    def by_modality(self, modality: str):
        """Filter by modality (RX, US, CT, MRI, etc.)."""
        return self.filter(modality=modality)

    def by_code(self, code: str):
        """Find type by catalog code."""
        return self.filter(code=code)


class ImagingOrderQuerySet(SoftDeleteQuerySet):
    """Custom queryset for ImagingOrder model."""

    def by_organization(self, organization_id: int):
        """Find orders from a specific organization."""
        return self.filter(organization_id=organization_id)

    def by_encounter(self, encounter_id: int):
        """Find orders for a specific encounter."""
        return self.filter(encounter_id=encounter_id)

    def by_patient(self, patient_id: int):
        """Find orders for a specific patient."""
        return self.filter(patient_id=patient_id)

    def by_doctor(self, doctor_id: int):
        """Find orders placed by a specific doctor."""
        return self.filter(doctor_id=doctor_id)

    def by_status(self, status: str):
        """Filter orders by status."""
        return self.filter(status=status)

    def pending(self):
        """Return pending orders."""
        return self.by_status('PENDIENTE')

    def completed(self):
        """Return completed orders."""
        return self.filter(status='COMPLETADA')

    def urgent(self):
        """Return urgent priority orders."""
        return self.filter(priority='URGENTE')

    def by_imaging_type(self, imaging_type_id: int):
        """Find orders for a specific imaging type."""
        return self.filter(imaging_type_id=imaging_type_id)

    def date_range(self, start_date, end_date):
        """Filter orders within a date range."""
        return self.filter(
            ordered_at__date__range=(start_date, end_date)
        )

    def with_report(self):
        """Prefetch imaging report for orders."""
        return self.prefetch_related('imagingreport')


class ImagingReportQuerySet(SoftDeleteQuerySet):
    """Custom queryset for ImagingReport model."""

    def by_order(self, order_id: int):
        """Find report for a specific order."""
        return self.filter(imaging_order_id=order_id)

    def by_status(self, status: str):
        """Filter reports by status."""
        return self.filter(status=status)

    def signed_reports(self):
        """Return signed imaging reports."""
        return self.filter(status='FIRMADA')

    def draft_reports(self):
        """Return draft imaging reports."""
        return self.filter(status='BORRADOR')

    def with_radiologist(self):
        """Prefetch radiologist user."""
        return self.prefetch_related('radiologist_user')


class ImagingFileQuerySet(SoftDeleteQuerySet):
    """Custom queryset for ImagingFile model."""

    def by_order(self, order_id: int):
        """Find files for a specific order."""
        return self.filter(imaging_order_id=order_id)

    def by_type(self, file_type: str):
        """Filter files by type (DICOM, PDF, JPG, etc.)."""
        return self.filter(file_type=file_type)

    def uploaded_date_range(self, start_datetime, end_datetime):
        """Filter files within an upload date range."""
        return self.filter(
            uploaded_at__range=(start_datetime, end_datetime)
        )

    def with_uploader(self):
        """Prefetch user who uploaded the file."""
        return self.prefetch_related('uploaded_by')


class ImagingTypeCatalogManager(SoftDeleteManager.from_queryset(ImagingTypeCatalogQuerySet)):
    """Manager for ImagingTypeCatalog model."""


class ImagingOrderManager(SoftDeleteManager.from_queryset(ImagingOrderQuerySet)):
    """Manager for ImagingOrder model."""


class ImagingReportManager(SoftDeleteManager.from_queryset(ImagingReportQuerySet)):
    """Manager for ImagingReport model."""


class ImagingFileManager(SoftDeleteManager.from_queryset(ImagingFileQuerySet)):
    """Manager for ImagingFile model."""
