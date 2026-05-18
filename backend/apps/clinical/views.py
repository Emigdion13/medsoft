from typing import Any

from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ClinicalNote, Diagnosis, Prescription
from .serializers import (
    ClinicalNoteSerializer,
    DiagnosisSerializer,
    PrescriptionSerializer,
)


class ClinicalNotePagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500


class ClinicalNoteViewSet(viewsets.ModelViewSet):
    """CRUD operations for clinical notes."""

    queryset = ClinicalNote.objects.select_related(
        'doctor', 'signed_by', 'created_by', 'updated_by', 'encounter',
    ).order_by('-created_at')
    serializer_class = ClinicalNoteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ClinicalNotePagination

    def get_queryset(self) -> Any:
        """Filter by organization (via encounter)."""
        qs = super().get_queryset()

        user = self.request.user
        if hasattr(user, 'organization') and user.organization:
            qs = qs.filter(encounter__organization=user.organization)

        params = self.request.query_params

        # Filter by encounter
        encounter_id = params.get('encounter_id')
        if encounter_id:
            qs = qs.filter(encounter_id=encounter_id)

        # Filter by doctor
        doctor_id = params.get('doctor_id')
        if doctor_id:
            qs = qs.filter(doctor_id=doctor_id)

        # Filter by status
        status_param = params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)

        # Filter by note type
        note_type = params.get('note_type')
        if note_type:
            qs = qs.filter(note_type=note_type)

        return qs.distinct()

    def perform_create(self, serializer: ClinicalNoteSerializer) -> None:
        """Set created_by from request user."""
        request = self.request
        if hasattr(request, 'user'):
            serializer.save(created_by=request.user)


class DiagnosisViewSet(viewsets.ModelViewSet):
    """CRUD operations for diagnosis records (ICD-10)."""

    queryset = Diagnosis.objects.select_related(
        'recorded_by', 'encounter__organization'
    ).order_by('-recorded_at')
    serializer_class = DiagnosisSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ClinicalNotePagination

    def get_queryset(self) -> Any:
        """Filter by organization (via encounter)."""
        qs = super().get_queryset()

        user = self.request.user
        if hasattr(user, 'organization') and user.organization:
            qs = qs.filter(encounter__organization=user.organization)

        params = self.request.query_params

        # Filter by encounter
        encounter_id = params.get('encounter_id')
        if encounter_id:
            qs = qs.filter(encounter_id=encounter_id)

        # Filter by status
        status_param = params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)

        # Filter by type
        diag_type = params.get('diagnosis_type')
        if diag_type:
            qs = qs.filter(diagnosis_type=diag_type)

        return qs.distinct()

    def perform_create(self, serializer: DiagnosisSerializer) -> None:
        """Set recorded_by from request user."""
        request = self.request
        if hasattr(request, 'user'):
            serializer.save(recorded_by=request.user)


class PrescriptionViewSet(viewsets.ModelViewSet):
    """CRUD operations for prescription records."""

    queryset = Prescription.objects.select_related(
        'prescribed_by', 'encounter__organization'
    ).order_by('-prescribed_at')
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ClinicalNotePagination

    def get_queryset(self) -> Any:
        """Filter by organization (via encounter)."""
        qs = super().get_queryset()

        user = self.request.user
        if hasattr(user, 'organization') and user.organization:
            qs = qs.filter(encounter__organization=user.organization)

        params = self.request.query_params

        # Filter by encounter
        encounter_id = params.get('encounter_id')
        if encounter_id:
            qs = qs.filter(encounter_id=encounter_id)

        # Filter by status
        status_param = params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)

        return qs.distinct()

    def perform_create(self, serializer: PrescriptionSerializer) -> None:
        """Set prescribed_by from request user."""
        request = self.request
        if hasattr(request, 'user'):
            serializer.save(prescribed_by=request.user)
