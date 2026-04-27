# Login Endpoint 400 Bad Request Fix - April 26, 2026

## Problem Description

The login endpoint (`POST /api/auth/login/`) returned HTTP 400 Bad Request with minimal response:
```html
<!doctype html>
<html lang="en">
<head><title>Bad Request (400)</title></head>
<body><h1>Bad Request (400)</h1><p></p></body>
</html>
```

This prevented any authentication through the frontend proxy.

## Root Cause Analysis

Django's `ALLOWED_HOSTS` security setting was rejecting requests because:

1. Nginx forwarded requests with `Host: medisoft-frontend` header
2. Django's `ALLOWED_HOSTS` only contained `localhost,127.0.0.1`
3. The container name `medisoft-frontend` wasn't in the allowed list

Django's `CommonMiddleware` checks the `Host` header against `ALLOWED_HOSTS` and returns 400 if it doesn't match.

## Solution

### Changes Made

#### 1. Backend Configuration Files (3 files updated)

**backend/config/settings.py**
```python
# Before
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# After
ALLOWED_HOSTS = os.environ.get(
    'DJANGO_ALLOWED_HOSTS',
    'localhost,127.0.0.1,medisoft-frontend'
).split(',')
```

**backend/config/settings_docker.py**
```python
# Same change as above
```

**backend/config/__init__.py**
```python
# Same change as above
```

#### 2. Docker Compose Configuration

**docker-compose.yml**
```yaml
services:
  backend:
    environment:
      # Changed from ALLOWED_HOSTS to DJANGO_ALLOWED_HOSTS for consistency
      - DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,backend,medisoft-frontend
```

## How It Was Tested

```bash
# Verify settings in running container
docker exec medisoft-backend python manage.py shell \
  -c "from django.conf import settings; print('ALLOWED_HOSTS:', settings.ALLOWED_HOSTS)"

# Expected output: ['localhost', '127.0.0.1', 'backend', 'medisoft-frontend']

# Test login endpoint from Docker network
docker run --rm --network medisoft_medisoft-network \
  mcr.microsoft.com/playwright:v1.59.1-jammy sh -c '
  curl -s http://medisoft-frontend:80/api/auth/login/ \
    -X POST \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"admin\",\"password\":\"admin\"}"
'

# Expected output: JSON with access and refresh tokens
```

## How to Apply This Fix in the Future

### Scenario 1: Adding New Container Names

When adding a new service or renaming containers:

1. Update `docker-compose.yml` → `DJANGO_ALLOWED_HOSTS`
2. Include all container names that will proxy requests to backend:
   - Service name (e.g., `medisoft-frontend`)
   - Backend container name (e.g., `backend`)
   - Any reverse proxy hostnames

### Scenario 2: Development vs Production

**Development/Docker:**
```yaml
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,backend,medisoft-frontend
```

**Production (with custom domain):**
```yaml
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com,www.yourdomain.com
```

### Scenario 3: Debugging 400 Errors

If you see "Bad Request (400)" without body:

```bash
# Check if Host header matches ALLOWED_HOSTS
docker exec medisoft-backend python manage.py shell \
  -c "from django.conf import settings; print(settings.ALLOWED_HOSTS)"

# Test with verbose curl to see Host header
docker run --rm --network medisoft_medisoft-network \
  mcr.microsoft.com/playwright:v1.59.1-jammy sh -c '
  curl -v http://medisoft-frontend:80/api/...'
```

## Files Modified

| File | Change |
|------|--------|
| `backend/config/settings.py` | Added `medisoft-frontend` to default ALLOWED_HOSTS |
| `backend/config/settings_docker.py` | Added `medisoft-frontend` to default ALLOWED_HOSTS |
| `backend/config/__init__.py` | Added `medisoft-frontend` to default ALLOWED_HOSTS |
| `docker-compose.yml` | Changed env var to `DJANGO_ALLOWED_HOSTS` with all needed values |

## Key Takeaways

1. **Docker network services use container names as Host headers** - Django needs these in ALLOWED_HOSTS
2. **Environment variable overrides file defaults** - Check `env | grep DJANGO` when debugging
3. **Always test endpoints from within Docker network** - Local curl behaves differently than container-to-container
4. **Document hostnames needed** - Save this file for future reference when network changes
