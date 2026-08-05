"""Self-service endpoints: my effective permissions and navigation."""

from __future__ import annotations

from rest_framework.response import Response

from apps.common.api.viewsets import BaseAPIView
from apps.common.permissions import IsAuthenticatedAndActive

from ...services import EffectivePermissionService


class MyPermissionsView(BaseAPIView):
    """The caller's effective permissions in the current tenant."""

    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request):
        service = EffectivePermissionService()
        return Response(
            {
                "user": str(request.user.pk),
                "roles": service.assigned_roles(request.user, getattr(request, "tenant", None)),
                **service.my_permissions_payload(request.user, getattr(request, "tenant", None)),
            }
        )


class MyNavigationView(BaseAPIView):
    """Dynamic sidebar/navigation derived from the caller's permissions."""

    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request):
        service = EffectivePermissionService()
        return Response({"navigation": service.navigation(request.user, getattr(request, "tenant", None))})
