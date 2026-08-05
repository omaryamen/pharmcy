"""Permission catalog endpoints."""

from __future__ import annotations

from apps.common.api.viewsets import BaseModelViewSet
from apps.common.permissions import IsAuthenticatedAndActive

from ...permissions import HasPermission
from ...serializers import PermissionSerializer
from ...services import PermissionService

UUID_REGEX = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"


class PermissionViewSet(BaseModelViewSet):
    """CRUD over the global permission catalog (platform + tenant codes)."""

    service_class = PermissionService
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticatedAndActive, HasPermission]
    permission_code_prefix = "rbac.permission"
    lookup_value_regex = UUID_REGEX
