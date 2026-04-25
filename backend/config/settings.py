import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'change-me-in-production')

DEBUG = os.environ.get('DJANGO_DEBUG', 'false').lower() == 'true'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'apps.core.organizations.apps.OrganizationsConfig',
    'apps.core.users.apps.UsersConfig',
    'apps.core.roles.apps.RolesConfig',
    'apps.core.permissions_app.apps.PermissionsConfig',
    'apps.core.user_roles.apps.UserRolesConfig',
    'apps.core.role_permissions.apps.RolePermissionsConfig',
    'apps.core.audit.apps.AuditConfig',
    'apps.core.access_logs.apps.AccessLogsConfig',
    'apps.patients',
    'apps.doctors',
    'apps.appointments',
    'apps.encounters',
    'apps.clinical',
]

ROOT_URLCONF = 'config.urls'

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
