from typing import Any

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from django.db.models import Q, Prefetch

from apps.core.users.models import User
from apps.patients.models import Patient

from .models import Encounter, VitalSign
from .serializers import (
    EncounterSerializer,
    VitalSignSerializer,
)


class EncounterPagination:
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500


class EncounterViewSet(viewsets.ModelViewSet):
    """CRUD operations for clinical encounters."""

    queryset = Encounter.objects.select_related(
        'patient', 'doctor', 'appointment', 'created_by', 'updated_by',
        'organization',
    ).prefetch_related(
        Prefetch('vitalsign_set', queryset=VitalSign.objects.order_by('-recorded_at')),
    ).order_by('-start_at')
    serializer_class = EncounterSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = EncounterPagination

    def get_queryset(self) -> Any:
        """Filter by organization, date range, search, and type/status."""
        qs = super().get_queryset()

        # Organization scoping — only encounters for user's org
        user = self.request.user
        if hasattr(user, 'organization') and user.organization:
            qs = qs.filter(organization=user.organization)

        params = self.request.query_params

        # Search by patient name or cedula (via FK join)
        search = params.get('search')
        if search:
            patient_ids = Patient.objects.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(cedula__icontains=search)
            ).values_list('id', flat=True)
            qs = qs.filter(patient_id__in=patient_ids)

        # Filter by encounter type
        enc_type = params.get('encounter_type')
        if enc_type:
            qs = qs.filter(encounter_type=enc_type)

        # Filter by status
        status_param = params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)

        # Date range filter on start_at
        date_from = params.get('date_from')
        date_to = params.get('date_to')
        if date_from or date_to:
            filters = Q()
            if date_from:
                filters &= Q(start_at__gte=date_from)
            if date_to:
                filters &= Q(start_at__lte=date_to)
            qs = qs.filter(filters)

        # Filter by doctor
        doctor_id = params.get('doctor_id')
        if doctor_id:
            qs = qs.filter(doctor_id=doctor_id)

        return qs.distinct()

    def perform_create(self, serializer: EncounterSerializer) -> None:
        """Let serializer handle created_by/updated_by from request user."""
        serializer.save()


class VitalSignViewSet(viewsets.ModelViewSet):
    """CRUD operations for vital signs linked to encounters."""

    queryset = VitalSign.objects.select_related(
        'encounter', 'recorded_by',
        'encounter__patient', 'encounter__doctor', 'encounter__organization',
    ).order_by('-recorded_at')
    serializer_class = VitalSignSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = EncounterPagination

    def get_queryset(self) -> Any:
        """Filter by organization (via encounter) and optionally by encounter_id."""
        qs = super().get_queryset()

        user = self.request.user
        if hasattr(user, 'organization') and user.organization:
            org = user.organization
            qs = qs.filter(encounter__organization=org)

        # Filter by specific encounter
        encounter_id = self.request.query_params.get('encounter_id')
        if encounter_id:
            qs = qs.filter(encounter_id=encounter_id)

        return qs.distinct()

    def perform_create(self, serializer: VitalSignSerializer) -> None:
        """Let serializer handle recorded_by from request user."""
        serializer.save()
