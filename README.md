# Task Scheduler

A fullstack task scheduling web application where users can create scheduled tasks, monitor their execution status in real time, and have tasks automatically executed by a background worker with retry logic.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | Python 3.13, Django 5.x, Django REST Framework 3.16 |
| Authentication | JWT via SimpleJWT |
| Task Queue | Celery 5.x + Celery Beat |
| Database | PostgreSQL 16 |
| Cache / Broker | Redis 7 |
| Frontend | React 19, Vite 7, Axios |
| Reverse Proxy | Nginx |
| Containerisation | Docker + Docker Compose |
| Tests | pytest, pytest-django, pytest-cov |

---

## Architecture Overview
```
Browser (React SPA)
      │
      ▼
   Nginx :80
   ├── /api/*  ──────────► Django + DRF :8000
   │                          │
   │                     PostgreSQL :5432
   │                          │
   │                       Redis :6379
   │                          │
   │                    Celery Worker
   │                    Celery Beat (scheduler)
   │
   └── /*  ─────────────► Vite Dev Server :5173
```

**Request flow for task scheduling:**
1. User creates a task via `POST /api/tasks/`
2. Django saves it with `status: PENDING`
3. Celery Beat polls every 60 seconds for due tasks
4. Beat dispatches `execute_task` to the worker queue via Redis
5. Worker picks up the job, runs the task logic, updates status
6. On failure, exponential backoff retry (60s → 120s → 240s)
7. After max retries, task is marked `FAILED`
8. React frontend polls `GET /api/tasks/` every 10 seconds and reflects live status

---

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Docker Desktop | Latest | Required — everything runs in containers |
| Git | Any | For cloning |
| Make | Optional | For shorthand commands |

No local Python or Node.js installation required.

---

## Setup and Installation

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/task-scheduler.git
cd task-scheduler
```

### 2. Configure Environment Variables
```bash
cp backend/.env.example backend/.env
cp backend/.env .env
```

Open `backend/.env` and update the values:
```env
# Django
DJANGO_SECRET_KEY=replace-with-a-long-random-string
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database
POSTGRES_DB=taskscheduler
POSTGRES_USER=taskuser
POSTGRES_PASSWORD=taskpassword
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# JWT
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
```

> **Security note:** Never commit `.env` to version control.
> Generate a strong secret key with:
> ```bash
> python -c "import secrets; print(secrets.token_urlsafe(50))"
> ```

### 3. Start All Services
```bash
docker compose up -d
```

Or with Make:
```bash
make up
```

This starts 6 containers: `db`, `redis`, `backend`, `worker`, `beat`, `frontend`, `nginx`.

### 4. Verify All Services Are Running
```bash
docker compose ps
```

Expected output — all services should show `running` or `healthy`:
```
NAME                          STATUS
task-scheduler-db-1           running (healthy)
task-scheduler-redis-1        running (healthy)
task-scheduler-backend-1      running (healthy)
task-scheduler-worker-1       running
task-scheduler-beat-1         running
task-scheduler-frontend-1     running
task-scheduler-nginx-1        running
```

### 5. Open the Application

| URL | Description |
|---|---|
| `http://localhost` | React frontend |
| `http://localhost:8000/api/` | Django REST API |
| `http://localhost:8000/admin/` | Django admin panel |
| `http://localhost:8000/api/health/` | Health check endpoint |

### 6. Create an Admin User (Optional)
```bash
docker compose run --rm backend python manage.py createsuperuser
```

Then log in at `http://localhost:8000/admin/`

---

## Running Tests

### Run the Full Test Suite
```bash
docker compose run --rm backend pytest
```

Or:
```bash
make test
```

### Run a Specific Test File
```bash
docker compose run --rm backend pytest authentication/tests/test_views.py -v
docker compose run --rm backend pytest tasks/tests/test_services.py -v
docker compose run --rm backend pytest tasks/tests/test_tasks.py -v
```

### Run With Coverage Report
```bash
docker compose run --rm backend pytest --cov=. --cov-report=term-missing
```

Or:
```bash
make coverage
```

### Test Coverage by Module

| Module | Tests |
|---|---|
| `authentication` | Registration, login, logout, profile |
| `tasks` (views) | CRUD, complete, cancel, filter by status |
| `tasks` (services) | Business logic, validation, error cases |
| `tasks` (worker) | Celery execution, retry logic, dispatch |
| `core` | Health check endpoint |

---

## API Reference

### Authentication

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/register/` | No | Create account |
| POST | `/api/auth/login/` | No | Get JWT tokens |
| POST | `/api/auth/refresh/` | No | Refresh access token |
| POST | `/api/auth/logout/` | No | Blacklist refresh token |
| GET | `/api/auth/me/` | Yes | Get current user |

### Tasks

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/tasks/` | Yes | List tasks (filterable) |
| POST | `/api/tasks/` | Yes | Create scheduled task |
| GET | `/api/tasks/{id}/` | Yes | Get single task |
| PATCH | `/api/tasks/{id}/` | Yes | Update task |
| DELETE | `/api/tasks/{id}/` | Yes | Delete task |
| POST | `/api/tasks/{id}/complete/` | Yes | Mark as completed |
| POST | `/api/tasks/{id}/cancel/` | Yes | Cancel task |

### Other

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/health/` | No | Service health check |

### Example: Create a Task
```bash
# 1. Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "yourpassword"}'

# 2. Use the returned access token
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "title": "Send weekly report",
    "description": "Email the team summary",
    "scheduled_at": "2026-06-01T09:00:00Z",
    "priority": "HIGH",
    "max_retries": 3
  }'
