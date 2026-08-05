# RBAC Architecture & Configuration

Enterprise role-based access control for PharmaCloud ERP. This document covers
the permission model, the resolution engine, the tenant bootstrap, the write
guards and every configuration knob.

## 1. The permission model

### 1.1 Catalog

Every capability the platform exposes is a **permission code** in one of two
shapes:

- `<module>.<resource>.<action>` — e.g. `catalog.item.read`
- `<module>.<action>` — e.g. `inventory.manage` (module-level action)

Codes are generated from `MODULE_SPECS` in `apps/rbac/constants.py` into
`PERMISSION_CATALOG` (76 entries across 15 modules). Each entry carries:

| Field | Meaning |
| --- | --- |
| `code` | Stable API contract, e.g. `rbac.role.read` |
| `module` / `category` | Grouping for the UI permission tree |
| `action` | `read` / `create` / `update` / `delete` / `manage` / `protected_manage` |
| `scope` | `tenant` (default) or `platform` (e.g. subscription administration) |

Add a module by editing `MODULE_SPECS`, then run
`python manage.py sync_permissions` (or let the `0002_seed_permissions`
data migration provision a fresh install). `sync_permissions` creates new
permissions, updates metadata and deactivates removed ones — it never deletes
rows.

### 1.2 Entities

```
Permission ──< RolePermission >── Role ──< RoleHierarchy (parents)
Role ──< RoleGroupMembership >── RoleGroup
Role ──< UserRoleAssignment >── User
User ──< UserPermissionOverride >── Permission
Role ──< RoleVersion (snapshot history)
Role ──< RoleAuditLog (audit trail)
```

All RBAC rows are tenant-scoped; `Role`, `RoleGroup`, `UserRoleAssignment`
and `UserPermissionOverride` carry a `tenant` FK. `Permission` is global.

## 2. Resolution engine

`PermissionEngine` (`engine/engine.py`) answers "can this user do X in this
tenant?".

### 2.1 Precedence (highest wins)

1. **User override** — `UserPermissionOverride` for the exact code;
2. **Direct link** — a `RolePermission` on any role assigned to the user;
3. **Inherited link** — via role parents (transitive, cycle-safe).

Across different roles held by the same user, **grant beats denial**.
`overrides` are resolved last and can both add and strip a code.

Superusers bypass the engine entirely when `RBAC_SUPERADMIN_BYPASS` is enabled.

### 2.2 Caching

`PermissionCache` (Redis via `django.core.cache`) stores the effective set per
`(user, tenant)` under `rbac:effective:{version}:{user_id}:{tenant_id}`. The
`version` is a global monotonic counter kept in the cache: any RBAC mutation
(`PermissionCache.invalidate()`, wired through `signals.py`) bumps it, so every
previously computed result is atomically stale. `RBAC_CACHE_TTL_SECONDS`
bounds the garbage the TTL-based backend eventually evicts.

Per-request, the middleware stores the computed set on `request._rbac_effective`
so DRF permission classes, decorators and views compute it exactly once.

## 3. Tenant bootstrap

Creating a `Tenant` fires `post_save` → `RoleBootstrapService` (guarded by
`RBAC_BOOTSTRAP_ON_TENANT_CREATE`). It provisions:

- **`admin`** (protected) — every active tenant-scope permission;
- **`member`** (default, not protected) — every tenant-scope **read**
  permission, excluding the `rbac` admin module.

Bootstrap is idempotent: a soft-deleted role is restored in place rather than
duplicated, so re-provisioning a tenant never raises a unique-constraint
violation. Both roles receive an initial `RoleVersion` snapshot and audit log.

## 4. Write guards

All mutations run inside `@transaction.atomic` service methods that re-check
authorization and record history:

| Guard | Behavior |
| --- | --- |
| Permission check | The actor needs the CRUD code derived from the HTTP method (`<prefix>.read` / `.create` / `.update` / `.delete`), or an explicit `required_permissions` map. |
| Protected roles | `admin` (and any `is_protected` role) can only be touched by actors holding `rbac.role.protected_manage`. Code `admin` is reserved for creation. |
| Escalation guard | `assign` rejects granting a role whose granted permissions are not a subset of the actor's own effective permissions (`PrivilegeEscalationError`). Disable with `RBAC_ENFORCE_ESCALATION_GUARD=False`. |
| Last admin | The final active `admin` assignment of a tenant cannot be revoked (`ProtectedAssignmentError`). |
| Role in use | A role with active assignments cannot be deleted. |
| Cross-tenant | Roles, users and parents must belong to the request tenant (`CrossTenantError`). |
| History | Every mutation writes a `RoleVersion` (pruned to `RBAC_ROLE_HISTORY_MAX_VERSIONS`) and a `RoleAuditLog`. |

## 5. HTTP → permission mapping

DRF permission classes derive the code from the view:

| HTTP method | Action code |
| --- | --- |
| GET / HEAD / OPTIONS | `<prefix>.read` |
| POST | `<prefix>.create` |
| PUT / PATCH | `<prefix>.update` |
| DELETE | `<prefix>.delete` |

Viewsets set `permission_code_prefix` (e.g. `rbac.role`); standalone views set
`required_permissions`. `HasObjectPermission` additionally verifies the object
belongs to the request tenant. Function views and Celery tasks can use
`require_permission(...)` / `require_permissions(...)`.

## 6. Configuration reference

All keys are read from the environment in `config/settings/base.py`:

| Setting | Default | Meaning |
| --- | --- | --- |
| `RBAC_SUPERADMIN_BYPASS` | `True` | Superusers bypass all checks. |
| `RBAC_CACHE_TTL_SECONDS` | `300` | TTL for effective-permission cache entries. |
| `RBAC_ENFORCE_ESCALATION_GUARD` | `True` | Enforce the escalation guard on assign. |
| `RBAC_ROLE_HISTORY_MAX_VERSIONS` | `20` | Number of `RoleVersion` snapshots kept per role. |
| `RBAC_PROTECTED_ROLE_CODES` | `["admin"]` | Codes no API user may delete/rename. |
| `RBAC_DEFAULT_ROLE_CODES` | `["member"]` | Roles new members receive by default. |
| `RBAC_BOOTSTRAP_ON_TENANT_CREATE` | `True` | Provision admin/member roles when a tenant is created. |
| `RBAC_PERMISSION_CODE_REGEX` | `^[a-z][a-z0-9._]*$` | Valid permission code pattern. |
