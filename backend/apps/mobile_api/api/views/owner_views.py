"""REST API View for Pharmacy Owner Mobile Executive Dashboard."""

from rest_framework import permissions, status, views
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.models import Tenant
from apps.mobile_api.selectors import PharmacyOwnerMobileSelector


class PharmacyOwnerMobileDashboardView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    selector = PharmacyOwnerMobileSelector()

    def get(self, request: Request) -> Response:
        tenant = getattr(request, "tenant", None) or getattr(request.user, "tenant", None)
        if not tenant:
            tenant_id = request.query_params.get("tenant_id")
            tenant = Tenant.objects.filter(pk=tenant_id).first()

        if not tenant:
            return Response({"error": "Valid tenant context required."}, status=status.HTTP_400_BAD_REQUEST)

        dashboard = self.selector.get_owner_dashboard(tenant)
        return Response(dashboard, status=status.HTTP_200_OK)
