from typing import Any

from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from django.utils import timezone

from apps.core.users.models import User

from .serializers import (
    AuthResponseSerializer,
    LoginSerializer,
    RegisterSerializer,
    TokenRefreshSerializer,
    UserSerializer,
)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request: Request) -> Response:
    """Login user and return tokens."""
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data['username']
    password = serializer.validated_data['password']

    # TODO: Implement proper authentication
    try:
        user = User.objects.get(username=username, is_active=True)
        # TODO: Verify password
        if not user.check_password(password):
            return Response(
                {'detail': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # TODO: Generate tokens
        # TODO: Update last_login_at

        response_serializer = AuthResponseSerializer({
            'access': '',
            'refresh': '',
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
    """Register new user."""
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.save()

    # TODO: Generate tokens for newly registered user

    response_serializer = AuthResponseSerializer({
        'access': '',
        'refresh': '',
        'user': user,
    })
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request: Request) -> Response:
    """Refresh access token."""
    serializer = TokenRefreshSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # TODO: Implement token refresh logic
    refresh_token = serializer.validated_data['refresh']

    return Response({'detail': 'Not implemented yet'}, status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request: Request) -> Response:
    """Get current user profile."""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    """CRUD operations for users."""

    queryset = User.objects.filter(is_active=True, deleted_at__isnull=True).order_by('-created_at')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> Any:
        """Filter queryset based on current user scope."""
        queryset = super().get_queryset()

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                username__icontains=search
            ) | queryset.filter(
                first_name__icontains=search
            ) | queryset.filter(
                last_name__icontains=search
            )

        return queryset

    def perform_create(self, serializer: UserSerializer) -> None:
        """Set organization on create."""
        # TODO: Set organization from request.user.organization
        serializer.save()

    def perform_update(self, serializer: UserSerializer) -> None:
        """Handle role updates and other business logic."""
        serializer.save()

    def perform_destroy(self, instance: User) -> None:
        """Soft delete user."""
        instance.deleted_at = timezone.now()
        instance.save(update_fields=['deleted_at'])
