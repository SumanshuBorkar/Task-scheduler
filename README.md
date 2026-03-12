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

### Class Diagram :

<p align="center">
  <img src="https://uml.planttext.com/plantuml/svg/VLJ9Rjim4BqRy3yGxiLkuI2zwb34bULOW2mPMf2Zm51JXR146YILfKN_lLois7AKGWSDtvjzXhoJ2WlLjSrq8W-K7R70BI8DbdAbbA2FdOAGS9RHtu1kBtKUCJdKWdUiydd31VgoMPblEfbEh3ag90ZqPpf1w1kjF5GKuTeUEeqpt8A7CXs0rHQ45jDcW1orZnSkgXv4yoSidw1QE8-on4JHP-tb9-SDO6PX8W0hg4giFBJMKavRi4J3QyhcYrxcdJA7l-TiSomFOzaggffXgXL88kXHKSu6k6wawgHdFMLMTdK8oWLLRuxOdqxEWkXwkcOiNtW5qerMGdXxR62K4g34MqdqJ3GJCWKr24kq-BKq90Kv90Wqe4sKpgoarQ2SJrlP7QjneY_drEOMYuFV9tk1RVIatm62MMgodYyk1darbi3sGhTxR3vsVSUo-KKPDVloaT73rqtKGtrtd3Z4TLu8BieMfCJrrU0xWOrssLvrKQ_f0SIWWLSbHBmUItuiIWFFe6-2jeYCz9zPs1Z0klPYvLoKVH2lm_ZUY9c_3TP55DY0QH779znFTlieo1s-MOKd3NyL-q5a3qFt_UAw057oO7vnakvMaP6suVtMsgTX7le6EvjVjzcvo0hV3xAi3r-aWH7pS1SaHNvftdV2cONn9Z7_XrNQbnAaQPAUBEoZC_i-GyibHxFRcvklCtUrFSHVcBwHzZ2YS5uo3-c7vdD5CqeFwJUarrakVmpk_00yt_TX4CD_NB_Uls7F2t07hB8Fz3y0" alt="Logo" width="100%"/>
</p

### ER Diagram :

<p align="center">
  <img src="https://uml.planttext.com/plantuml/svg/fPHVIyCm5CNV2_qEORveOQ3YG4J6gbOTEYUp4_6bnFQwXQLDoH-dEB-xIRDXPbTHf4_jxzxqt7DksnCISwbowdjYHeeISvoZ9vpE9fof8Zjbb76qTHwQo_Ty3mf9v1jgAG5SjD2xxo4K89AX8pGUzy_GyV7jLRThdhRRbfdA0kUWA-x3qUbbEDhUw-pkM0Wv9jGX-vs39Icn47F6CxTj_t09YKXmAicBEVHaEBoEmXiBKWvOGfPWgKdS7qHtSJYuZHyDHKYLMGFzS6UJMCn-FrlY5fml2mAaZwAmDbbdnwh8GAISb9AmmiY87cBRePEGIhWjAvTAJXWtqXmlLaoaKyWKRPmPNY5LpPQaB2yfDF40SP3yBKdrBXZSlucZYsXaKOvV4uC9Y7MaJmKAkiqOQUtvxiBFIGL_IIgn4setVvVPbwXQPjMtq6ZLCoc8c3PAPafgCw6Udyw0SyQJ78J04t0orxkWE3RIaxpceLx-sMgxrkshMq3PvD_3r-K5YC8Bq4rRrvnU9QxwEw35ejrcxzKxpNGjDjSH-PwzTw2Je2cRuirLPaZ39r20TWrCLG-AJF-yFW40" alt="Logo" width="100%"/>
</p

### Sequence Diagram :

