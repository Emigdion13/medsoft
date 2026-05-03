# Medisoft - Project Overview

## Important: Before Fixing Anything

**If you are going to fix anything, please read [HowItWasFixed.md](./HowItWasFixed.md) first.**

This file contains critical historical fixes that will save you time and prevent reintroducing old bugs.

---

## Architecture & Design

### High-Level Structure

```
Medisoft
├── backend/          # Django REST Framework API (Python 3.12)
├── frontend/         # React + Vite SPA
└── test/e2e/         # Playwright end-to-end tests
```

### Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2.15 + Django REST Framework |
| Frontend | React 18 + Vite + TypeScript |
| Database | PostgreSQL 15 (Alpine) |
| Auth | JWT (access token: 60min, refresh token: 7 days) |
| Testing | Playwright |

### Language

**Spanish (es-do)** - All UI text, labels, validation messages, and documentation are in Spanish.

---

## Backend Design

### Project Structure
```
backend/
├── config/
│   ├── __init__.py
│   ├── settings.py       # Base settings (local dev)
│   ├── settings_docker.py # Docker-specific settings
│   └── urls.py
├── apps/
│   └── core/
│       ├── organizations/
│       ├── users/
│       ├── roles/
│       ├── permissions_app/
│       ├── user_roles/
│       ├── role_permissions/
│       ├── audit/
│       └── access_logs/
├── apps/ (feature modules)
│   ├── patients/
│   ├── doctors/
│   ├── appointments/
│   ├── encounters/
│   └── clinical/
└── manage.py
```

### Key Backend Concepts

1. **ALLOWED_HOSTS**: Critical for Docker networking
   - Local: `localhost,127.0.0.1`
   - Docker: Add container names (e.g., `medisoft-frontend`)
   - See `HowItWasFixed.md` for history of this issue

2. **JWT Authentication**
   - Access tokens expire in 60 minutes
   - Refresh tokens expire in 7 days
   - Tokens stored in frontend memory (not localStorage)

3. **CORS Configuration**
   - Only allows `http://localhost:5173` and `http://127.0.0.1:5173`
   - Credentials allowed

4. **Database Models**
   - Custom User model via `AUTH_USER_MODEL = 'core_users.User'`
   - Organizations → Users → Roles → Permissions hierarchy

---

## Frontend Design

### Project Structure
```
frontend/
├── src/
│   ├── pages/          # Page components (one file per route)
│   ├── types/         # TypeScript type definitions
│   └── utils/         # Helper functions
├── vite.config.ts     # Vite config with API proxy
└── package.json
```

### Key Frontend Concepts

1. **API Proxy**: `/api` routes are proxied to `http://localhost:8000`
2. **Routing**: Simple file-based routing via pages directory
3. **State Management**: Component-level state (useState) - no Redux/Zustand
4. **Styling**: Inline styles with Tailwind-like patterns

---

## Environment Variables

### Local Development (`.env.local`)
```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=medisoft
DB_USER=postgres
DB_PASSWORD=secret

# Frontend
VITE_API_URL=/api  # Uses Vite proxy, NOT absolute URL
```

### Docker Deployment (`.env.docker`)
```bash
# Database
DB_HOST=db  # Docker service name
DB_PORT=5432
DB_NAME=medisoft
DB_USER=medisoft
DB_PASSWORD=medisoft

# Backend
DJANGO_SECRET_KEY=your-secret-key
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,backend,medisoft-frontend
DJANGO_SETTINGS_MODULE=config.settings_docker

# Frontend
VITE_BACKEND_URL=http://backend:8000/api  # Docker service URL
```

---

## Common Operations

### Starting Development
```bash
# Backend (Python 3.12 required)
cd backend && source venv/bin/activate && python manage.py runserver

# Frontend
cd frontend && npm run dev
```

### Running Tests
```bash
cd test/e2e && npx playwright test
```

### Docker Commands
```bash
# Start all services
docker compose up --build

# View logs
docker compose logs -f

# Run migrations
docker compose exec backend python manage.py migrate

# Create superuser
docker compose exec backend python manage.py createsuperuser
```

---

## Routes & Endpoints

### Frontend Routes
| Route | Page |
|-------|------|
| `/login` | Login page |
| `/dashboard` | Dashboard (requires auth) |
| `/appointments` | Appointments (requires auth) |
| `/patients` | Patients (requires auth) |
| `/medical-records` | Medical Records (requires auth) |
| `/admin/users` | User Management (requires auth) |

### Key Backend Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login/` | Login, returns JWT tokens |
| GET | `/health/` | Health check |
| GET | `/api/users/` | List users (requires auth) |

---

## Critical Pitfalls to Avoid

1. **Docker Host Headers**: Adding new services? Update `DJANGO_ALLOWED_HOSTS` - see `HowItWasFixed.md`

2. **Vite Proxy in Local Dev**: Use relative `/api` paths, NOT absolute URLs

3. **Python Version**: Must use Python 3.12 (see `backend/.python-version`)

4. **Environment Files**: `.env.local` for local dev, `.env.docker` for Docker - they have different values

5. **Language**: Everything must be in Spanish - no English text in UI

6. **JWT Token Storage**: Tokens stored in memory only - never localStorage

7. **Test Requirements**: Frontend dev server MUST be running before e2e tests

---

## Database Schema (Key Tables)

```
core_users.User
├── username, email, password
├── first_name, last_name
└── roles (many-to-many through user_roles)

core_organizations.Organization
├── name, code, address
└── users (via user_roles)

core_roles.Role
├── name
└── permissions (many-to-many through role_permissions)

apps_patients.Patient
apps_doctors.Doctor
apps_appointments.Appointment
apps_encounters.Encounter
apps_clinical.ClinicalData
```

---

## Adding New Features

1. **Backend**: Create new Django app under `apps/`
2. **Frontend**: Add page component to `frontend/src/pages/`
3. **Routes**: Update `config/urls.py` and frontend router
4. **Migrations**: Run `python manage.py makemigrations && python manage.py migrate`

---

See individual app READMEs for detailed documentation.
