"""REST API ViewSet for Super Admin Customer Tenant Operations (Suspend, Reactivate, Impersonate)."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.models import Tenant
from apps.platform_ops.services import TenantImpersonationService, TenantLifecycleAdminService


class PlatformTenantAdminViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAdminUser]
    queryset = Tenant.objects.all()
    lifecycle_service = TenantLifecycleAdminService()
    impersonation_service = TenantImpersonationService()

    @action(detail=True, methods=["post"], url_path="suspend")
    def suspend(self, request: Request, pk: str = None) -> Response:
        tenant = self.get_object()
        reason = request.data.get("reason", "Suspended via Platform Admin")
        ip = request.META.get("REMOTE_ADDR")

        self.lifecycle_service.suspend_tenant(tenant, admin_user=request.user, reason=reason, ip_address=ip)
        return Response({"message": f"Tenant '{tenant.name}' suspended successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reactivate")
    def reactivate(self, request: Request, pk: str = None) -> Response:
        tenant = self.get_object()
        reason = request.data.get("reason", "Reactivated via Platform Admin")
        ip = request.META.get("REMOTE_ADDR")

        self.lifecycle_service.reactivate_tenant(tenant, admin_user=request.user, reason=reason, ip_address=ip)
        return Response({"message": f"Tenant '{tenant.name}' reactivated successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="impersonate")
    def impersonate(self, request: Request, pk: str = None) -> Response:
        tenant = self.get_object()
        reason = request.data.get("reason", "Customer Support Session")
        ticket = request.data.get("ticket_reference", "")
        ip = request.META.get("REMOTE_ADDR")

        log, token = self.impersonation_service.start_impersonation(
            admin_user=request.user,
            tenant=tenant,
            reason=reason,
            ticket_reference=ticket,
            ip_address=ip,
        )
        return Response(
            {
                "message": f"Impersonation session started for Tenant '{tenant.name}'",
                "impersonation_log_id": log.pk,
                "session_token": token,
            },
            status=status.HTTP_200_OK,
        )
