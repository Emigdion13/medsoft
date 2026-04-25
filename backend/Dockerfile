FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies and postgres client for health check
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.12-slim

WORKDIR /app

# Install curl and postgres client for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Copy installed dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Patch Django's _check_indexes to handle both Index and UniqueConstraint
RUN sed -i 's/for field, _ in index\.fields_orders/for field in getattr(index, "fields", getattr(index, "fields_orders", []))/' /usr/local/lib/python3.12/site-packages/django/db/models/base.py

# Copy application code
COPY . .

# Generate Django migrations if none exist (needed for fresh database setup)
RUN MIGRATION_FILES=$(find /app -path "*/migrations/migrations/*.py" ! -name "__init__.py" 2>/dev/null | head -5); \
    if [ -z "$MIGRATION_FILES" ]; then \
        echo "No migration files found. Generating initial migrations..."; \
        python manage.py makemigrations --noinput || true; \
    else \
        echo "Migration files already exist, skipping generation."; \
    fi

# Expose port
EXPOSE 8000

# Startup script - copy and set executable before switching to non-root user
COPY docker/startup.sh /startup.sh
RUN chmod +x /startup.sh

USER appuser

ENTRYPOINT ["/startup.sh"]
