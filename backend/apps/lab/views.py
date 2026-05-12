from typing import Any

from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import LabTestCatalog, LabOrder, LabOrderItem, LabResult
from .serializers import (
    LabTestCatalogSerializer,
    LabOrderSerializer,
    LabOrderItemSerializer,
    LabResultSerializer,
)


class LabPagination:
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500


class LabTestCatalogViewSet(viewsets.ModelViewSet):
    """CRUD operations for lab test catalog."""

    queryset = LabTestCatalog.objects.all().order_by('name')
    serializer_class = LabTestCatalogSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LabPagination

    def get_queryset(self) -> Any:
        """Filter by active status."""
        qs = super().get_queryset()

        is_active = self.request.query_params.get('is_active')

        if is_active is not None:
            if is_active.lower() == 'true':
                qs = qs.filter(is_active=True)
            elif is_active.lower() == 'false':
                qs = qs.filter(is_active=False)

        return qs


class LabOrderViewSet(viewsets.ModelViewSet):
    """CRUD operations for lab orders."""

    queryset = LabOrder.objects.select_related(
        'patient', 'doctor', 'encounter__organization',
        'created_by', 'updated_by'
    ).order_by('-ordered_at')
    serializer_class = LabOrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LabPagination

    def get_queryset(self) -> Any:
        """Filter by organization."""
        qs = super().get_queryset()

        user = self.request.user
        if hasattr(user, 'organization') and user.organization:
            qs = qs.filter(organization=user.organization)

        params = self.request.query_params

        # Filter by encounter
        encounter_id = params.get('encounter_id')
        if encounter_id:
            qs = qs.filter(encounter_id=encounter_id)

        # Filter by patient
        patient_id = params.get('patient_id')
        if patient_id:
            qs = qs.filter(patient_id=patient_id)

        # Filter by doctor
        doctor_id = params.get('doctor_id')
        if doctor_id:
            qs = qs.filter(doctor_id=doctor_id)

        # Filter by status
        status_param = params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)

        # Filter by priority
        priority_param = params.get('priority')
        if priority_param:
            qs = qs.filter(priority=priority_param)

        return qs.distinct()

    def perform_create(self, serializer: LabOrderSerializer) -> None:
        """Set organization and created_by from request user."""
        request = self.request
        if hasattr(request, 'user') and hasattr(request.user, 'organization'):
            serializer.save(
                organization=request.user.organization,
                created_by=request.user
            )
        else:
            serializer.save(created_by=request.user)


class LabOrderItemViewSet(viewsets.ModelViewSet):
    """CRUD operations for lab order items."""

    queryset = LabOrderItem.objects.select_related(
        'lab_order', 'lab_test'
    ).order_by('id')
    serializer_class = LabOrderItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LabPagination

    def get_queryset(self) -> Any:
        """Filter by organization (via lab order)."""
        qs = super().get_queryset()

        user = self.request.user
        if hasattr(user, 'organization') and user.organization:
            qs = qs.filter(lab_order__organization=user.organization)

        params = self.request.query_params

        # Filter by lab order
        lab_order_id = params.get('lab_order_id')
        if lab_order_id:
            qs = qs.filter(lab_order_id=lab_order_id)

        # Filter by status
        status_param = params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)

        return qs.distinct()

    def perform_create(self, serializer: LabOrderItemSerializer) -> None:
        """Set lab_order from request context or validated data."""
        request = self.request
        lab_order_id = request.data.get('lab_order_id') if hasattr(request, 'data') else None
        if lab_order_id:
            try:
                from .models import LabOrder
                lab_order = LabOrder.objects.get(pk=lab_order_id)
                serializer.save(lab_order=lab_order)
            except LabOrder.DoesNotExist:
                raise serializers.ValidationError(
                    {'lab_order_id': 'Invalid lab order ID'}
                )
        else:
            serializer.save()


class LabResultViewSet(viewsets.ModelViewSet):
    """CRUD operations for lab results."""

    queryset = LabResult.objects.select_related(
        'processed_by', 'reviewed_by', 'lab_order_item__lab_order__organization'
    ).order_by('-processed_at')
    serializer_class = LabResultSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LabPagination

    def get_queryset(self) -> Any:
        """Filter by organization (via lab order)."""
        qs = super().get_queryset()

        user = self.request.user
        if hasattr(user, 'organization') and user.organization:
            qs = qs.filter(lab_order_item__lab_order__organization=user.organization)

        params = self.request.query_params

        # Filter by lab order item
        lab_order_item_id = params.get('lab_order_item_id')
        if lab_order_item_id:
            qs = qs.filter(lab_order_item_id=lab_order_item_id)

        # Filter by result flag
        result_flag = params.get('result_flag')
        if result_flag:
            qs = qs.filter(result_flag=result_flag)

        return qs.distinct()

    def perform_create(self, serializer: LabResultSerializer) -> None:
        """Set processed_by from request user."""
        request = self.request
        if hasattr(request, 'user'):
            serializer.save(processed_by=request.user)
