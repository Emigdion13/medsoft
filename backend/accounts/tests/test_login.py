import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_docker")

import pytest
from django.conf import settings

# Configure Django before importing models
import django
django.setup()

from accounts.serializers import LoginSerializer
from apps.core.organizations.models import Organization
from apps.core.users.models import User


pytestmark = pytest.mark.django_db(transaction=True)


class TestLoginSerializer:
    """Test login serializer functionality."""

    @pytest.fixture
    def org(self):
        """Create a test organization."""
        return Organization.objects.get_or_create(
            name="Test Org",
            defaults={
                "phone": "+1234567890",
                "email": "test@example.com",
                "address": "123 Test St"
            }
        )[0]

    @pytest.fixture
    def user(self, org):
        """Create a test user."""
        return User.objects.create_user(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="testpass123",
            organization_id=org.id
        )

    def test_login_serializer_validates_credentials(self, user):
        """Test that login serializer validates username and password fields."""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        serializer = LoginSerializer(data=data)
        assert serializer.is_valid(), f"Expected valid data, got errors: {serializer.errors}"
        
        # Serializer should validate and return username/password
        validated_data = serializer.validated_data
        assert 'username' in validated_data
        assert 'password' in validated_data
        assert validated_data['username'] == 'testuser'

    def test_login_serializer_invalid_username(self, org):
        """Test login serializer with non-existent username."""
        data = {
            'username': 'nonexistent',
            'password': 'testpass123'
        }
        
        serializer = LoginSerializer(data=data)
        # Serializer itself doesn't validate if user exists - that's done in the view
        assert serializer.is_valid()

    def test_login_serializer_missing_fields(self, org):
        """Test login serializer with missing required fields."""
        data = {
            'username': 'testuser'
        }
        
        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors

    def test_login_serializer_empty_data(self, org):
        """Test login serializer with empty data."""
        serializer = LoginSerializer(data={})
        assert not serializer.is_valid()
        assert 'username' in serializer.errors
        assert 'password' in serializer.errors
