"""
Lab app managers with domain-specific query methods.
"""

from django.db import models

from core.models import SoftDeleteQuerySet, SoftDeleteManager


class LabTestCatalogQuerySet(SoftDeleteQuerySet):
    """Custom queryset for LabTestCatalog model."""

    def active_tests(self):
        """Return active lab tests."""
        return self.filter(is_active=True)

    def by_category(self, category: str):
        """Filter tests by category (if added in future)."""
        return self

    def by_code(self, code: str):
        """Find test by catalog code."""
        return self.filter(code=code)


class LabOrderQuerySet(SoftDeleteQuerySet):
    """Custom queryset for LabOrder model."""

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
        return self.by_status('COMPLETADA')

    def urgent(self):
        """Return urgent priority orders."""
        return self.filter(priority='URGENTE')

    def date_range(self, start_date, end_date):
        """Filter orders within a date range."""
        return self.filter(
            ordered_at__date__range=(start_date, end_date)
        )

    def with_results(self):
        """Prefetch lab results for orders."""
        return self.prefetch_related('laborderitem_set__labresult_set')


class LabOrderItemQuerySet(SoftDeleteQuerySet):
    """Custom queryset for LabOrderItem model."""

    def by_order(self, order_id: int):
        """Find items in a specific order."""
        return self.filter(lab_order_id=order_id)

    def by_test(self, test_id: int):
        """Find items for a specific lab test."""
        return self.filter(lab_test_id=test_test)

    def pending_items(self):
        """Return pending order items."""
        return self.filter(status='PENDIENTE')

    def completed_items(self):
        """Return completed order items."""
        return self.exclude(status='PENDIENTE')


class LabResultQuerySet(SoftDeleteQuerySet):
    """Custom queryset for LabResult model."""

    def by_order_item(self, item_id: int):
        """Find results for a specific order item."""
        return self.filter(lab_order_item_id=item_id)

    def by_flag(self, flag: str):
        """Filter results by flag (NORMAL, ANORMAL, CRITICO)."""
        return self.filter(result_flag=flag)

    def abnormal_results(self):
        """Return abnormal or critical results."""
        return self.filter(result_flag__in=['ANORMAL', 'CRITICO'])

    def critical_results(self):
        """Return only critical results."""
        return self.filter(result_flag='CRITICO')

    def by_date_range(self, start_datetime, end_datetime):
        """Filter results within a datetime range."""
        return self.filter(
            processed_at__range=(start_datetime, end_datetime)
        )

    def with_reviewer(self):
        """Prefetch user who reviewed the result."""
        return self.prefetch_related('reviewed_by')


class LabTestCatalogManager(SoftDeleteManager.from_queryset(LabTestCatalogQuerySet)):
    """Manager for LabTestCatalog model."""


class LabOrderManager(SoftDeleteManager.from_queryset(LabOrderQuerySet)):
    """Manager for LabOrder model."""


class LabOrderItemManager(SoftDeleteManager.from_queryset(LabOrderItemQuerySet)):
    """Manager for LabOrderItem model."""


class LabResultManager(SoftDeleteManager.from_queryset(LabResultQuerySet)):
    """Manager for LabResult model."""
