# Medisoft Docker Deployment Guide

## Quick Start

```bash
# 1. Copy environment files
cp .env.example .env.local        # For local development
cp .env.docker.example .env.docker  # For Docker deployment

# 2. Start all services
docker compose up --build

# 3. View logs in another terminal
docker compose ps
docker compose logs backend -f
docker compose logs db -f
docker compose logs frontend -f
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| `db` | 5432 | PostgreSQL 15 database |
| `backend` | 8000 | Django API server |
| `frontend` | 5173 (dev) / 80 (prod) | Vite + React app |
| `pgadmin` | 8081 | Database administration UI |

## First-Run Setup

### 1. Check Container Status
```bash
docker compose ps
```

All services should show as "healthy" after startup.

### 2. Verify Migrations
```bash
docker compose exec backend python manage.py showmigrations
```

### 3. Create Superuser (Optional)
```bash
docker compose exec backend python manage.py createsuperuser
```

### 4. Access pgAdmin (Database Inspection)
Open: http://localhost:8081

Credentials:
- Email: `admin@medisoft.local`
- Password: `admin`

Add server connection:
- Host: `db`
- Port: `5432`
- Username: `postgres`
- Password: `secret`
- Database: `medisoft`

## API Smoke Test

Test authentication endpoints:

```bash
# Login (returns tokens)
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# Register new user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username":"testuser",
    "email":"test@medisoft.local",
    "first_name":"Test",
    "last_name":"User",
    "password":"testpass123",
    "confirm_password":"testpass123"
  }'

# Health check
curl http://localhost:8000/health/

# Users list (with auth token)
TOKEN="your_token_here"
curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Bearer $TOKEN"
```

## Frontend Testing

```bash
# Start frontend only (requires backend running)
docker compose up frontend

# Access at http://localhost:5173
```

## Common Commands

```bash
# View logs (follow mode)
docker compose logs -f

# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v

# Restart a specific service
docker compose restart backend

# Run management commands
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
```

## Environment Variables Reference

### Database (Docker)
- `DB_HOST=db` (service name, not localhost)
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`

### Backend
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=false`
- `DJANGO_ALLOWED_HOSTS=localhost,backend`

### Frontend
- `VITE_API_URL=http://backend:8000/api`

## Troubleshooting

### Database connection errors
```bash
# Check if db is healthy
docker compose ps db
docker compose logs db

# Ensure DB_HOST is set to 'db' in .env.docker
```

### Port conflicts
Edit `docker-compose.yml` and change:
- `BACKEND_PORT:8000`
- `FRONTEND_PORT:5173`
- `PGADMIN_PORT:8081`

### Container won't start
```bash
# Check for errors
docker compose logs backend
docker compose logs frontend

# Rebuild containers
docker compose up --build
```

## Production Notes

For production deployment:

1. Use a strong `DJANGO_SECRET_KEY`
2. Set `DJANGO_DEBUG=false`
3. Configure proper CORS origins
4. Use HTTPS/SSL termination
5. Enable database backups
6. Set up monitoring/logging

See: https://docs.djangoproject.com/en/stable/howto/deployment/
