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
from .token_utils import get_tokens_for_user


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request: Request) -> Response:
    """Login user and return tokens."""
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

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
