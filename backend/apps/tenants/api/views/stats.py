"""Tenant Statistics & Resource Limits View."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.tenants.selectors import TenantSelector


class TenantStatsView(APIView):
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext]

    @extend_schema(tags=["tenants"], summary="Retrieve tenant resource stats & quota usage")
    def get(self, request):
        tenant = request.tenant
        if not tenant:
            return Response({"detail": "No tenant context."}, status=status.HTTP_400_BAD_REQUEST)
        stats = TenantSelector().get_tenant_stats(tenant)
        return Response(stats)


class TenantLimitsView(APIView):
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext]

    @extend_schema(tags=["tenants"], summary="Retrieve tenant plan resource limits")
    def get(self, request):
        tenant = request.tenant
        subscription = getattr(tenant, "subscription", None)
        limits = {
            "max_users": subscription.max_users if subscription else 5,
            "max_branches": subscription.max_branches if subscription else 1,
            "storage_limit_mb": subscription.storage_limit_mb if subscription else 1024,
            "api_rate_limit_per_min": subscription.api_rate_limit_per_min if subscription else 1000,
        }
        return Response(limits)
