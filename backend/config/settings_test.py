"""Test settings using SQLite for local testing."""
from .settings import *

# Use SQLite for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Add all apps needed for tests
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
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
    'apps.imaging',
    'apps.lab',
]
