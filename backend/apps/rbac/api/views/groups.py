"""Role group endpoints."""

from __future__ import annotations

from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.api.viewsets import BaseModelViewSet
from apps.common.exceptions import NotFoundError
from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive

from ...models import Role
from ...permissions import HasPermission
from ...serializers import RoleGroupRolesSerializer, RoleGroupSerializer, RoleSerializer
from ...services import RoleGroupService

UUID_REGEX = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"


class RoleGroupViewSet(BaseModelViewSet):
    """Tenant-scoped role groups and their role membership."""

    service_class = RoleGroupService
    serializer_class = RoleGroupSerializer
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext, HasPermission]
    permission_code_prefix = "rbac.group"
    lookup_value_regex = UUID_REGEX

    @action(detail=True, methods=["get", "put"], url_path="roles")
    def roles(self, request, pk=None):
        group = self.get_object()
        if request.method == "PUT":
            serializer = RoleGroupRolesSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            role_ids = serializer.validated_data["role_ids"]
            found = set(Role.objects.filter(pk__in=role_ids, tenant=group.tenant).values_list("pk", flat=True))
            missing = set(role_ids) - found
            if missing:
                raise NotFoundError("One or more roles do not exist in this tenant.")
            self.get_service().set_roles(group, role_ids)
        memberships = group.memberships.select_related("role").order_by("role__name")
        return Response(RoleSerializer([m.role for m in memberships], many=True).data)
