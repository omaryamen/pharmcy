# RBAC API Reference

Routes are mounted under `/api/v1/rbac/*`. All responses use the standard
PharmaCloud envelope (`data` / `errors`); errors carry a stable `code` —
clients branch on `code`, never on the message.

Authentication: `Authorization: Bearer <access>` plus the tenant header
(`X-Tenant-ID` or `X-Tenant-Slug`).

## Permissions catalog

| Method & path | Permission | Description |
| --- | --- | --- |
| `GET /api/v1/rbac/permissions/` | `rbac.permission.read` | Paginated catalog. |
| `GET /api/v1/rbac/permissions/{id}/` | `rbac.permission.read` | Single permission. |
| `POST /api/v1/rbac/permissions/` | `rbac.permission.create` | Register a custom permission. |
| `PATCH /api/v1/rbac/permissions/{id}/` | `rbac.permission.update` | Update metadata. |
| `DELETE /api/v1/rbac/permissions/{id}/` | `rbac.permission.delete` | Delete (system permissions are protected). |

## Roles

| Method & path | Permission | Description |
| --- | --- | --- |
| `GET /api/v1/rbac/roles/` | `rbac.role.read` | List tenant roles. |
| `POST /api/v1/rbac/roles/` | `rbac.role.create` | Create role (`code` must be lowercase `[a-z0-9_]`; `admin` reserved). |
| `GET /api/v1/rbac/roles/{id}/` | `rbac.role.read` | Retrieve role. |
| `PATCH /api/v1/rbac/roles/{id}/` | `rbac.role.update` | Update role. |
| `DELETE /api/v1/rbac/roles/{id}/` | `rbac.role.delete` | Delete role (fails if active assignments exist). |
| `GET /api/v1/rbac/roles/{id}/permissions/` | `rbac.role.read` | Effective permission matrix (incl. inheritance source). |
| `PUT /api/v1/rbac/roles/{id}/permissions/` | `rbac.role.update` | Replace permission set: `{"permissions": {"catalog.item.read": true}}`. |
| `GET /api/v1/rbac/roles/{id}/parents/` | `rbac.role.read` | List parent links. |
| `POST /api/v1/rbac/roles/{id}/parents/` | `rbac.role.update` | Add parent: `{"parent_role": "<uuid>"}`. |
| `DELETE /api/v1/rbac/roles/{id}/parents/{parent_id}/` | `rbac.role.update` | Remove parent link. |
| `POST /api/v1/rbac/roles/{id}/clone/` | `rbac.role.create` | Clone role (links + parents). |
| `GET /api/v1/rbac/roles/{id}/history/` | `rbac.role.read` | `RoleVersion` snapshots + `RoleAuditLog` trail. |

## Groups

| Method & path | Permission | Description |
| --- | --- | --- |
| `GET /api/v1/rbac/groups/` | `rbac.group.read` | List groups. |
| `POST /api/v1/rbac/groups/` | `rbac.group.create` | Create group (`code` unique per tenant). |
| `GET /api/v1/rbac/groups/{id}/roles/` | `rbac.group.read` | Member roles. |
| `PUT /api/v1/rbac/groups/{id}/roles/` | `rbac.group.update` | Replace membership: `{"role_ids": ["<uuid>"]}`. |

## Assignments

| Method & path | Permission | Description |
| --- | --- | --- |
| `GET /api/v1/rbac/assignments/` | `rbac.assignment.read` | List assignments for the tenant. |
| `POST /api/v1/rbac/assignments/` | `rbac.assignment.create` | Assign: `{"user": "<uuid>", "role": "<uuid>", "is_primary": false, "reason": ""}`. |
| `DELETE /api/v1/rbac/assignments/{id}/` | `rbac.assignment.delete` | Revoke. |
| `POST /api/v1/rbac/assignments/bulk/` | `rbac.assignment.create` | `{"entries": [{"user": "...", "role": "..."}]}` — per-entry errors are collected. |

## Per-user management

| Method & path | Permission | Description |
| --- | --- | --- |
| `GET /api/v1/rbac/users/{user_id}/roles/` | `rbac.assignment.read` | User's active roles. |
| `PUT /api/v1/rbac/users/{user_id}/roles/` | `rbac.assignment.create` | Replace roles: `{"roles": [{"role": "<uuid>"}], "reason": ""}`. |
| `GET /api/v1/rbac/users/{user_id}/permissions/` | `rbac.assignment.read` | User's effective permissions. |
| `GET /api/v1/rbac/users/{user_id}/overrides/` | `rbac.override.read` | List overrides. |
| `POST /api/v1/rbac/users/{user_id}/overrides/` | `rbac.override.create` | Create/upsert: `{"permission": "<uuid>", "allow": bool}`. |
| `DELETE /api/v1/rbac/users/{user_id}/overrides/{override_id}/` | `rbac.override.delete` | Remove override. |

## Self-service (no permission required)

| Method & path | Description |
| --- | --- |
| `GET /api/v1/rbac/me/permissions/` | Caller's effective permissions + modules + roles. |
| `GET /api/v1/rbac/me/navigation/` | Dynamic sidebar derived from granted permissions. |

## Matrix

| Method & path | Permission | Description |
| --- | --- | --- |
| `GET /api/v1/rbac/matrix/` | `rbac.matrix.read` | Caller's matrix; pass `?role=<uuid>` for a role matrix. |

## Error codes

Domain errors are raised by the service layer and rendered by the shared
exception handler:

| Code | HTTP | Meaning |
| --- | --- | --- |
| `missing_permission` | 403 | Actor lacks the required permission. |
| `privilege_escalation` | 403 | Granting a role broader than the actor's own permissions. |
| `protected_role` | 409 | Protected role modified/removed, or reserved code `admin`. |
| `protected_assignment` | 409 | Revoking the last active admin assignment. |
| `role_in_use` | 409 | Role still has active assignments. |
| `role_assignment_conflict` | 409 | Assignment impossible in current state. |
| `conflict` | 409 | Generic state conflict (duplicate code, user not a tenant member). |
| `role_inactive` | 422 | Cannot assign an inactive role. |
| `cross_tenant_reference` | 422 | Role/user/parent from another tenant. |
| `permission_code_invalid` | 422 | Malformed permission code. |
| `not_found` | 404 | Resource missing or in another tenant (no enumeration). |