<p align="center">
  <img src="https://uml.planttext.com/plantuml/svg/dLLHZnet47v7uZ-CqXUYt8aaKbzM8WsmIqfBWBBGF2B7EmSkNdjhUmleTF-zOtlXW5pKgE9XqVgRcM--yJVxqJfcN5tATilkXAgOOILyPNotCRfMnL1BRU2dKT__BY4M_wvHSUmRe_VBhU0xXTR2-tQhtMBSKT3Aecct2Eq45nLJ3buja8vWDNu5pDBZvdIw4UeGZkP67uutf-bVJ6qqzESncfutWBcsRcCm_sCI0EdWc-A5iE4e_Biv7Q94SuG1CXSm_i_Ba2_QxD04KFphM-xre5-xBIg2CoUqWbwltV8ImFq7QZM1YQRse5FJAyLAl8EAMRlNfdXDkB57XQuJcC_o9NHP9RgCCdQbZ-ksM-7KmwZp14RQx9afmFWnM69AR_rXEaZWJoP5mHm2DrXuHanIj-a0xa_HWPT1JjMRo8RaRr-Mm3Ztatn3W0U3TWjExr3P4qiFosc-sBm7wgh4KfjZT-jSDLFo25phdS16bw51JoRdMongYGKicTrz8yz8I0dEdpneKr9rMtyjXRkiEgkSA8KbXQ6kGeCTkzNx6ELlJJPDnzDFtzVJ0ssNSjDm3PKE3NnFsOxn5IHLT43K-IuC3EthizO1VXQRfBkQmdYQPujb9FT89dErJKuKdwx74GIv6iU7U4SJQEuSgofvN3DxLBo3ZlNiISmrSqGeW9_p-PfhKLpHMStJ_ZABTF9i2JmaNbz36w7VlttNJAs0nn117RAdPfw3ytA0x82yFjzsRvaBwdDD4wLXGb5Zg6ilYNfm0XWIOA11jyXQji7dHD5U2QJ2LipnRSZIRiNNBpLsrdcncav9vxjJ0QzJ0ahldox3J_bZ6v4aUBznsc7IGLu7AxHR03zGSpZxF9zaoooze_jVLXAlozxckBWVQpph-AXhHz587biDXrcUKoHAYp1YGjPaEczBPmHQUfPCAA4s_y7FuuzhJWFpNDwyk-7IJ6k1zxH9Q59xuROaMwLLN1tXOw0V7XeUdzdXp00F76d353yeqAW_dcJf_v321wuM6KsJFZOqhz9kl2ogQ6uasTrVDf8YhfLBzt_AhitVmN-yeNxsFdxH-5UkoRD9DepCQDl_cYqoy0kS70Cz-EK55qlQJr72kA8AYDsZlRNOMvZz7jrbWHd3Za-Nksv1sq1n8PjvwEVLv_EHHpvI-_JL_XS0" alt="Logo" width="100%"/>
</p

### Object Diagram :

<p align="center">
  <img src="https://uml.planttext.com/plantuml/svg/XPDXQzim48Q_-rU8xBCtnHw31JOIadG910PfyzaezZNLB5b6EZS9O_zzTtRSk6j6iS6wHoVT-vwbQK3biR4c2gMkQkML5NkLbmVlcggOE-Ey-70tuoUAtFuNv2X6okWSn4Ji0lYHK45qu7SaX2x4Dp5gWe-b78y8D9HJAGkCspI6O9KsBsGA9sLh0nzpPtbMXqpbg9zv3Ve6eZ_NqXwihWhm3ogKf80_hGAamNYW04FPAq2DfYr_3rKXZW2bEGiFjVF8qzG0R0BDtyzNoyLkirmGhBrsNkEPy6hzOyLf-HCKZO4YKyYR9JBv4iiq7aiXlqwaf9Ttyu3-dENKFCwIHAmwPKmrS96KI0u6A8abPvtQZiHgdyVZ91qD3VFFQEfRTfCtTfDNTXSArLu54DqMhxpUpTPlZCwtwuVrVBPvnspoFxFf3RC38t22V7pniAHnWzfLhPbkvcg6u_xdkGRfLC15ycwxvDFZlVEPXH3KeNKwTrL5DMW_Sc-1rl3Iel6AMMPRBL9-JeWUdI_1N_hU1TCd5p3cUWEvnXrwjHjtQ7Msw2gJmbxbGCiC4MoD8lsKYaSwvL1Cn6rz1fw1By5ok_svvTBTBOhZxvVJF17kM8L_SDBZBc3STzQeW6tGjdQGSF5oW0ge9L0mYAPq6_ZU_mK0" alt="Logo" width="100%"/>
</p

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