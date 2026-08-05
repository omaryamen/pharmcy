"""Per-user RBAC endpoints: roles, effective permissions, overrides."""

from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response

from apps.common.api.viewsets import BaseAPIView
from apps.common.exceptions import NotFoundError
from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.core.models import User

from ...constants import RBAC_PERMISSIONS
from ...engine import PermissionCache
from ...models import Permission, Role
from ...permissions import HasPermission
from ...serializers import (
    RoleAssignmentSerializer,
    UserPermissionOverrideSerializer,
    UserRolesReplaceSerializer,
)
from ...services import EffectivePermissionService, RoleAssignmentService


def _get_user(user_id) -> User:
    user = User.objects.filter(pk=user_id).first()
    if user is None:
        raise NotFoundError("User not found.")
    return user


class UserRolesView(BaseAPIView):
    """Read or replace a user's active roles inside the request tenant."""

    permission_classes = [IsAuthenticatedAndActive, HasTenantContext, HasPermission]
    required_permissions = {
        "get": RBAC_PERMISSIONS["ASSIGNMENT_READ"],
        "put": RBAC_PERMISSIONS["ASSIGNMENT_CREATE"],
    }

    def get(self, request, user_id):
        user = _get_user(user_id)
        assignments = RoleAssignmentService().list_for_user(user, request.tenant)
        return Response(RoleAssignmentSerializer(assignments, many=True).data)

    def put(self, request, user_id):
        user = _get_user(user_id)
        serializer = UserRolesReplaceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role_ids = [entry["role"] for entry in serializer.validated_data["roles"]]
        role_codes = self._resolve_role_codes(role_ids)
        result = RoleAssignmentService().set_user_roles(
            user=user,
            tenant=request.tenant,
            role_codes=role_codes,
            actor=request.user,
            reason=serializer.validated_data.get("reason", ""),
        )
        assignments = RoleAssignmentService().list_for_user(user, request.tenant)
        return Response(
            {
                "assigned": result["assigned"],
                "removed": result["removed"],
                "roles": RoleAssignmentSerializer(assignments, many=True).data,
            }
        )

    def _resolve_role_codes(self, role_ids: list) -> list[str]:
        roles = Role.objects.filter(pk__in=role_ids, tenant=self.request.tenant)
        found = {role.pk: role.code for role in roles}
        missing = [rid for rid in role_ids if rid not in found]
        if missing:
            raise NotFoundError("One or more roles do not exist in this tenant.")
        return [found[rid] for rid in role_ids]


class UserEffectivePermissionsView(BaseAPIView):
    """The resolved effective permission set for a user in the request tenant."""

    permission_classes = [IsAuthenticatedAndActive, HasTenantContext, HasPermission]
    required_permissions = {
        "get": RBAC_PERMISSIONS["ASSIGNMENT_READ"],
    }

    def get(self, request, user_id):
        user = _get_user(user_id)
        service = EffectivePermissionService()
        return Response(
            {
                "user": str(user.pk),
                "roles": service.assigned_roles(user, request.tenant),
                **service.my_permissions_payload(user, request.tenant),
            }
        )


class UserPermissionOverridesView(BaseAPIView):
    """List or create per-user permission overrides."""

    permission_classes = [IsAuthenticatedAndActive, HasTenantContext, HasPermission]
    required_permissions = {
        "get": RBAC_PERMISSIONS["OVERRIDE_READ"],
        "post": RBAC_PERMISSIONS["OVERRIDE_CREATE"],
    }

    def get(self, request, user_id):
        user = _get_user(user_id)
        overrides = user.permission_overrides.filter(tenant=request.tenant).select_related("permission")
        return Response(UserPermissionOverrideSerializer(overrides, many=True).data)

    def post(self, request, user_id):
        user = _get_user(user_id)
        permission = Permission.objects.filter(pk=request.data.get("permission")).first()
        if permission is None:
            raise NotFoundError("Permission not found.")
        if request.data.get("deny", False):
            allow = False
        else:
            allow = bool(request.data.get("allow", True))
        override, _created = user.permission_overrides.update_or_create(
            tenant=request.tenant,
            user=user,
            permission=permission,
            defaults={"allow": allow},
        )
        PermissionCache().invalidate()
        return Response(UserPermissionOverrideSerializer(override).data, status=status.HTTP_201_CREATED)


class UserPermissionOverrideDetailView(BaseAPIView):
    """Remove a per-user override."""

    permission_classes = [IsAuthenticatedAndActive, HasTenantContext, HasPermission]
    required_permissions = {
        "delete": RBAC_PERMISSIONS["OVERRIDE_DELETE"],
    }

    def delete(self, request, user_id, override_id):
        user = _get_user(user_id)
        override = user.permission_overrides.filter(tenant=request.tenant, pk=override_id).first()
        if override is None:
            raise NotFoundError("Override not found.")
        override.delete()
        PermissionCache().invalidate()
        return Response(status=status.HTTP_204_NO_CONTENT)
