from typing import Any

from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ImagingTypeCatalog, ImagingOrder, ImagingReport, ImagingFile
from .serializers import (
    ImagingTypeCatalogSerializer,
    ImagingOrderSerializer,
    ImagingReportSerializer,
    ImagingFileSerializer,
)


class ImagingPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500


class ImagingTypeCatalogViewSet(viewsets.ModelViewSet):
    """CRUD operations for imaging type catalog."""

    queryset = ImagingTypeCatalog.objects.all().order_by('name')
    serializer_class = ImagingTypeCatalogSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ImagingPagination

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


class ImagingOrderViewSet(viewsets.ModelViewSet):
    """CRUD operations for imaging orders."""

    queryset = ImagingOrder.objects.select_related(
        'patient', 'doctor', 'encounter__organization',
        'imaging_type', 'created_by', 'updated_by'
    ).order_by('-ordered_at')
    serializer_class = ImagingOrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ImagingPagination

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

        # Filter by imaging type
        imaging_type_id = params.get('imaging_type_id')
        if imaging_type_id:
            qs = qs.filter(imaging_type_id=imaging_type_id)

        # Filter by status
        status_param = params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)

        # Filter by priority
        priority_param = params.get('priority')
        if priority_param:
            qs = qs.filter(priority=priority_param)

        return qs.distinct()

    def perform_create(self, serializer: ImagingOrderSerializer) -> None:
        """Set organization and created_by from request user."""
        request = self.request
        if hasattr(request, 'user') and hasattr(request.user, 'organization'):
            serializer.save(
                organization=request.user.organization,
                created_by=request.user
            )
        else:
            serializer.save(created_by=request.user)


class ImagingReportViewSet(viewsets.ModelViewSet):
    """CRUD operations for imaging reports."""

    queryset = ImagingReport.objects.select_related(
        'technician_user', 'radiologist_user', 'imaging_order__organization'
    ).order_by('-performed_at')
    serializer_class = ImagingReportSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ImagingPagination

    def get_queryset(self) -> Any:
        """Filter by organization (via imaging order)."""
        qs = super().get_queryset()

        user = self.request.user
        if hasattr(user, 'organization') and user.organization:
            qs = qs.filter(imaging_order__organization=user.organization)

        params = self.request.query_params

        # Filter by imaging order
        imaging_order_id = params.get('imaging_order_id')
        if imaging_order_id:
            qs = qs.filter(imaging_order_id=imaging_order_id)

        # Filter by status
        status_param = params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)

        return qs.distinct()

    def perform_create(self, serializer: ImagingReportSerializer) -> None:
        """Set technician_user from request user."""
        request = self.request
        if hasattr(request, 'user'):
            serializer.save(technician_user=request.user)


class ImagingFileViewSet(viewsets.ModelViewSet):
    """CRUD operations for imaging files."""

    queryset = ImagingFile.objects.select_related(
        'uploaded_by', 'imaging_order__organization'
    ).order_by('-uploaded_at')
    serializer_class = ImagingFileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ImagingPagination

    def get_queryset(self) -> Any:
        """Filter by organization (via imaging order)."""
        qs = super().get_queryset()

        user = self.request.user
        if hasattr(user, 'organization') and user.organization:
            qs = qs.filter(imaging_order__organization=user.organization)

        params = self.request.query_params

        # Filter by imaging order
        imaging_order_id = params.get('imaging_order_id')
        if imaging_order_id:
            qs = qs.filter(imaging_order_id=imaging_order_id)

        return qs.distinct()

    def perform_create(self, serializer: ImagingFileSerializer) -> None:
        """Set uploaded_by from request user."""
        request = self.request
        if hasattr(request, 'user'):
            serializer.save(updated_by=request.user)
