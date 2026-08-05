# PharmaCloud ERP — Backend

Enterprise, cloud-native, **multi-tenant SaaS pharmacy ERP** backend.

- **Framework:** Django 5.2 + Django REST Framework
- **Stack:** PostgreSQL 16 · Redis 7 · Celery 5 · JWT · Docker · Gunicorn · Nginx · MinIO/S3 · Pytest
- **Docs:** OpenAPI 3 (drf-spectacular) with Swagger UI and ReDoc

> This is the **backend foundation only**. Business modules (Medicines, Inventory,
> POS, Sales, Accounting, Purchasing, …) are intentionally not part of this codebase yet.
> This layer provides the platform contract they will build on: settings, multi-tenancy,
> auth, audit/soft-delete/UUID bases, repository + service layers, the API envelope,
> exception handling, pagination, health checks, Docker, CI, and tooling.

---

## Table of Contents

- [Requirements](#requirements)
- [Project Structure](#project-structure)
- [Quick Start (local)](#quick-start-local)
- [Quick Start (Docker)](#quick-start-docker)
- [Configuration](#configuration)
- [API Contract](#api-contract)
- [Architecture](#architecture)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Deployment](#deployment)
- [Operational](#operational)

---

## Requirements

- Python 3.10+ (Docker images use 3.12)
- PostgreSQL 16 (or Docker)
- Redis 7 (or Docker)
- Docker + Docker Compose (optional, for the containerized stack)

---

## Project Structure

```
backend/
├── apps/
│   ├── common/            # Shared infrastructure (base models, repo/service layers, API envelope)
│   └── core/              # Platform foundations (User, Tenant, health, auth)
├── config/                # Django project package
│   └── settings/          # base.py / development.py / testing.py / production.py
├── nginx/                 # Production reverse proxy
├── requirements/          # base / development / testing / production
├── scripts/               # wait_for_db.py
├── tests/                 # pytest suite + factories
├── .github/workflows/     # CI pipeline
├── docker-compose.yml     # Development stack
├── docker-compose.prod.yml
├── Dockerfile             # Development image
├── Dockerfile.prod        # Production image (multi-stage)
├── entrypoint.sh
├── Makefile
└── pyproject.toml         # Ruff, Black, isort, Pytest configuration
```

A generated full tree is in `docs/PROJECT_TREE.md`.

---

## Quick Start (local)

```bash
# 1. Create a venv and install dependencies
python -m venv .venv
.venv\Scripts\activate            # Windows
source .venv/bin/activate         # Linux/macOS
pip install -r requirements/development.txt

# 2. Configure environment
cp .env.example .env
#   -> edit DATABASE_URL / REDIS_URL for your local services

# 3. Migrate + create an admin
python manage.py migrate
python manage.py createsuperuser

# 4. Run
python manage.py runserver 0.0.0.0:8000
```

Open:

| URL | Description |
|-----|-------------|
| `http://localhost:8000/api/docs/` | Swagger UI |
| `http://localhost:8000/api/redoc/` | ReDoc |
| `http://localhost:8000/api/schema/` | OpenAPI schema (JSON) |
| `http://localhost:8000/api/v1/health/liveness/` | Liveness probe |
| `http://localhost:8000/api/v1/health/readiness/` | Readiness probe |
| `http://localhost:8000/admin/` | Django admin |

---

## Quick Start (Docker)

```bash
cp .env.example .env

# Development stack: postgres + redis + minio + web + celery-worker + celery-beat
docker compose up --build

# Production stack
cp .env.example .env.production   # then set real secrets
docker compose -f docker-compose.prod.yml up -d --build
```

The entrypoint waits for the database, applies migrations, collects static
files, then starts the server (runserver in dev, Gunicorn in prod).

---

## Configuration

All configuration is environment-driven (django-environ). Copy `.env.example`
to `.env` and adjust. Key variables:

| Variable | Purpose |
|----------|---------|
| `DJANGO_SETTINGS_MODULE` | `config.settings.development` \| `testing` \| `production` |
| `DJANGO_SECRET_KEY` | **Required in production** |
| `DATABASE_URL` | `postgres://user:pass@host:5432/dbname` |
| `REDIS_URL` / `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND` | Redis connections |
| `CORS_ALLOWED_ORIGINS` | Comma-separated frontend origins |
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` / `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | Token lifetimes |
| `USE_S3` | Enable S3/MinIO object storage (production) |

---

## API Contract

### Response envelope

Every JSON API response is wrapped in a stable envelope:

```json
{
  "success": true,
  "status_code": 200,
  "message": "Success",
  "data": {},
  "errors": [],
  "meta": { "request_id": "...", "timestamp": "...", "version": "v1" }
}
```

- Errors are always an array of `{"code", "field", "message", "details"?}`.
- Every response carries the originating `X-Request-ID`.
- **Exemption:** health probes (`/api/v1/health/*`) return raw JSON
  (`X-Envelope: skip`) so orchestrators can parse them directly.

### Authentication (JWT)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/token/` | POST | Obtain `access` + `refresh` tokens |
| `/api/v1/auth/token/refresh/` | POST | Rotate tokens |
| `/api/v1/auth/token/verify/` | POST | Verify a token |
| `/api/v1/auth/me/` | GET | Current authenticated user |

Send tokens as `Authorization: Bearer <access>`.

### Versioning

- URL path versioning: `/api/v1/...`
- `DEFAULT_VERSION = "v1"`, only `v1` allowed.

### Pagination

List endpoints paginate by default (`page`, `page_size`, max 200):

```json
"data": {
  "results": [],
  "count": 0,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "next": null,
  "previous": null
}
```

---

## Architecture

### Multi-tenancy

- `Tenant` (core) identifies each contracted customer.
- `TenantIdentificationMiddleware` resolves `request.tenant` from
  `X-Tenant-ID` / `X-Tenant-Slug` (cached in Redis).
- `TenantAwareModel` (common) is the abstract base for tenant-scoped entities.
- Permissions: `HasTenantContext`, `IsTenantMember` (superusers bypass).
- `BaseService.list()` auto-scopes by `request.tenant` when the model has a
  `tenant` field.

### Base models (common)

| Base | Adds |
|------|------|
| `UUIDBase` | `id = UUID` primary key |
| `TimeStampedBase` | `created_at`, `updated_at` |
| `SoftDeleteBase` | `is_deleted`, `deleted_at`, soft `delete()` / `hard_delete()`, `objects` + `all_objects` |
| `AuditBase` | `created_by`, `updated_by` auto-stamped from request context |
| `FullAuditModel` | All of the above (recommended base) |

### Layering

```
Viewsets  ->  Services  ->  Repositories  ->  ORM
            (business rules,   (persistence,
             transactions)      queries)
```

- `BaseService` wraps every state change in `transaction.atomic`, auto-fills
  `created_by`/`updated_by`, and injects the current tenant on create.
- `BaseRepository` is a typed data-access layer (CRUD, bulk, locking).
- Domain errors raise `apps.common.exceptions.PharmaCloudError` subclasses,
  translated to proper HTTP codes by the API exception handler.

### Observability

- Correlation: `request_id` propagates into every log line and response header.
- Logging: console (dev) / structured JSON (prod) with request context filter.
- Health: liveness + readiness (database, cache, Celery).

---

## Testing

```bash
make test            # pytest
make test-cov        # pytest with coverage
```

- Settings: `config.settings.testing` (SQLite in-memory by default).
- CI runs against PostgreSQL 16 (set `DATABASE_URL`).
- Factories in `tests/factories.py`; fixtures in `tests/conftest.py`.

---

## Code Quality

```bash
make lint            # ruff check .
make format          # ruff format + black + isort
make format-check    # verify formatting in CI
pre-commit install   # install git hooks
```

Configured in `pyproject.toml` (line length 119). CI enforces lint + format +
`pip-audit` security scan.

---

## Deployment

### Production image

`Dockerfile.prod` is multi-stage: build deps, then a minimal runtime running
Gunicorn (`gthread`, 4 workers × 4 threads) as a non-root user.

### Nginx

`nginx/nginx.conf` serves `/static/` + `/media/` directly, proxies `/api/`,
`/admin/`, and health probes, and redirects HTTP→HTTPS.

### Security posture (production settings)

- `DEBUG=False`, secure cookies, HSTS, `X-Frame-Options: DENY`, strict CSP
  headers, `SECURE_PROXY_SSL_HEADER` behind a TLS-terminating proxy.
- Optional Sentry error tracking (`SENTRY_DSN`).
- Optional S3/MinIO object storage (`USE_S3=True`).
- JWT access + rotating refresh tokens (blacklist enabled).

---

## Operational

### Django management

```bash
make migrate && make run
make celery-worker
make celery-beat
```

### CI (GitHub Actions)

`.github/workflows/ci.yml` runs on push/PR to `main`/`develop`:
lint & format → tests against PostgreSQL → dependency vulnerability scan.

---

## License

Proprietary. PharmaCloud ERP © 2026. All rights reserved.
