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

# Apply migrations (no --fake-initial for fresh databases)
# echo "Running migrations..."
# python manage.py migrate --noinput

# DEBUG: Check migration graph before applying
echo "Checking migration graph..."
python << 'PYEOF'
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_docker')
django.setup()
from django.db.migrations.loader import MigrationLoader
loader = MigrationLoader(None)
print('\n=== Migration Graph Dependencies ===')
for key in sorted(loader.graph.nodes.keys()):
    node = loader.graph.node_map[key]
    if key[0] not in ['contenttypes', 'auth']:
        print(f'{key}: parents={len(node.parents)}, children={len(node.children)}')
PYEOF

# Create fresh migrations if none exist (first run or fresh clone)
MIGRATION_COUNT=$(find /app -path "*/migrations/0*.py" 2>/dev/null | wc -l)
if [ "$MIGRATION_COUNT" -eq 0 ]; then
    echo "No migrations found — generating from current models..."
    python manage.py makemigrations --noinput
fi

# Apply migrations (no --fake-initial for fresh databases)
echo "Running migrations..."
python manage.py migrate --noinput

# Seed the database with initial data (admin user, organization, etc.)
echo "Seeding database..."
python init_db.py

# Collect static files if needed
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear 2>/dev/null || true

echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000
