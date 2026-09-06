"""RBAC module constants.

The permission catalog is the single source of truth for every capability the
platform exposes. Permission codes follow ``<module>.<resource>.<action>``
(``rbac.role.read``) or ``<module>.<action>`` (``inventory.manage``) and are
referenced by name in views/services — never hardcoded free-text strings.

New business modules should extend ``MODULE_SPECS`` here and then run
``python manage.py sync_permissions`` (or rely on the ``0002`` data migration
for a fresh install).
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Core metadata
# ---------------------------------------------------------------------------

#: Modules the platform ships. ``scope`` defaults to tenant; platform-level
#: capabilities (e.g. subscription administration) use scope ``platform``.
MODULE_SPECS: dict[str, dict[str, Any]] = {
    "dashboard": {
        "label": "Dashboard",
        "icon": "dashboard",
        "route": "/dashboard",
        "order": 10,
        "actions": ["read", "manage"],
    },
    "catalog": {
        "label": "Catalog",
        "icon": "medication",
        "route": "/catalog",
        "order": 20,
        "actions": ["manage"],
        "resources": {"item": ["read", "create", "update", "delete"]},
    },
    "inventory": {
        "label": "Inventory",
        "icon": "inventory",
        "route": "/inventory",
        "order": 30,
        "actions": ["manage"],
        "resources": {
            "stock": ["read", "create", "update", "delete"],
            "transfer": ["read", "create", "update", "delete"],
        },
    },
    "purchasing": {
        "label": "Purchasing",
        "icon": "cart",
        "route": "/purchasing",
        "order": 40,
        "actions": ["manage"],
        "resources": {"purchase_order": ["read", "create", "update", "delete"]},
    },
    "sales": {
        "label": "Sales",
        "icon": "receipt",
        "route": "/sales",
        "order": 50,
        "actions": ["manage"],
        "resources": {
            "sale": ["read", "create", "update", "delete"],
            "return": ["read", "create", "update", "delete"],
        },
    },
    "pos": {"label": "Point of Sale", "icon": "pos", "route": "/pos", "order": 60, "actions": ["read", "manage"]},
    "customers": {
        "label": "Customers",
        "icon": "people",
        "route": "/customers",
        "order": 70,
        "actions": ["read", "create", "update", "delete"],
        "resources": {
            "customer": ["read", "create", "update", "delete"],
            "medical_profile": ["read", "update"],
        },
    },
    "suppliers": {
        "label": "Suppliers",
        "icon": "truck",
        "route": "/suppliers",
        "order": 80,
        "actions": ["read", "create", "update", "delete"],
    },
    "warehouses": {
        "label": "Warehouses",
        "icon": "warehouse",
        "route": "/warehouses",
        "order": 85,
        "actions": ["read", "create", "update", "delete"],
        "resources": {
            "warehouse": ["read", "create", "update", "delete", "manage"],
            "location": ["read", "create", "update", "delete"],
        },
    },
    "inventory": {
        "label": "Inventory & Batches",
        "icon": "box",
        "route": "/inventory",
        "order": 90,
        "actions": ["read", "create", "update", "delete", "adjust"],
        "resources": {
            "stock": ["read", "create", "update", "delete"],
            "batch": ["read", "create", "update", "block", "recall"],
            "transaction": ["read"],
        },
    },
    "stock_movement": {
        "label": "Stock Movement Engine",
        "icon": "arrow-left-right",
        "route": "/stock-movements",
        "order": 95,
        "actions": [
            "read",
            "create",
            "process",
            "approve",
            "cancel",
            "reverse",
            "receive",
            "issue",
            "transfer",
            "adjust",
            "quarantine",
            "release",
            "reserve",
        ],
        "resources": {
            "movement": ["read", "create", "process", "approve", "cancel", "reverse"],
            "cost": ["read"],
            "trace": ["read"],
        },
    },
    "stock_adjustment": {
        "label": "Stock Count & Adjustment",
        "icon": "clipboard-check",
        "route": "/stock-counts",
        "order": 96,
        "actions": [
            "read",
            "create",
            "start",
            "perform",
            "submit",
            "review",
            "approve",
            "reconcile",
            "cancel",
            "recount",
            "view_system_quantity",
        ],
        "resources": {
            "count": ["read", "create", "start", "perform", "submit", "review", "approve", "reconcile", "cancel", "recount"],
            "system_quantity": ["read"],
        },
    },
    "stock_transfer": {
        "label": "Inter-Branch & Warehouse Stock Transfer",
        "icon": "truck",
        "route": "/stock-transfers",
        "order": 97,
        "actions": [
            "read",
            "create",
            "request",
            "approve",
            "pick",
            "dispatch",
            "receive",
            "reject",
            "cancel",
            "reconcile",
            "reverse",
            "discrepancy_view",
            "discrepancy_resolve",
        ],
        "resources": {
            "transfer": [
                "read",
                "create",
                "request",
                "approve",
                "pick",
                "dispatch",
                "receive",
                "reject",
                "cancel",
                "reconcile",
                "reverse",
            ],
            "discrepancy": ["discrepancy_view", "discrepancy_resolve"],
        },
    },
    "pharmacy": {
        "label": "Pharmacy",
        "icon": "medical",
        "route": "/pharmacy",
        "order": 90,
        "actions": ["read", "manage"],
    },
    "reports": {"label": "Reports", "icon": "chart", "route": "/reports", "order": 100, "actions": ["read", "manage"]},
    "billing": {
        "label": "Billing",
        "icon": "card",
        "route": "/billing",
        "order": 110,
        "actions": ["read", "create", "update", "delete"],
    },
    "rbac": {
        "label": "Access Control",
        "icon": "lock",
        "route": "/access",
        "order": 125,
        "actions": ["manage"],
        "resources": {
            "permission": ["read", "create", "update", "delete"],
            "role": ["read", "create", "update", "delete"],
            "group": ["read", "create", "update", "delete"],
            "assignment": ["read", "create", "delete"],
            "override": ["read", "create", "update", "delete"],
        },
        "extra": [
            "rbac.role.protected_manage",
            "rbac.matrix.read",
        ],
    },
    "settings": {
        "label": "Settings",
        "icon": "settings",
        "route": "/settings",
        "order": 120,
        "actions": ["read", "manage"],
    },
    "integrations": {
        "label": "Integrations",
        "icon": "plug",
        "route": "/integrations",
        "order": 130,
        "actions": ["read", "manage"],
    },
    "platform": {
        "label": "Platform",
        "icon": "cloud",
        "route": "/platform",
        "order": 140,
        "scope": "platform",
        "actions": ["read", "manage"],
    },
}

#: Roles that no API user may delete or rename. The tenant ``admin`` role is
#: created automatically during tenant bootstrap.
PROTECTED_ROLE_CODES: tuple[str, ...] = ("admin",)

#: Roles a newly created member receives by default (tenant bootstrap).
DEFAULT_ROLE_CODES: tuple[str, ...] = ("member",)

#: Predefined Enterprise Staff Roles
ADMIN_ROLE_CODE: str = "admin"
COMPANY_ADMIN_ROLE_CODE: str = "company_admin"
BRANCH_MANAGER_ROLE_CODE: str = "branch_manager"
PHARMACIST_ROLE_CODE: str = "pharmacist"
CASHIER_ROLE_CODE: str = "cashier"
INVENTORY_MANAGER_ROLE_CODE: str = "inventory_manager"
ACCOUNTANT_ROLE_CODE: str = "accountant"
PURCHASING_OFFICER_ROLE_CODE: str = "purchasing_officer"
SALES_SUPERVISOR_ROLE_CODE: str = "sales_supervisor"
CUSTOMER_SERVICE_ROLE_CODE: str = "customer_service"
MEMBER_ROLE_CODE: str = "member"

PREDEFINED_STAFF_ROLES: list[dict[str, str]] = [
    {"code": ADMIN_ROLE_CODE, "name": "Pharmacy Admin / Owner", "description": "Full tenant-level administration and operations."},
    {"code": COMPANY_ADMIN_ROLE_CODE, "name": "Company Admin", "description": "Company-wide operational governance and supervision."},
    {"code": BRANCH_MANAGER_ROLE_CODE, "name": "Branch Manager", "description": "Branch-scoped operations, POS supervision, staff and stock management."},
    {"code": PHARMACIST_ROLE_CODE, "name": "Licensed Pharmacist", "description": "Prescriptions review, clinical dispensing, and medicine management."},
    {"code": CASHIER_ROLE_CODE, "name": "POS Cashier", "description": "POS checkout, cash sessions, returns and receipts."},
    {"code": INVENTORY_MANAGER_ROLE_CODE, "name": "Inventory & Warehouse Manager", "description": "Warehouses, batches, stock movements, and counts."},
    {"code": ACCOUNTANT_ROLE_CODE, "name": "Accountant", "description": "General ledger, AP, AR, cash & bank reconciliation."},
    {"code": PURCHASING_OFFICER_ROLE_CODE, "name": "Purchasing Officer", "description": "Purchase orders, suppliers, and goods receiving."},
    {"code": SALES_SUPERVISOR_ROLE_CODE, "name": "Sales Supervisor", "description": "Sales management, customer discounts, and POS oversight."},
    {"code": CUSTOMER_SERVICE_ROLE_CODE, "name": "Customer Service", "description": "Customer profiles, orders, and inquiries."},
]

#: Stable code constants — business logic references these, never raw strings.
RBAC_PERMISSIONS: dict[str, str] = {
    "PERMISSION_READ": "rbac.permission.read",
    "PERMISSION_CREATE": "rbac.permission.create",
    "PERMISSION_UPDATE": "rbac.permission.update",
    "PERMISSION_DELETE": "rbac.permission.delete",
    "ROLE_READ": "rbac.role.read",
    "ROLE_CREATE": "rbac.role.create",
    "ROLE_UPDATE": "rbac.role.update",
    "ROLE_DELETE": "rbac.role.delete",
    "ROLE_PROTECTED_MANAGE": "rbac.role.protected_manage",
    "GROUP_READ": "rbac.group.read",
    "GROUP_CREATE": "rbac.group.create",
    "GROUP_UPDATE": "rbac.group.update",
    "GROUP_DELETE": "rbac.group.delete",
    "ASSIGNMENT_READ": "rbac.assignment.read",
    "ASSIGNMENT_CREATE": "rbac.assignment.create",
    "ASSIGNMENT_DELETE": "rbac.assignment.delete",
    "OVERRIDE_READ": "rbac.override.read",
    "OVERRIDE_CREATE": "rbac.override.create",
    "OVERRIDE_UPDATE": "rbac.override.update",
    "OVERRIDE_DELETE": "rbac.override.delete",
    "MATRIX_READ": "rbac.matrix.read",
}


def _humanize(part: str) -> str:
    return part.replace("_", " ").strip().title()


def _entry(code: str, module: str, category: str, action: str, scope: str) -> dict[str, str]:
    module_label = MODULE_SPECS[module]["label"]
    if category == "general":
        name = f"{module_label} — {_humanize(action)}"
    else:
        name = f"{module_label} — {_humanize(category)} {_humanize(action)}"
    return {
        "code": code,
        "name": name,
        "module": module,
        "category": category,
        "action": action,
        "scope": scope,
    }


def build_permission_catalog() -> list[dict[str, str]]:
    """Expand ``MODULE_SPECS`` into a flat catalog of permission entries.

    Each entry carries ``code``, ``name``, ``module``, ``category``,
    ``action`` and ``scope``. Codes are guaranteed unique.
    """
    entries: list[dict[str, str]] = []
    seen: set[str] = set()
    for module, spec in MODULE_SPECS.items():
        scope = spec.get("scope", "tenant")
        for resource, actions in spec.get("resources", {}).items():
            for action in actions:
                code = f"{module}.{resource}.{action}"
                if code in seen:
                    raise ValueError(f"Duplicate permission code: {code}")
                seen.add(code)
                entries.append(_entry(code, module, resource, action, scope))
        for action in spec.get("actions", []):
            code = f"{module}.{action}"
            if code in seen:
                raise ValueError(f"Duplicate permission code: {code}")
            seen.add(code)
            entries.append(_entry(code, module, "general", action, scope))
        if "extra" in spec:
            for code in spec["extra"]:
                if code in seen:
                    raise ValueError(f"Duplicate permission code: {code}")
                seen.add(code)
                parts = code.split(".")
                entries.append(_entry(code, parts[0], "special", parts[-1], scope))
    return entries


#: Canonical, code-generated permission catalog (imported by the data
#: migration, the sync command and the engine tests).
PERMISSION_CATALOG: list[dict[str, str]] = build_permission_catalog()


def catalog_by_module() -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for entry in PERMISSION_CATALOG:
        grouped.setdefault(entry["module"], []).append(entry)
    return grouped
