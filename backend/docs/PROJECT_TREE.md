# PharmaCloud ERP — Backend Project Tree

> Generated for the foundation milestone. `.venv`, `__pycache__`, `.pytest_cache`,
> `.ruff_cache`, `media/`, `staticfiles/` and build artifacts are excluded.

```
backend/
├── .github/
│   └── workflows/
│       └── ci.yml                      # GitHub Actions: lint, format-check, tests (sqlite + postgres)
├── apps/
│   ├── __init__.py
│   ├── common/                         # Cross-cutting foundation app
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── exceptions.py               # PharmaCloudError + domain exception hierarchy
│   │   ├── permissions.py              # IsAuthenticatedAndActive, HasTenantContext, ...
│   │   ├── storages.py                 # S3 / MinIO storage backend
│   │   ├── api/
│   │   │   ├── exceptions.py           # normalize_errors + DRF exception_handler
│   │   │   ├── pagination.py           # DefaultPagination (frontend-friendly shape)
│   │   │   ├── renderers.py            # ApiRenderer — unified response envelope
│   │   │   ├── serializers.py          # shared serializer mixins/fields
│   │   │   ├── viewsets.py             # BaseAPIView / BaseModelViewSet
│   │   ├── middleware/
│   │   │   ├── request_context.py      # request-id + timing context
│   │   │   └── tenant.py               # TenantIdentificationMiddleware
│   │   ├── models/
│   │   │   ├── bases.py                # UUIDBase, TimeStampedBase, SoftDeleteBase, AuditBase, FullAuditModel
│   │   │   ├── managers.py             # SoftDeleteManager, TenantManager, AllObjectsManager
│   │   │   └── tenancy.py              # TenantAwareModel
│   │   ├── repositories/
│   │   │   └── base.py                 # BaseRepository (CRUD + soft/hard delete)
│   │   ├── services/
│   │   │   └── base.py                 # BaseService (transactions, tenant injection, validation)
│   │   └── utils/
│   │       ├── context.py              # request-id / correlation helpers
│   │       ├── logging.py              # JsonFormatter + RequestContextFilter
│   │       ├── strings.py              # slugify etc.
│   │       ├── tenant.py               # resolve_tenant (Redis-cached)
│   │       └── time.py                 # timezone helpers
│   └── core/                           # Users, tenants, health (foundation domain)
│       ├── admin.py                    # User + Tenant admin
│       ├── apps.py
│       ├── api/
│       │   ├── serializers.py          # UserSerializer
│       │   ├── urls.py                 # /health/*, /auth/*
│       │   └── views.py                # LivenessView, ReadinessView, MeView
│       ├── migrations/
│       │   ├── 0001_initial.py         # Tenant + User (initial schema)
│       ├── models/
│       │   ├── tenant.py               # Tenant (status lifecycle, slug, timezone)
│       │   └── user.py                 # User (email login, UUID, tenants M2M)
├── config/                             # Project configuration package
│   ├── asgi.py
│   ├── celery.py                       # Celery app + autodiscovery
│   ├── urls.py                         # admin, /api/v1/, schema, docs, handler404/500
│   ├── wsgi.py
│   └── settings/
│       ├── base.py                     # Shared settings (env-driven)
│       ├── development.py              # DEBUG + local overrides
│       ├── production.py               # hardened production settings
│       └── testing.py                  # pytest settings (sqlite in-memory by default)
├── docs/
│   └── PROJECT_TREE.md                 # This file
├── nginx/
│   └── nginx.conf                      # HTTP→HTTPS, static/media, API proxy
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   ├── production.txt
│   └── testing.txt
├── scripts/
│   └── wait_for_db.py                  # DB readiness check for containers
├── static/
│   └── .gitkeep
├── tests/
│   ├── conftest.py                     # fixtures (factories, API clients, static root)
│   ├── factories.py                    # factory_boy factories
│   ├── test_api.py                     # envelope + JWT contracts
│   ├── test_health.py                  # liveness / readiness probes
│   ├── test_models.py                  # User + Tenant model behavior
│   └── test_repositories_services.py   # BaseRepository / BaseService contracts
├── .dockerignore
├── .env.example                        # Documented environment variables
├── .gitignore
├── .pre-commit-config.yaml             # pre-commit hooks (ruff, black, isort, ...)
├── Dockerfile                          # Dev image
├── Dockerfile.prod                     # Multi-stage production image
├── Makefile                            # make targets (install/test/lint/docker/...)
├── docker-compose.yml                  # Dev stack: postgres, redis, minio, web, celery
├── docker-compose.prod.yml             # Production stack
├── entrypoint.sh                       # Container entrypoint (wait-for-db + migrate)
├── manage.py
└── pyproject.toml                      # ruff/black/isort/pytest configuration
```
