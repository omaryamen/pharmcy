"""RBAC API views."""

from __future__ import annotations

from .assignments import AssignmentViewSet
from .groups import RoleGroupViewSet
from .matrix import PermissionMatrixView
from .me import MyNavigationView, MyPermissionsView
from .permissions import PermissionViewSet
from .roles import RoleViewSet
from .users import (
    UserEffectivePermissionsView,
    UserPermissionOverrideDetailView,
    UserPermissionOverridesView,
    UserRolesView,
)

__all__ = [
    "AssignmentViewSet",
    "PermissionMatrixView",
    "PermissionViewSet",
    "RoleGroupViewSet",
    "RoleViewSet",
    "UserEffectivePermissionsView",
    "UserPermissionOverrideDetailView",
    "UserPermissionOverridesView",
    "UserRolesView",
    "MyNavigationView",
    "MyPermissionsView",
]
