# Medisoft

A medical practice management application with a Django backend and React frontend.

## Quick Start

### Docker (Recommended for full stack)

```bash
docker-compose up --build
```

Services:
- **Frontend**: `http://localhost:3000` (Nginx, production build)
- **Backend API**: `http://localhost:8000` (Django)
- **Database**: PostgreSQL 15 on port 5432
- **pgAdmin**: `http://localhost:8081`

Default credentials: `admin` / `admin`

### Local Development

```bash
# 1. Start database (PostgreSQL 15 must be running locally)
# 2. Start backend
cd backend
source venv/bin/activate  # or use your preferred venv
python manage.py migrate
python manage.py runserver 0.0.0.0:8000 &

# 3. Start frontend (in a new terminal)
cd frontend
npm install
npm run dev  # runs on http://localhost:5173

# 4. Run e2e tests (requires frontend dev server running)
cd test/e2e
npx playwright test
```

## Architecture

```
┌─────────────┐     /api proxy      ┌──────────────┐     PostgreSQL      ┌─────────────┐
│   Frontend  │ ──────────────────►  │   Backend    │ ◄───────────────── │   Database  │
│   (Vite)    │   http://localhost:  │  (Django)    │     localhost:5432  │  (Postgres) │
│ :5173       │                      │  :8000       │                     │             │
└─────────────┘                      └──────────────┘                     └─────────────┘
```

### Local Dev Routing

- Frontend runs on `http://localhost:5173`
- Vite dev server proxies `/api` requests to `http://localhost:8000` (configured in `frontend/vite.config.ts`)
- Backend listens on `http://localhost:8000`
- Database: `localhost:5432`, user `postgres`, password `secret`, database `medisoft`

### Docker Routing

- Frontend on `http://localhost:3000` (Nginx serves static, proxy passes `/api` to backend)
- Backend on `http://localhost:8000` inside the container
- Database service name: `db` (used as `DB_HOST=db` in `.env.docker`)
- Backend connects to DB via `postgresql://medisoft:medisoft@db:5432/medisoft`

## Environment Files

| File | Purpose |
|---|---|
| `.env.example` | Template — copy to either `.env.local` or `.env.docker` |
| `.env.local` | Local development — `DB_HOST=localhost`, `VITE_API_URL=/api` |
| `.env.docker` | Docker deployment — `DB_HOST=db`, `VITE_BACKEND_URL=http://backend:8000/api` |

### Key Variables

| Variable | Local Dev | Docker | Description |
|---|---|---|---|
| `DB_HOST` | `localhost` | `db` | Database host |
| `VITE_API_URL` | `/api` | `/api` | Frontend API base path |
| `VITE_BACKEND_URL` | `http://localhost:8000/api` | `http://backend:8000/api` | Proxy target |
| `DJANGO_SETTINGS_MODULE` | default | `config.settings_docker` | Django settings module |
| `DJANGO_ADMIN_PASSWORD` | `admin` | `admin` | Default admin password |

## E2E Testing with Playwright

### Running Tests

```bash
cd test/e2e
npx playwright test                    # all tests
npx playwright test frontend.test.ts   # frontend UI tests only
npx playwright test api.test.ts        # backend API tests only
npx playwright test appointments.test.ts  # appointment navigation tests
```

### Test Results

- HTML report: `test/playwright-report/index.html`
- JSON results: `test/test-results/results.json`
- Test artifacts (screenshots, traces): `test/e2e/test-results/`

### Test Credentials

- Username: `admin`
- Password: `admin`

## ⚠️ Rules & Common Pitfalls

### E2E Tests

1. **Frontend dev server must be running before e2e tests**
   - E2E tests navigate to `http://localhost:5173` (the Vite dev server)
   - If the dev server isn't running, tests fail with `net::ERR_CONNECTION_REFUSED`
   - **Fix**: Run `npm run dev` in `frontend/` before running e2e tests, OR add a `webServer` config in `playwright.config.ts` to auto-start it

2. **Playwright config has no `webServer` auto-start**
   - `playwright.config.ts` sets `webServer: null` — tests expect the server to be pre-started
   - In CI mode (`CI=true`), tests get 2 retries and run with 1 worker
   - In local mode, tests run with 4 workers, 0 retries

3. **Test timeouts are 30s per test**
   - Each test has `{ timeout: 30000 }` set
   - Navigation timeouts: 5s for URL assertions, 10s for login flow
   - If tests are slow, increase timeouts rather than reducing them

4. **Use regex selectors for labels and URLs**
   - `getByLabel(/username/i)` — case-insensitive matching
   - `toHaveURL(/\/dashboard$/)` — regex for URL assertions
   - `getByText(/error|invalid|failed/i)` — case-insensitive error detection

### Local Development

5. **Use `.env.local` for local dev, NOT `.env.docker`**
   - `.env.local` sets `DB_HOST=localhost` — Docker uses `DB_HOST=db`
   - `.env.local` sets `VITE_API_URL=/api` — uses Vite proxy for API requests
   - `.env.docker` sets `VITE_BACKEND_URL=http://backend:8000/api` — Docker service name

6. **Vite proxy configuration**
   - `frontend/vite.config.ts` proxies `/api` → `http://localhost:8000`
   - This means frontend API calls go to `/api/...` (relative) and Vite forwards them
   - Do NOT set `VITE_API_URL` to an absolute URL in local dev — it breaks the proxy

7. **Backend must be running before frontend can make API calls**
   - The Vite proxy forwards `/api` to the Django backend
   - If backend is down, API calls fail even if frontend loads

### Docker

8. **Docker uses different settings module**
   - Backend uses `DJANGO_SETTINGS_MODULE=config.settings_docker` in Docker
   - Local dev uses the default settings

9. **Docker services depend on health checks**
   - Frontend waits for backend health check (`/health/`)
   - Backend waits for database health check (`pg_isready`)
   - Test runner waits for both frontend and backend

10. **Database credentials differ between environments**
    - Local: user `postgres`, password `secret`
    - Docker: user `medisoft`, password `medisoft`

### Frontend Pages

11. **Available routes**
    - `/login` — Login page
    - `/dashboard` — Dashboard (requires auth)
    - `/appointments` — Appointments page (requires auth)
    - `/patients` — Patients page (requires auth)
    - `/medical-records` — Medical Records page (requires auth)
    - `/admin/users` — User Management (requires auth)

12. **Navigation pattern**
    - Top bar links use `exact: true` for disambiguation (e.g., `'Appointments'` vs `'Today Appointments'`)
    - Logout button uses `getByRole('button', { name: 'Logout' })`

### API

13. **Auth is JWT-based**
    - Login returns a token stored for subsequent API requests
    - API tests use `Authorization: Bearer <token>` header
    - Unauthenticated requests to `/api/users/` return 401

14. **Health check endpoint**
    - `GET /health/` returns `{ "status": "healthy", "service": "medisoft-backend" }`

## Project Structure

```
medisoft/
├── backend/                 # Django backend
│   ├── apps/               # Django apps
│   ├── config/             # Django settings
│   └── manage.py
├── frontend/               # React + Vite frontend
│   ├── src/pages/          # Page components
│   ├── vite.config.ts      # Vite proxy config
│   └── Dockerfile
├── test/
│   └── e2e/               # Playwright e2e tests
│       ├── playwright.config.ts
│       └── tests/         # Test files
├── docker-compose.yml
├── .env.local             # Local dev env
└── .env.docker            # Docker env
```

## License

See [LICENSE](LICENSE)
