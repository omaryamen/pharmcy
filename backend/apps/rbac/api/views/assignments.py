"""Role assignment endpoints (assign / revoke / bulk)."""

from __future__ import annotations

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.api.viewsets import BaseModelViewSet
from apps.common.exceptions import NotFoundError
from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.core.models import User

from ...models import Role
from ...permissions import HasPermission
from ...serializers import (
    AssignmentCreateSerializer,
    BulkAssignSerializer,
    RoleAssignmentSerializer,
)
from ...services import RoleAssignmentService

UUID_REGEX = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"


class AssignmentViewSet(BaseModelViewSet):
    """Create, list and revoke user↔role assignments for the request tenant."""

    service_class = RoleAssignmentService
    serializer_class = RoleAssignmentSerializer
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext, HasPermission]
    permission_code_prefix = "rbac.assignment"
    lookup_value_regex = UUID_REGEX

    def create(self, request, *args, **kwargs):
        serializer = AssignmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self._get_user(serializer.validated_data["user"])
        role = self._get_role(serializer.validated_data["role"])
        assignment = self.get_service().assign(
            user=user,
            role=role,
            actor=request.user,
            is_primary=serializer.validated_data.get("is_primary", False),
            reason=serializer.validated_data.get("reason", ""),
        )
        return Response(RoleAssignmentSerializer(assignment).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        assignment = self.get_object()
        self.get_service().revoke(
            user=assignment.user,
            role=assignment.role,
            actor=request.user,
            reason="revoked via API",
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"])
    def bulk(self, request):
        serializer = BulkAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entries = []
        for entry in serializer.validated_data["entries"]:
            user = self._get_user(entry["user"])
            role = self._get_role(entry["role"])
            entries.append({"user": user, "role": role, "reason": entry.get("reason", "")})
        result = self.get_service().bulk_assign(entries, actor=request.user)
        return Response(result)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _get_user(self, user_id) -> User:
        user = User.objects.filter(pk=user_id).first()
        if user is None:
            raise NotFoundError("User not found.")
        return user

    def _get_role(self, role_id) -> Role:
        role = Role.objects.filter(pk=role_id).first()
        if role is None:
            raise NotFoundError("Role not found.")
        return role
