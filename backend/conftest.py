import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_docker")

import django
django.setup()

import pytest
from django.conf import settings


@pytest.fixture(scope='session')
def django_db_setup():
    """Configure database settings for tests."""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'medisoft'),
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
