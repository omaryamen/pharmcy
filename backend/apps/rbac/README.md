# apps/rbac — Enterprise Role-Based Access Control

Production RBAC for PharmaCloud ERP. A permission catalog (code-driven,
76 entries), a cached resolution engine, tenant-scoped roles/groups/assignments,
per-user overrides, role inheritance and versioned audit history.

## Scope

| Concern | Where it lives |
| --- | --- |
| Permission catalog | `constants.py` (`MODULE_SPECS` → `PERMISSION_CATALOG`) |
| Effective-permission engine + cache | `engine/` (`engine.py`, `resolver.py`, `cache.py`) |
| Roles & permission sets | `models/role.py` + `services/role.py` |
| Role inheritance | `models/hierarchy.py` + `services/hierarchy.py` |
| Role groups | `models/group.py` + `services/group.py` |
| User ↔ role assignments | `models/assignment.py` + `services/assignment.py` |
| Per-user overrides | `models/assignment.py` |
| Tenant bootstrap (admin/member) | `services/bootstrap.py` + `signals.py` |
| Read-side queries / UI metadata | `services/effective.py` + `ui.py` |
| DRF authorization | `permissions.py` (HasPermission …), `decorators.py` |
| REST API | `api/` (routers + views, mounted under `/api/v1/rbac/*`) |

## Design highlights

- **Catalog is the single source of truth.** Every capability is a
  `<module>.<resource>.<action>` (or `<module>.<action>`) code in
  `MODULE_SPECS`. Business logic references codes through
  `RBAC_PERMISSIONS`, never hardcoded strings. A data migration seeds the
  catalog; `python manage.py sync_permissions` reconciles drift.
- **One engine, one cache.** `PermissionEngine.effective_permissions` computes
  a user's exact granted set once per (user, tenant), caches it, and answers
  point checks with no further I/O. A global monotonic version key invalidates
  every cached result on any RBAC mutation.
- **Precedence.** User override > direct role link > inherited link. Across the
  roles a user holds, a grant beats a denial (union semantics).
- **Safe by default.** Members get every tenant-scope *read* (excluding the
  `rbac` admin module); the protected `admin` role gets everything.
- **Escalation guard.** An actor may only grant a role whose granted
  permissions are a subset of their own effective permissions
  (`RBAC_ENFORCE_ESCALATION_GUARD`).
- **Last-admin protection.** The final active `admin` assignment in a tenant
  can never be revoked.
- **Full audit.** Role mutations write a `RoleVersion` snapshot plus a
  `RoleAuditLog` entry and prune history to `RBAC_ROLE_HISTORY_MAX_VERSIONS`.
- **Soft deletes, hard truth.** Removed role-permission and group-role links
  are hard-deleted so the M2M relations never leak stale memberships.

## Running tests

```bash
cd backend
.venv\Scripts\python.exe -m pytest tests/test_rbac_models.py tests/test_rbac_engine.py tests/test_rbac_services.py tests/test_rbac_api.py tests/test_rbac_security.py -q
```

## Configuration

All policy knobs are env-driven — see `docs/RBAC_ARCHITECTURE.md` for the
full reference and `config/settings/base.py` for defaults.

## Endpoints

See `docs/RBAC_API.md` for the request/response contracts and error codes.
Routes are mounted under `/api/v1/rbac/*` in `api/urls.py`.
