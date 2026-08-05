# PharmaCloud ERP — Backend Project Tree

> Generated for the foundation + authentication + enterprise-RBAC milestone.
> `.venv`, `__pycache__`, `.pytest_cache`, `.ruff_cache`, `media/`,
> `staticfiles/` and build artifacts are excluded.

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
│   ├── authentication/                 # Identity & access (login lifecycle, verification, audit)
│   │   ├── README.md                   # module overview
│   │   ├── admin.py                    # LoginSession / VerificationToken / PasswordHistory / SecurityEvent
│   │   ├── apps.py
│   │   ├── exceptions.py               # AuthError hierarchy (invalid_credentials, account_locked, ...)
│   │   ├── throttles.py                # email/IP-scoped login, reset & register throttles
│   │   ├── validators.py               # password strength + verification-code format
│   │   ├── notifications.py            # verification/reset/lockout emails (+ SMS hook)
│   │   ├── tasks.py                    # Celery tasks for code delivery
│   │   ├── signals.py                  # status transitions, session revocation on lock/delete
│   │   ├── utils.py                    # client_ip, parse_user_agent, deliver_phone_code
│   │   ├── api/
│   │   │   ├── urls.py                 # /api/v1/auth/* routes
│   │   │   └── views/
│   │   │       ├── auth.py             # login, refresh, verify, logout
│   │   │       ├── registration.py     # register
│   │   │       ├── verification.py     # email/phone verify + password reset
│   │   │       ├── password.py         # password change
│   │   │       ├── profile.py          # /auth/me/ + /auth/profile/
│   │   │       ├── sessions.py         # session list / revoke / revoke-all
│   │   │       └── security.py         # security events trail
│   │   ├── migrations/
│   │   │   └── 0001_initial.py         # LoginSession, VerificationToken, PasswordHistory, SecurityEvent
│   │   ├── models/
│   │   │   ├── session.py              # LoginSession (ledger keyed by refresh jti)
│   │   │   ├── token.py                # VerificationToken (hashed OTPs, single-use)
│   │   │   ├── password.py             # PasswordHistory (reuse prevention)
│   │   │   └── event.py                # SecurityEvent (audit trail)
│   │   ├── repositories/
│   │   │   ├── session.py              # session CRUD + JWT blacklist helpers
│   │   │   ├── token.py                # token issue / invalidate / consume
│   │   │   ├── password.py             # history recording + reuse checks
│   │   │   └── event.py                # audit event persistence
│   │   ├── selectors.py                # session / event read queries
│   │   ├── serializers/
│   │   │   ├── auth.py                 # login / refresh / verify / logout contracts
│   │   │   ├── registration.py
│   │   │   ├── verification.py         # OTP confirm / reset contracts
│   │   │   ├── password.py             # change-password contract
│   │   │   ├── profile.py              # editable profile subset
│   │   │   ├── session.py              # LoginSessionSerializer
│   │   │   └── security.py             # SecurityEventSerializer
│   │   └── services/
│   │       ├── auth.py                 # login (lockout), refresh (rotation), logout, verify
│   │       ├── registration.py         # account creation + initial code
│   │       ├── verification.py         # email/phone verify + password reset
│   │       ├── password.py             # change password + history + revoke-all
│   │       ├── session.py              # session list/revoke
│   │       ├── security.py             # audit trail reads
│   │       └── events.py               # record_* audit helpers
│   ├── rbac/                           # Enterprise role-based access control
│   │   ├── README.md                   # module overview
│   │   ├── admin.py                    # Permission / Role / RoleGroup / Assignment admin
│   │   ├── apps.py
│   │   ├── constants.py                # MODULE_SPECS → PERMISSION_CATALOG (76 codes) + RBAC_PERMISSIONS
│   │   ├── decorators.py               # require_permission / require_permissions
│   │   ├── exceptions.py               # RbacError hierarchy (protected_role, privilege_escalation, ...)
│   │   ├── managers.py                 # Permission / role query managers
│   │   ├── middleware.py               # PermissionContextMiddleware (per-request cache slot)
│   │   ├── permissions.py              # HasPermission, HasAny/All, HasModuleAccess, HasObjectPermission
│   │   ├── serializers.py              # Role / Group / Assignment / Override / History contracts
│   │   ├── signals.py                  # tenant bootstrap + cache-version invalidation
│   │   ├── ui.py                       # NavigationBuilder / PermissionTreeBuilder / ButtonVisibility
│   │   ├── utils.py                    # code helpers
│   │   ├── api/
│   │   │   ├── urls.py                 # /api/v1/rbac/* routes (router + standalone views)
│   │   │   └── views/
│   │   │       ├── permissions.py      # catalog CRUD
│   │   │       ├── roles.py            # role CRUD, permissions, parents, clone, history
│   │   │       ├── groups.py           # group CRUD + role membership
│   │   │       ├── assignments.py      # assign / revoke / bulk
│   │   │       ├── users.py            # per-user roles / effective perms / overrides
│   │   │       ├── me.py               # self-service permissions + navigation
│   │   │       └── matrix.py           # role / caller permission matrix
│   │   ├── engine/
│   │   │   ├── engine.py               # PermissionEngine (precedence, point checks, cache)
│   │   │   ├── resolver.py             # role_permission_map incl. inheritance
│   │   │   └── cache.py                # PermissionCache (versioned effective-perm cache)
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── sync_permissions.py # reconcile catalog with constants
│   │   ├── migrations/
│   │   │   ├── 0001_initial.py         # Permission, Role, RoleGroup, Hierarchy, Assignment, Override, Audit
│   │   │   └── 0002_seed_permissions.py# data migration seeding the 76-code catalog
│   │   ├── models/
│   │   │   ├── permission.py           # Permission (global catalog)
│   │   │   ├── role.py                 # Role + RolePermission links
│   │   │   ├── hierarchy.py            # RoleHierarchy (parent links, cycle-safe)
│   │   │   ├── group.py                # RoleGroup + RoleGroupMembership
│   │   │   ├── assignment.py           # UserRoleAssignment + UserPermissionOverride
│   │   │   └── audit.py                # RoleVersion snapshots + RoleAuditLog
│   │   ├── repositories/
│   │   │   ├── permission.py           # catalog + sync queries
│   │   │   ├── role.py                 # role CRUD + link replacement (hard delete)
│   │   │   ├── hierarchy.py            # parent-link management
│   │   │   ├── group.py                # group CRUD + membership replacement
│   │   │   ├── assignment.py           # active assignments, primaries, admin count
│   │   │   └── audit.py                # version snapshots (pruning) + audit trail
│   │   └── services/
│   │       ├── permission.py           # catalog sync
│   │       ├── role.py                 # role lifecycle + guards + history
│   │       ├── hierarchy.py            # add/remove parent, cycle detection
│   │       ├── group.py                # group lifecycle + role membership
│   │       ├── assignment.py           # assign/revoke + escalation/protected/last-admin guards
│   │       ├── bootstrap.py            # idempotent tenant admin/member provisioning
│   │       └── effective.py            # read-side facade (my perms, matrices, navigation)
│   └── core/                           # Users, tenants, health (foundation domain)
│       ├── admin.py                    # User + Tenant admin
│       ├── apps.py
│       ├── api/
│       │   ├── serializers.py          # UserSerializer
│       │   ├── urls.py                 # /health/* (auth moved to apps.authentication)
│       │   └── views.py                # LivenessView, ReadinessView
│       ├── migrations/
│       │   ├── 0001_initial.py         # Tenant + User (initial schema)
│       │   └── 0002_user_identity.py   # UserStatus lifecycle, verification flags, security fields
│       ├── models/
│       │   ├── tenant.py               # Tenant (status lifecycle, slug, timezone)
│       │   └── user.py                 # User (email login, UUID, status, soft delete, tenants M2M)
├── config/                             # Project configuration package
│   ├── asgi.py
│   ├── celery.py                       # Celery app + autodiscovery
│   ├── urls.py                         # admin, /api/v1/, schema, docs, handler404/500
│   ├── wsgi.py
│   └── settings/
│       ├── base.py                     # Shared settings (env-driven) incl. auth policy
│       ├── development.py              # DEBUG + local overrides
│       ├── production.py               # hardened production settings
│       └── testing.py                  # pytest settings (sqlite in-memory by default)
├── docs/
│   ├── AUTH_API.md                     # Authentication API reference + error codes
│   ├── AUTH_CONFIG.md                  # Policy / throttle / JWT configuration guide
│   ├── AUTH_FLOWS.md                   # Mermaid sequence diagrams for identity flows
│   ├── RBAC_API.md                     # RBAC API reference + error codes
│   ├── RBAC_ARCHITECTURE.md            # Permission model, engine, guards, configuration
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
│   ├── conftest.py                     # fixtures (factories, API clients, static root, mail outbox)
│   ├── factories.py                    # factory_boy factories
│   ├── helpers.py                      # email/OTP extraction helpers
│   ├── test_api.py                     # envelope + JWT contracts
│   ├── test_auth_api.py                # login / refresh / verify / logout / lockout
│   ├── test_auth_models.py             # LoginSession / VerificationToken / PasswordHistory / SecurityEvent
│   ├── test_health.py                  # liveness / readiness probes
│   ├── test_models.py                  # User + Tenant model behavior
│   ├── test_password.py                # password change + reuse prevention
│   ├── test_repositories_services.py   # BaseRepository / BaseService contracts
│   ├── test_rbac_api.py                # RBAC API endpoints (roles, groups, assignments, users, me, matrix)
│   ├── test_rbac_engine.py             # PermissionEngine precedence, caching, module access
│   ├── test_rbac_models.py             # Permission / Role / Group / Hierarchy / Assignment models
│   ├── test_rbac_security.py           # escalation, protected-role, last-admin, tenant isolation
│   ├── test_rbac_services.py           # Role / Group / Assignment / Bootstrap services
│   ├── test_sessions.py                # session ledger, audit trail, profile
│   ├── test_throttling.py              # per-email / per-IP rate limits
│   └── test_verification.py            # registration, email/phone verify, password reset
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
