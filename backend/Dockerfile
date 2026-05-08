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

# Install pytest for testing (as root before switching to appuser)
RUN pip install --no-cache-dir pytest-django==4.9.0

# Expose port
EXPOSE 8000

# Startup script - copy, convert line endings, and set executable before switching to non-root user
COPY startup.sh /startup.sh.tmp
RUN sed -i 's/\r$//' /startup.sh.tmp && \
    sed -i '1s|^#!.*|#!/bin/sh|' /startup.sh.tmp && \
    mv /startup.sh.tmp /startup.sh && \
    chmod +x /startup.sh

USER appuser

ENTRYPOINT ["/startup.sh"]
