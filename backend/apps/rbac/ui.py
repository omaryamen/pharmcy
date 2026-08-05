"""UI metadata builders.

Derive dynamic front-end content directly from the permission engine so the
UI can never show an action the user cannot perform:

- ``NavigationBuilder`` produces the sidebar/navigation for the current user;
- ``PermissionTreeBuilder`` produces the admin permission-picker tree;
- ``ButtonVisibility`` answers "can this user click this button?".
"""

from __future__ import annotations

from .constants import MODULE_SPECS
from .engine import PermissionEngine
from .models import Permission


class NavigationBuilder:
    """Sidebar items grouped by module, filtered by granted permissions."""

    def __init__(self, engine: PermissionEngine | None = None) -> None:
        self.engine = engine or PermissionEngine()

    def build(self, user, tenant=None) -> list[dict]:
        granted = self.engine.effective_permissions(user, tenant)
        if not granted and not (getattr(user, "is_superuser", False)):
            return []
        modules = {code.split(".")[0] for code in granted}
        items = []
        for module, spec in sorted(MODULE_SPECS.items(), key=lambda kv: kv[1]["order"]):
            if module not in modules and not getattr(user, "is_superuser", False):
                continue
            module_permissions = sorted(code for code in granted if code.startswith(f"{module}."))
            items.append(
                {
                    "module": module,
                    "label": spec["label"],
                    "icon": spec["icon"],
                    "route": spec["route"],
                    "order": spec["order"],
                    "permissions": module_permissions,
                }
            )
        return items


class PermissionTreeBuilder:
    """Nested module → category → permission tree for permission pickers."""

    def build(self) -> list[dict]:
        modules: dict[str, dict] = {}
        for perm in Permission.objects.filter(is_active=True).order_by("module", "category", "code"):
            module = modules.setdefault(
                perm.module,
                {
                    "module": perm.module,
                    "label": MODULE_SPECS.get(perm.module, {}).get("label", perm.module.title()),
                    "categories": {},
                },
            )
            category = module["categories"].setdefault(perm.category, {"category": perm.category, "permissions": []})
            category["permissions"].append(
                {
                    "code": perm.code,
                    "name": perm.name,
                    "action": perm.action,
                    "scope": perm.scope,
                    "is_active": perm.is_active,
                }
            )
        return [
            {
                "module": module["module"],
                "label": module["label"],
                "categories": sorted(
                    (
                        {"category": key, "permissions": value["permissions"]}
                        for key, value in module["categories"].items()
                    ),
                    key=lambda item: item["category"],
                ),
            }
            for module in modules.values()
        ]


class ButtonVisibility:
    """Action-level visibility helper for button/CTA rendering."""

    def __init__(self, engine: PermissionEngine | None = None) -> None:
        self.engine = engine or PermissionEngine()

    def can(self, user, code: str, tenant=None) -> bool:
        return self.engine.has_permission(user, code, tenant)

    def permissions_for(self, user, tenant=None) -> set[str]:
        return self.engine.effective_permissions(user, tenant)

    def any(self, user, codes: list[str], tenant=None) -> bool:
        return self.engine.has_any(user, codes, tenant)

    def all(self, user, codes: list[str], tenant=None) -> bool:
        return self.engine.has_all(user, codes, tenant)
