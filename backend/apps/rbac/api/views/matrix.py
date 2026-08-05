"""Permission matrix endpoint."""

from __future__ import annotations

from rest_framework.response import Response

from apps.common.api.viewsets import BaseAPIView
from apps.common.exceptions import NotFoundError
from apps.common.permissions import IsAuthenticatedAndActive

from ...constants import RBAC_PERMISSIONS
from ...models import Role
from ...permissions import HasPermission
from ...services import EffectivePermissionService


class PermissionMatrixView(BaseAPIView):
    """Role or user permission matrix.

    ``GET /rbac/matrix/?role=<uuid>`` returns the role's allow/deny matrix
    (with inheritance source); without ``role`` it returns the caller's
    effective matrix.
    """

    permission_classes = [IsAuthenticatedAndActive, HasPermission]
    required_permissions = {"get": RBAC_PERMISSIONS["MATRIX_READ"]}

    def get(self, request):
        service = EffectivePermissionService()
        role_id = request.query_params.get("role")
        if role_id:
            role = Role.objects.filter(pk=role_id).first()
            if role is None:
                raise NotFoundError("Role not found.")
            if request.tenant is not None and role.tenant_id != request.tenant.pk:
                raise NotFoundError("Role not found in this tenant.")
            return Response(
                {
                    "role": str(role.pk),
                    "code": role.code,
                    "name": role.name,
                    "matrix": service.role_matrix(role),
                }
            )
        return Response(service.user_matrix(request.user, getattr(request, "tenant", None)))
