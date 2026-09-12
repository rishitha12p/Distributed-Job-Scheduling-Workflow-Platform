# Distributed Job Scheduling & Workflow Platform

A production-style backend demonstrating scheduling, background execution, retries, persistence, authentication, and distributed workers.

## Features

- FastAPI REST API and automatic Swagger docs
- JWT authentication and user-owned jobs
- PostgreSQL persistence through SQLAlchemy
- Redis broker/backend
- Celery workers for asynchronous execution
- APScheduler for due-job dispatching
- One-time jobs, priorities, retries, timeouts, cancellation, and execution history model
- Docker Compose development environment
- Pytest smoke tests

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

Open http://localhost:8000/docs.

## Local development

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload
```

For local development without PostgreSQL or Redis, the default SQLite database supports health checks and API startup. Set `DATABASE_URL` and `REDIS_URL` for full distributed execution.

## API flow

1. `POST /auth/register`
2. Authorize with the returned bearer token in `/docs`.
3. `POST /jobs` with `{ "name": "backup", "payload": {"message": "backup complete"} }`.
4. Run a Celery worker and Redis to process queued jobs.

## Architecture

```text
Client -> FastAPI -> PostgreSQL
                  -> Redis -> Celery Worker -> Execution Log
                  -> APScheduler -> Redis -> Celery Worker
```

## Engineering notes

This repository is an interview-ready foundation. For a larger production deployment, add Alembic migrations, distributed locks, a dedicated workflow DAG model, structured log storage, metrics/tracing, and a separate admin service.
