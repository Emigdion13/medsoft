#!/bin/bash

set -e

echo "Starting Medisoft backend..."

# Parse DATABASE_URL if set (format: postgresql://user:pass@host:port/db)
if [ -n "$DATABASE_URL" ]; then
    # Extract host:port part after @ and before /
    db_host_port=$(echo $DATABASE_URL | sed -E 's|^[^/]+://[^@]+@([^/]+)/.*$|\1|')
    export DB_HOST=$(echo $db_host_port | cut -d: -f1)
    export DB_PORT=$(echo $db_host_port | cut -d: -f2 | grep -o '[0-9]*' || echo "5432")
    
    # Extract user from beginning
    export DB_USER=$(echo $DATABASE_URL | sed -E 's|^[^/]+://([^:]+):[^@]+@.*$|\1|')
fi

# Wait for database to be ready
echo "Waiting for PostgreSQL..."
while ! pg_isready -h ${DB_HOST:-localhost} -p ${DB_PORT:-5432} -U ${DB_USER:-postgres}; do
    sleep 1
done
echo "PostgreSQL is ready!"

# Apply migrations (use --fake-initial if database is empty)
echo "Running migrations..."
python manage.py migrate --noinput --fake-initial || python manage.py migrate --noinput

# Create default organization and admin user via Python script (CRLF-safe)
echo "Initializing database defaults..."
python init_db.py

# Collect static files if needed
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear 2>/dev/null || true

echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000
