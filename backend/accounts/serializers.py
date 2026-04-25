from rest_framework import serializers

from apps.core.users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    id = serializers.UUIDField(source='pk', read_only=True)
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'role',
            'is_active',
        ]
        read_only_fields = ['id', 'is_active']

    def get_role(self, obj: User) -> str:
        """Get primary role for user."""
        # TODO: Implement actual role lookup via user_roles table
        return 'RECEPTIONIST'  # Default fallback


class LoginSerializer(serializers.Serializer):
    """Serializer for login endpoint."""

    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for registration endpoint."""

    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'confirm_password',
        ]

    def validate(self, attrs: dict) -> dict:
        """Validate password confirmation matches."""
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match'})
        return attrs

    def create(self, validated_data: dict) -> User:
        """Create user with hashed password."""
        # TODO: Implement proper password hashing
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
        )
        return user


class TokenRefreshSerializer(serializers.Serializer):
    """Serializer for token refresh endpoint."""

    refresh = serializers.CharField()


class AuthResponseSerializer(serializers.Serializer):
    """Serializer for auth response (tokens + user)."""

    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()
