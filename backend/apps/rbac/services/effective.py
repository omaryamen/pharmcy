"""Read-side service: answers "what can this user do" questions.

This is the facade consumed by the API (``/me/permissions``,
``/me/navigation``, the permission matrix and user effective-permission
endpoints) and by the UI-metadata builders.
"""

from __future__ import annotations

from ..constants import MODULE_SPECS
from ..engine import PermissionEngine
from ..models import Permission, Role, UserRoleAssignment
from ..ui import NavigationBuilder, PermissionTreeBuilder


class EffectivePermissionService:
    def __init__(self, engine: PermissionEngine | None = None) -> None:
        self.engine = engine or PermissionEngine()

    def effective(self, user, tenant=None) -> set[str]:
        return self.engine.effective_permissions(user, tenant)

    def can(self, user, code: str, tenant=None) -> bool:
        return self.engine.has_permission(user, code, tenant)

    def modules(self, user, tenant=None) -> list[str]:
        codes = self.engine.modules_for(user, tenant)
        ordered = [module for module, spec in sorted(MODULE_SPECS.items(), key=lambda kv: kv[1]["order"]) if module in codes]
        return ordered

    # ------------------------------------------------------------------
    # API payloads
    # ------------------------------------------------------------------
    def my_permissions_payload(self, user, tenant=None) -> dict:
        codes = sorted(self.effective(user, tenant))
        meta = {
            p["code"]: {
                "code": p["code"],
                "name": p["name"],
                "module": p["module"],
                "category": p["category"],
                "action": p["action"],
                "scope": p["scope"],
            }
            for p in Permission.objects.filter(code__in=codes, is_active=True).values(
                "code", "name", "module", "category", "action", "scope"
            )
        }
        return {
            "count": len(codes),
            "permissions": {code: meta.get(code, {"code": code}) for code in codes},
            "modules": self.modules(user, tenant),
        }

    def role_matrix(self, role: Role) -> dict:
        resolver = self.engine.resolver
        matrix = {}
        for code, (allow, source) in resolver.role_permission_map(role).items():
            matrix[code] = {"allow": allow, "source": source}
        return matrix

    def user_matrix(self, user, tenant=None) -> dict:
        granted = self.effective(user, tenant)
        rows = {}
        for perm in Permission.objects.filter(is_active=True).order_by("module", "category", "code"):
            rows[perm.code] = {
                "name": perm.name,
                "module": perm.module,
                "category": perm.category,
                "action": perm.action,
                "scope": perm.scope,
                "granted": perm.code in granted,
            }
        return {
            "count": len(rows),
            "granted_count": len(granted),
            "permissions": rows,
        }

    def assigned_roles(self, user, tenant=None) -> list[dict]:
        assignments = UserRoleAssignment.objects.filter(user=user, tenant=tenant, is_active=True).select_related("role")
        return [
            {
                "role_id": str(assignment.role_id),
                "code": assignment.role.code,
                "name": assignment.role.name,
                "is_primary": assignment.is_primary,
            }
            for assignment in assignments
        ]

    # ------------------------------------------------------------------
    # UI metadata
    # ------------------------------------------------------------------
    def permission_tree(self) -> list[dict]:
        return PermissionTreeBuilder().build()

    def navigation(self, user, tenant=None) -> list[dict]:
        return NavigationBuilder(self.engine).build(user, tenant)
