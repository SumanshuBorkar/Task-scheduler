# ── Task Scheduler — Developer Commands ──────────────────────────

.PHONY: help up down build logs shell test migrate createsuperuser clean

help:
	@echo ""
	@echo "  Task Scheduler — Available Commands"
	@echo "  ──────────────────────────────────"
	@echo "  make up              Start all services"
	@echo "  make down            Stop all services"
	@echo "  make down-v          Stop and wipe database volume"
	@echo "  make build           Rebuild Docker images"
	@echo "  make logs            Tail logs from all services"
	@echo "  make logs-worker     Tail Celery worker logs"
	@echo "  make shell           Open Django shell"
	@echo "  make test            Run test suite"
	@echo "  make coverage        Run tests with coverage report"
	@echo "  make migrate         Run database migrations"
	@echo "  make migrations      Create new migrations"
	@echo "  make superuser       Create Django superuser"
	@echo "  make clean           Remove all containers and volumes"
	@echo ""

up:
	docker compose up -d

down:
	docker compose down

down-v:
	docker compose down -v

build:
	docker compose build

logs:
	docker compose logs -f

logs-worker:
	docker compose logs -f worker

logs-beat:
	docker compose logs -f beat

logs-backend:
	docker compose logs -f backend

shell:
	docker compose run --rm backend python manage.py shell

test:
	docker compose run --rm backend pytest

coverage:
	docker compose run --rm backend pytest --cov=. --cov-report=term-missing --cov-report=html

migrate:
	docker compose run --rm backend python manage.py migrate

migrations:
	docker compose run --rm backend python manage.py makemigrations

superuser:
	docker compose run --rm backend python manage.py createsuperuser

check:
	docker compose run --rm backend python manage.py check

clean:
	docker compose down -v --remove-orphans
	docker system prune -f