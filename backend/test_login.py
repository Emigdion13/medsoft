"""Test script for login functionality using Django test client."""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_docker')
sys.path.insert(0, '/Users/emi/Desktop/projects/medisoft/backend')
django.setup()

from django.test import TestCase, Client
from apps.core.users.models import User
from apps.core.organizations.models import Organization


class LoginTest(TestCase):
    """Test login endpoint."""

    def setUp(self):
        """Set up test data."""
        # Create organization
        self.org = Organization.objects.create(name='Default')

        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123',
            organization=self.org,
        )

    def test_login_success(self):
        """Test successful login."""
        client = Client()
        response = client.post(
            '/api/accounts/login/',
            data={'username': 'testuser', 'password': 'testpass123'},
            content_type='application/json'
        )

        print(f"\nStatus Code: {response.status_code}")
        if response.status_code == 200:
            import json
            data = json.loads(response.content)
            print(f"Response Data: {json.dumps(data, indent=2)}")
            print("\n✓ Login successful!")
        else:
            print(f"Response Content: {response.content.decode()}")
            print("\n✗ Login failed!")

        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    from django.test.utils import get_runner
    from django.conf import settings

    TestRunner = get_runner(settings)
    test_runner = TestRunner()

    # Run the tests
    failures = test_runner.run_tests(['__main__'])
    sys.exit(bool(failures))
