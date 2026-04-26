from rest_framework import serializers

from apps.core.users.models import User
from apps.core.organizations.models import Organization


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    id = serializers.UUIDField(source='pk', read_only=True)

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
            'is_staff',
        ]
        read_only_fields = ['id', 'is_active', 'is_staff']


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
        """Validate password confirmation matches and uniqueness."""
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match'})
        
        # Get the organization for uniqueness checks
        org = Organization.objects.first()
        if not org:
            raise serializers.ValidationError({'organization': 'No organization found. Please contact support.'})
        
        # Check for existing user with same username in this organization
        if User.objects.filter(organization=org, username=attrs['username']).exists():
            raise serializers.ValidationError({'username': 'A user with this username already exists in this organization'})
        
        # Check for existing user with same email in this organization  
        if User.objects.filter(organization=org, email=attrs['email'].lower()).exists():
            raise serializers.ValidationError({'email': 'A user with this email already exists in this organization'})
        
        return attrs

    def create(self, validated_data: dict) -> User:
        """Create user with hashed password."""
        # Get the first organization (there should be one from initial setup)
        org = Organization.objects.first()
        if not org:
            raise serializers.ValidationError({'organization': 'No organization found. Please contact support.'})
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
            organization_id=org.id,
        )
        return user


class TokenRefreshSerializer(serializers.Serializer):
    """Serializer for token refresh endpoint."""

    refresh = serializers.CharField()


class AuthResponseSerializer(serializers.Serializer):
    """Serializer for auth response (tokens + user)."""

    access = serializers.CharField(required=False, default='')
    refresh = serializers.CharField(required=False, default='')
    user = UserSerializer()
