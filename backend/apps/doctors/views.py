from typing import Any

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Doctor, Specialty
from .serializers import DoctorSerializer, SpecialtySerializer


class DoctorPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500


class SpecialtyViewSet(viewsets.ModelViewSet):
    """CRUD operations for medical specialties."""

    queryset = Specialty.objects.all().order_by('name')
    serializer_class = SpecialtySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DoctorPagination

    def get_queryset(self) -> Any:
        """Filter by active status."""
        qs = super().get_queryset()

        params = self.request.query_params
        is_active = params.get('is_active')

        if is_active is not None:
            if is_active.lower() == 'true':
                qs = qs.filter(is_active=True)
            elif is_active.lower() == 'false':
                qs = qs.filter(is_active=False)

        return qs

    def perform_create(self, serializer: SpecialtySerializer) -> None:
        """Set organization from request user."""
        serializer.save()


class DoctorViewSet(viewsets.ModelViewSet):
    """CRUD operations for medical doctors."""

    queryset = Doctor.objects.select_related(
        'user', 'specialty_main', 'created_by', 'updated_by', 'organization'
    ).order_by('-created_at')
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DoctorPagination

    def get_queryset(self) -> Any:
        """Filter by organization and search."""
        qs = super().get_queryset()

        user = self.request.user
        if hasattr(user, 'organization') and user.organization:
            qs = qs.filter(organization=user.organization)

        params = self.request.query_params

        # Search by name or cedula
        search = params.get('search')
        if search:
            qs = qs.filter(
                first_name__icontains=search
            ) | qs.filter(
                last_name__icontains=search
            ) | qs.filter(
                cedula__icontains=search
            )

        # Filter by specialty
        specialty_id = params.get('specialty_id')
        if specialty_id:
            qs = qs.filter(specialty_main_id=specialty_id)

        # Filter by active status
        is_active = params.get('is_active')
        if is_active is not None:
            if is_active.lower() == 'true':
                qs = qs.filter(is_active=True)
            elif is_active.lower() == 'false':
                qs = qs.filter(is_active=False)

        return qs.distinct()

    def perform_create(self, serializer: DoctorSerializer) -> None:
        """Set organization and audit fields from request user."""
        request = self.request
        if hasattr(request, 'user') and hasattr(request.user, 'organization'):
            serializer.save(organization=request.user.organization)
        else:
            serializer.save()

    def perform_update(self, serializer: DoctorSerializer) -> None:
        """Update audit field with request user."""
        request = self.request
        if hasattr(request, 'user'):
            serializer.save(updated_by=request.user)
