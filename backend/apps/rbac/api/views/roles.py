"""Role lifecycle endpoints."""

from __future__ import annotations

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.api.viewsets import BaseModelViewSet
from apps.common.exceptions import NotFoundError
from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive

from ...models import Role
from ...permissions import HasPermission
from ...serializers import (
    RoleAuditLogSerializer,
    RoleCloneSerializer,
    RoleHierarchySerializer,
    RoleParentLinkSerializer,
    RolePermissionMapSerializer,
    RolePermissionSerializer,
    RoleSerializer,
    RoleVersionSerializer,
)
from ...services import RoleHierarchyService, RoleService

UUID_REGEX = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"


class RoleViewSet(BaseModelViewSet):
    """Tenant-scoped role CRUD with permission-set, hierarchy and history actions."""

    service_class = RoleService
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext, HasPermission]
    permission_code_prefix = "rbac.role"
    lookup_value_regex = UUID_REGEX

    @action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        role = self.get_object()
        data = self.get_service().history(role)
        return Response(
            {
                "versions": RoleVersionSerializer(data["versions"], many=True).data,
                "audit_logs": RoleAuditLogSerializer(data["audit_logs"], many=True).data,
            }
        )

    @action(detail=True, methods=["post"])
    def clone(self, request, pk=None):
        role = self.get_object()
        serializer = RoleCloneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        clone = self.get_service().clone(
            role,
            name=serializer.validated_data["name"],
            code=serializer.validated_data["code"],
            description=serializer.validated_data.get("description", ""),
        )
        return Response(RoleSerializer(clone).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "put"], url_path="permissions")
    def permissions(self, request, pk=None):
        role = self.get_object()
        if request.method == "PUT":
            serializer = RolePermissionMapSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.get_service().set_permissions(role, serializer.validated_data["permissions"])
            return Response({"permissions": self.get_service().permissions_matrix(role)})
        return Response({"permissions": self.get_service().permissions_matrix(role)})

    @action(detail=True, methods=["get"], url_path="parents")
    def parents(self, request, pk=None):
        role = self.get_object()
        links = role.parent_links.select_related("parent_role").order_by("parent_role__name")
        return Response(RoleHierarchySerializer(links, many=True).data)

    @action(detail=True, methods=["post"], url_path="parents")
    def add_parent(self, request, pk=None):
        role = self.get_object()
        serializer = RoleParentLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        parent = Role.objects.filter(pk=serializer.validated_data["parent_role"]).first()
        if parent is None:
            raise NotFoundError("Parent role not found.")
        link = RoleHierarchyService().add_parent(role, parent, actor=request.user)
        return Response(RoleHierarchySerializer(link).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["delete"], url_path=f"parents/(?P<parent_id>{UUID_REGEX})")
    def remove_parent(self, request, pk=None, parent_id=None):
        role = self.get_object()
        parent = Role.objects.filter(pk=parent_id).first()
        if parent is None:
            raise NotFoundError("Parent role not found.")
        RoleHierarchyService().remove_parent(role, parent, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
