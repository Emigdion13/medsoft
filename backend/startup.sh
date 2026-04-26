#!/bin/bash

set -e

echo "Starting Medisoft backend..."

# Wait for database to be ready
echo "Waiting for PostgreSQL..."
while ! pg_isready -h $DB_HOST -p ${DB_PORT:-5432} -U $DB_USER; do
    sleep 1
done
echo "PostgreSQL is ready!"

# Apply migrations (use --fake-initial if database is empty)
echo "Running migrations..."
python manage.py migrate --noinput --fake-initial || python manage.py migrate --noinput

# Create default organization if not exists
echo "Checking/defaulting organization..."
python manage.py shell <<EOF
from apps.core.organizations.models import Organization
org, created = Organization.objects.get_or_create(
    name="Default Organization",
    defaults={
        'rnc': '123456789',
        'phone': '+1-809-000-0000',
        'email': 'contact@medisoft.local',
        'address': 'Default address',
        'province': 'Santo Domingo',
        'municipality': 'Santo Domingo',
        'is_active': True,
    }
)
print(f"Organization {'created' if created else 'exists'}: {org.name}")
EOF

# Create default admin user if not exists
echo "Checking/defaulting admin user..."
python manage.py shell <<EOF
from apps.core.users.models import User
from apps.core.organizations.models import Organization
import os

org = Organization.objects.first()
if org:
    password = os.environ.get('DJANGO_ADMIN_PASSWORD', 'admin123')
    email = os.environ.get('DJANGO_ADMIN_EMAIL', 'admin@medisoft.local')
    
    # Get or create the admin user with correct superuser status
    user, created = User.objects.get_or_create(
        username="admin",
        defaults={
            'organization': org,
            'email': email,
            'first_name': 'System',
            'last_name': 'Administrator',
        }
    )
    
    # Always ensure admin has correct password, superuser status, and email
    if not user.check_password(password):
        user.set_password(password)
    
    # Update email and role to match current config
    user.email = email
    user.role = 'ADMINISTRATOR'
    user.is_active = True
    user.is_superuser = True
    user.is_staff = True
    user.save()
    
    print(f"Admin user {'created' if created else 'updated'} with superuser status")
else:
    print("ERROR: No organization found!")
EOF

# Collect static files if needed
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear 2>/dev/null || true

echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000
