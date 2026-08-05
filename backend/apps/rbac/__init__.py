"""Enterprise Role-Based Access Control (RBAC) module.

Owns the permission catalog, tenant-scoped roles, role inheritance, user
assignment, per-user overrides, the effective-permission engine, the DRF
authorization layer, dynamic navigation metadata and full audit history.
"""

from __future__ import annotations

default_app_config = "apps.rbac.apps.RbacConfig"