```

### Filtering Tasks
```bash
# Filter by status
GET /api/tasks/?status=PENDING

# Filter by priority
GET /api/tasks/?priority=HIGH

# Search by title
GET /api/tasks/?search=report

# Combine filters
GET /api/tasks/?status=FAILED&priority=CRITICAL
```

---

## Implementation Notes

### Why a Custom User Model Before First Migration
Django's documentation explicitly recommends creating a custom `AUTH_USER_MODEL` at project start. Changing it after migrations exist requires wiping the database. Our `authentication.User` extends `AbstractUser` with a unique email field used as the login identifier.

### Why Services and Selectors Pattern
Views are kept intentionally thin — they only handle HTTP concerns (parse request, return response). All business logic lives in `services.py` and all database reads live in `selectors.py`. This makes logic reusable, independently testable, and prevents fat views.

### Why Celery Beat + Polling Instead of ETA-Based Scheduling
Using `apply_async(eta=scheduled_at)` stores the entire task in Redis until execution time. For thousands of tasks this creates memory pressure and makes tasks invisible to the scheduler if Redis restarts. Our approach stores tasks in PostgreSQL (durable) and Beat polls every 60 seconds — tasks are only in Redis for their brief execution window.

### Why Exponential Backoff for Retries
Retry 1: 60s, Retry 2: 120s, Retry 3: 240s. This prevents a failed downstream service from being hammered with immediate retries. Each retry doubles the wait time, giving dependent services time to recover.

### JWT Token Strategy
Access tokens live 60 minutes (in memory via React state + localStorage). Refresh tokens live 7 days and are blacklisted on logout via `rest_framework_simplejwt.token_blacklist`. The Axios interceptor automatically refreshes the access token on 401 responses, making token expiry invisible to the user.

---

## Potential Improvements

Given more time, the following improvements would be prioritised:

### Scalability
- Replace polling with WebSocket connections (Django Channels) for instant status updates
- Add Redis Cluster support for high-availability broker setup
- Implement task queues by priority (separate Celery queues for CRITICAL vs LOW)
- Add horizontal worker scaling via Docker Swarm or Kubernetes

### Performance
- Add database read replicas for the task list query
- Cache frequently-read data (user task counts) in Redis
- Add database connection pooling via PgBouncer
- Implement cursor-based pagination for large task lists

### Security
- Move JWT tokens to httpOnly cookies to prevent XSS token theft
- Add per-user rate limiting (currently global throttling only)
- Implement HTTPS with Let's Encrypt in production Nginx config
- Add request signing for internal service-to-service calls
- Conduct a dependency audit with `pip-audit` and `npm audit`

### Observability
- Integrate Prometheus metrics endpoint (`/metrics`) + Grafana dashboard
- Add structured JSON logging with correlation IDs per request
- Set up Sentry for error tracking and performance monitoring
- Add Celery Flower for real-time worker monitoring UI

### Developer Experience
- Add CI/CD pipeline with GitHub Actions (lint → test → build → deploy)
- Add pre-commit hooks (Black, isort, ESLint) for consistent code style
- Add API documentation with drf-spectacular (OpenAPI/Swagger)
- Containerise test runs in CI with the same Docker setup used locally

---

## Learnings

This project involved several concepts encountered and implemented for the first time or deepened significantly:

**Django architecture patterns** — the services/selectors separation was new. Keeping views as pure HTTP handlers and pushing all logic into dedicated service functions makes the codebase dramatically easier to test and reason about.

**Celery's execution model** — understanding the difference between the broker (Redis — transient job queue) and the result backend (PostgreSQL — durable results) clarified why each component exists. Celery Beat as a separate process that only dispatches — never executes — was an important architectural insight.

**JWT authentication flow** — implementing the full token lifecycle (issue, refresh, blacklist on logout) gave a clear picture of stateless authentication. The discovery that `AUTH_USER_MODEL` must be set before the first migration was a hard-learned lesson.

**Docker networking** — service names like `db` and `redis` as hostnames only resolve inside the Docker network. This caused early confusion when running `manage.py` locally and encountering "host not found" errors — now fully understood.

**Optimistic UI updates** — updating local React state immediately before the API call resolves makes the UI feel instant. The pattern of reverting on API failure by re-fetching server state is simple and robust.

---

## Project Structure
```
task-scheduler/
├── backend/                    # Django application
│   ├── authentication/         # Custom user model + JWT auth
│   ├── tasks/                  # Task models, API, services
│   ├── core/                   # Shared BaseModel, exceptions, pagination
│   ├── workers/                # Celery app, tasks, Beat schedule
│   ├── config/                 # Django settings (base/dev/prod)
│   ├── requirements/           # Pinned Python dependencies
│   └── manage.py
├── frontend/                   # React application
│   └── src/
│       ├── api/                # Axios instance + interceptors
│       ├── components/         # Reusable UI components
│       ├── contexts/           # Auth context (global state)
│       ├── hooks/              # useTasks (fetching + polling)
│       └── pages/              # Login, Register, Dashboard
├── docker/                     # Dockerfiles + Nginx config
│   ├── backend/Dockerfile
│   ├── frontend/Dockerfile
│   └── nginx/nginx.conf
├── docker-compose.yml          # Full stack orchestration
├── Makefile                    # Developer shorthand commands
├── .env.example                # Environment variable template
├── .gitignore
└── README.md
```

---

## Quick Reference
```bash
# Start everything
make up

# View logs
make logs

# Run tests
make test

# Open Django shell
make shell

# Stop everything
make down

# Wipe database and restart fresh
make down-v && make up
```

---

## License

MIT