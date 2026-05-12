from typing import Any

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Patient
from .serializers import PatientSerializer


class PatientPagination:
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500


class PatientViewSet(viewsets.ModelViewSet):
    """CRUD operations for patient records."""

    queryset = Patient.objects.select_related(
        'created_by', 'updated_by', 'organization'
    ).order_by('-created_at')
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PatientPagination

    def get_queryset(self) -> Any:
        """Filter by organization and search."""
        qs = super().get_queryset()

        user = self.request.user
        if hasattr(user, 'organization') and user.organization:
            qs = qs.filter(organization=user.organization)

        params = self.request.query_params

        # Search by name or cedula/passport
        search = params.get('search')
        if search:
            qs = qs.filter(
                first_name__icontains=search
            ) | qs.filter(
                last_name__icontains=search
            ) | qs.filter(
                cedula__icontains=search
            ) | qs.filter(
                passport_number__icontains=search
            )

        # Filter by status
        status_param = params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)

        # Filter by identity type
        identity_type = params.get('identity_type')
        if identity_type:
            qs = qs.filter(identity_type=identity_type)

        return qs.distinct()

    def perform_create(self, serializer: PatientSerializer) -> None:
        """Set organization and audit fields from request user."""
        request = self.request
        if hasattr(request, 'user') and hasattr(request.user, 'organization'):
            serializer.save(organization=request.user.organization)
        else:
            serializer.save()

    def perform_update(self, serializer: PatientSerializer) -> None:
        """Update audit field with request user."""
        request = self.request
        if hasattr(request, 'user'):
            serializer.save(updated_by=request.user)
