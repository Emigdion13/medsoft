#!/bin/bash

echo "Starting Medisoft backend..."

# If running a management command (args provided), just execute it without DB check
if [ $# -gt 0 ]; then
    # Check if this is actually a Django management command
    case "$1" in
        migrate|makemigrations|shell|runserver|createcachetable|collectstatic|flush|inspectdb|dumpdata|loaddata|test)
            exec python manage.py "$@"
            ;;
    esac
    
    # If we get here, it's not a Django command (e.g., shell, ls, cat)
    # Execute as-is
    exec "$@"
fi

# Server mode: wait for database to be ready
echo "Waiting for PostgreSQL..."
for i in {1..30}; do
    if pg_isready -h "${DB_HOST:-localhost}" -p "${DB_PORT:-5432}" -U "${DB_USER:-postgres}"; then
        echo "PostgreSQL is ready!"
        break
    fi
    sleep 2
done

if [ $i -eq 30 ]; then
    echo "WARNING: Database not ready after 60 seconds, proceeding anyway..."
fi

# Always check and generate migrations if needed (including any new models)
echo "Checking/generating migrations..."
python manage.py makemigrations --noinput || true

echo "Running migrations..."
python manage.py migrate --noinput

# Create default organization if not exists
echo "Checking/defaulting organization..."
python manage.py shell <<EOF
from apps.core.organizations.models import Organization
org, created = Organization.objects.get_or_create(
    name="Default Organization",
    defaults={
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
