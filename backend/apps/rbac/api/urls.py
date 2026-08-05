"""API routes for the RBAC app (mounted under /api/v1/)."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AssignmentViewSet,
    MyNavigationView,
    MyPermissionsView,
    PermissionMatrixView,
    PermissionViewSet,
    RoleGroupViewSet,
    RoleViewSet,
    UserEffectivePermissionsView,
    UserPermissionOverrideDetailView,
    UserPermissionOverridesView,
    UserRolesView,
)

app_name = "rbac"

router = DefaultRouter()
router.register("rbac/permissions", PermissionViewSet, basename="rbac-permission")
router.register("rbac/roles", RoleViewSet, basename="rbac-role")
router.register("rbac/groups", RoleGroupViewSet, basename="rbac-group")
router.register("rbac/assignments", AssignmentViewSet, basename="rbac-assignment")

urlpatterns = [
    # --- Per-user RBAC management ---
    path("rbac/users/<uuid:user_id>/roles/", UserRolesView.as_view(), name="rbac-user-roles"),
    path(
        "rbac/users/<uuid:user_id>/permissions/",
        UserEffectivePermissionsView.as_view(),
        name="rbac-user-permissions",
    ),
    path("rbac/users/<uuid:user_id>/overrides/", UserPermissionOverridesView.as_view(), name="rbac-user-overrides"),
    path(
        "rbac/users/<uuid:user_id>/overrides/<uuid:override_id>/",
        UserPermissionOverrideDetailView.as_view(),
        name="rbac-user-override-detail",
    ),
    # --- Self-service ---
    path("rbac/me/permissions/", MyPermissionsView.as_view(), name="rbac-me-permissions"),
    path("rbac/me/navigation/", MyNavigationView.as_view(), name="rbac-me-navigation"),
    # --- Matrix ---
    path("rbac/matrix/", PermissionMatrixView.as_view(), name="rbac-matrix"),
] + router.urls
