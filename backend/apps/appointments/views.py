from typing import Any

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Appointment
from .serializers import AppointmentSerializer


class AppointmentPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500


class AppointmentViewSet(viewsets.ModelViewSet):
    """CRUD operations for medical appointments."""

    queryset = Appointment.objects.select_related(
        'patient', 'doctor', 'created_by', 'updated_by', 'organization'
    ).order_by('-start_at')
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = AppointmentPagination

    def get_queryset(self) -> Any:
        """Filter by organization, date range, and user role."""
        qs = super().get_queryset()

        user = self.request.user
        if hasattr(user, 'organization') and user.organization:
            qs = qs.filter(organization=user.organization)

        params = self.request.query_params

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

        # Filter by appointment type
        appt_type = params.get('appointment_type')
        if appt_type:
            qs = qs.filter(appointment_type=appt_type)

        # Date range filter on start_at
        date_from = params.get('date_from')
        date_to = params.get('date_to')
        if date_from or date_to:
            from django.db.models import Q
            filters = Q()
            if date_from:
                filters &= Q(start_at__gte=date_from)
            if date_to:
                filters &= Q(start_at__lte=date_to)
            qs = qs.filter(filters)

        return qs.distinct()

    def perform_create(self, serializer: AppointmentSerializer) -> None:
        """Set organization and audit fields from request user."""
        request = self.request
        if hasattr(request, 'user') and hasattr(request.user, 'organization'):
            serializer.save(organization=request.user.organization)
        else:
            serializer.save()

    def perform_update(self, serializer: AppointmentSerializer) -> None:
        """Update audit field with request user."""
        request = self.request
        if hasattr(request, 'user'):
            serializer.save(updated_by=request.user)
