"""Supplier Statistics API View."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.suppliers.permissions import CanViewSuppliers
from apps.suppliers.selectors import SupplierSelector
from apps.suppliers.serializers import SupplierStatsSerializer


class SupplierStatsView(APIView):
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext, CanViewSuppliers]

    @extend_schema(
        tags=["suppliers"],
        summary="Get supplier statistics for active tenant",
        responses={200: SupplierStatsSerializer},
    )
    def get(self, request):
        selector = SupplierSelector()
        stats_data = selector.get_supplier_stats(request.tenant)
        serializer = SupplierStatsSerializer(data=stats_data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
