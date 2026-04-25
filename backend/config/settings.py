import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'change-me-in-production'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'apps.core.organizations',
    'apps.core.users',
    'apps.core.roles',
    'apps.core.permissions_app',
    'apps.core.user_roles',
    'apps.core.role_permissions',
    'apps.core.audit',
    'apps.core.access_logs',
    'apps.patients',
    'apps.doctors',
    'apps.appointments',
    'apps.encounters',
    'apps.clinical',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'medisoft'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

USE_TZ = True
TIME_ZONE = 'America/Santo_Domingo'
LANGUAGE_CODE = 'es-do'
