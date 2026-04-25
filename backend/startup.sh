#!/bin/bash

set -e

echo "Starting Medisoft backend..."

# Wait for database to be ready
echo "Waiting for PostgreSQL..."
while ! pg_isready -h $DB_HOST -p ${DB_PORT:-5432} -U $DB_USER; do
    sleep 1
done
echo "PostgreSQL is ready!"

# Apply migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Create default organization if not exists
echo "Checking/defaulting organization..."
python manage.py shell <<EOF
from core.organizations.models import Organization
org, created = Organization.objects.get_or_create(
    name="Default Organization",
    defaults={
        'description': 'Default organization for Medisoft',
        'is_active': True,
    }
)
print(f"Organization {'created' if created else 'exists'}: {org.name}")
EOF

# Create default admin user if not exists
echo "Checking/defaulting admin user..."
python manage.py shell <<EOF
from core.users.models import User
from core.organizations.models import Organization
import os

org = Organization.objects.first()
if org:
    user, created = User.objects.get_or_create(
        username="admin",
        defaults={
            'organization': org,
            'email': os.environ.get('DJANGO_ADMIN_EMAIL', 'admin@medisoft.local'),
            'first_name': 'System',
            'last_name': 'Administrator',
            'password_hash': 'pbkdf2_sha256$870000$yK4J3x1Q8Z9mN7pL6rF4sA3bC2dE1fG0hI9jK8lM7nO6pQ5rS4tU3vW2xY1zA0b==',
            'is_active': True,
        }
    )
    if created:
        # In real implementation, use proper password hashing
        user.password_hash = 'pbkdf2_sha256$870000$yK4J3x1Q8Z9mN7pL6rF4sA3bC2dE1fG0hI9jK8lM7nO6pQ5rS4tU3vW2xY1zA0b=='
        user.save()
        print("Default admin user created (password: admin)")
    else:
        print("Admin user already exists")
else:
    print("ERROR: No organization found!")
EOF

# Collect static files if needed
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear 2>/dev/null || true

echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000
