from typing import Any

from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from django.utils import timezone

from apps.core.users.models import User
from apps.doctors.models import Specialty, Doctor
from apps.patients.models import Patient
from apps.appointments.models import Appointment

from .serializers import (
    AuthResponseSerializer,
    LoginSerializer,
    RegisterSerializer,
    TokenRefreshSerializer,
    UserSerializer,
    SpecialtySerializer,
    DoctorSerializer,
    PatientSerializer,
    AppointmentSerializer,
)
from .token_utils import get_tokens_for_user


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request: Request) -> Response:
    """Login user and return tokens."""
    serializer = LoginSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
    except Exception:
        # Return generic error to avoid username enumeration
        return Response(
            {'detail': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    username = serializer.validated_data['username']
    password = serializer.validated_data['password']

    try:
        user = User.objects.get(username=username, is_active=True)
        if not user.check_password(password):
            return Response(
                {'detail': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        tokens = get_tokens_for_user(user)

        response_serializer = AuthResponseSerializer({
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'user': user,
        })
        return Response(response_serializer.data)

    except User.DoesNotExist:
        return Response(
            {'detail': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED,
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request: Request) -> Response:
    """Register new user and return tokens."""
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.save()
    tokens = get_tokens_for_user(user)

    response_serializer = AuthResponseSerializer({
        'access': tokens['access'],
        'refresh': tokens['refresh'],
        'user': user,
    })
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request: Request) -> Response:
    """Refresh access token."""
    serializer = TokenRefreshSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    refresh_token = serializer.validated_data['refresh']

    # Use SimpleJWT to validate and refresh the token
    from rest_framework_simplejwt.tokens import RefreshToken

    try:
        refresh = RefreshToken(refresh_token)
        access_token = str(refresh.access_token)
        
        return Response({
            'access': access_token,
            'refresh': refresh_token,
        })
    except Exception:
        return Response(
            {'detail': 'Invalid refresh token'},
            status=status.HTTP_401_UNAUTHORIZED,
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request: Request) -> Response:
    """Get current user profile."""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class UserPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class UserViewSet(viewsets.ModelViewSet):
    """CRUD operations for users."""

    queryset = User.objects.filter(is_active=True, deleted_at__isnull=True).order_by('-created_at')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = UserPagination

    def get_queryset(self) -> Any:
        """Filter queryset based on current user scope."""
        queryset = super().get_queryset()

        # Filter by organization (same org as requesting user)
        user = self.request.user
        if hasattr(user, 'organization') and user.organization:
            queryset = queryset.filter(organization=user.organization)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )

        return queryset.distinct()

    def perform_create(self, serializer: UserSerializer) -> None:
        """Set organization from the requesting user."""
        serializer.save(organization=self.request.user.organization)

    def perform_update(self, serializer: UserSerializer) -> None:
        """Handle role updates and other business logic."""
        serializer.save()

    def perform_destroy(self, instance: User) -> None:
        """Soft delete user."""
        instance.deleted_at = timezone.now()
        instance.save(update_fields=['deleted_at'])


# ── Specialty ViewSet ─────────────────────────────────────────────────

class SpecialtyViewSet(viewsets.ModelViewSet):
    """CRUD operations for medical specialties."""

    queryset = Specialty.objects.filter(is_active=True)
    serializer_class = SpecialtySerializer
    permission_classes = [IsAuthenticated]


# ── Doctor ViewSet ────────────────────────────────────────────────────

class DoctorPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class DoctorViewSet(viewsets.ModelViewSet):
    """CRUD operations for doctors."""

    queryset = Doctor.objects.filter(is_active=True, deleted_at__isnull=True)
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DoctorPagination

    def get_queryset(self) -> Any:
        """Filter by organization and optionally search."""
        qs = super().get_queryset()

        # Filter by the organization of the authenticated user
        user = self.request.user
        if hasattr(user, 'organization') and user.organization:
            qs = qs.filter(organization=user.organization)

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                first_name__icontains=search
            ) | qs.filter(
                last_name__icontains=search
            ) | qs.filter(
                cedula__icontains=search
            )

        return qs

    def perform_create(self, serializer: Any) -> None:
        """Set organization from the requesting user."""
        serializer.save(organization=self.request.user.organization)


# ── Patient ViewSet ───────────────────────────────────────────────────

class PatientPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class PatientViewSet(viewsets.ModelViewSet):
    """CRUD operations for patients."""

    queryset = Patient.objects.filter(deleted_at__isnull=True)
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PatientPagination

    def get_queryset(self) -> Any:
        """Filter by organization and optionally search."""
        qs = super().get_queryset()

        # Filter by the organization of the authenticated user
        user = self.request.user
        if hasattr(user, 'organization') and user.organization:
            qs = qs.filter(organization=user.organization)

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                first_name__icontains=search
            ) | qs.filter(
                last_name__icontains=search
            ) | qs.filter(
                cedula__icontains=search
            )

        return qs

    def perform_create(self, serializer: Any) -> None:
        """Set organization from the requesting user."""
        serializer.save(organization=self.request.user.organization)


# ── Appointment ViewSet ───────────────────────────────────────────────

class AppointmentPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class AppointmentViewSet(viewsets.ModelViewSet):
    """CRUD operations for appointments."""

    queryset = Appointment.objects.select_related(
        'doctor', 'patient', 'created_by'
    ).order_by('-start_at')
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = AppointmentPagination

    def get_queryset(self) -> Any:
        """Filter by organization and optionally by date."""
        qs = super().get_queryset()

        user = self.request.user
        if hasattr(user, 'organization') and user.organization:
            org = user.organization
            # Filter appointments belonging to the user's organization
            # (appointment itself, or via doctor/patient)
            qs = qs.filter(
                Q(organization=org) |
                Q(doctor__organization=org) |
                Q(patient__organization=org)
            )

        # Filter by date range if provided
        date_param = self.request.query_params.get('date')
        if date_param:
            qs = qs.filter(
                Q(start_at__date=date_param)
                | Q(end_at__date=date_param)
            )

        return qs

    def perform_create(self, serializer: AppointmentSerializer) -> None:
        """Let the serializer handle organization and created_by assignment."""
        serializer.save()
