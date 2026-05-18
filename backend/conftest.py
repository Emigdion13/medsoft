import os

# Set Django settings module - use test settings (SQLite in-memory)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_test")

import pytest


@pytest.fixture
def api_client():
    """Django REST framework API client."""
    from rest_framework.test import APIClient
    return APIClient()
