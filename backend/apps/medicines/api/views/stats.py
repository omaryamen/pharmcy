"""Medicine Master Catalog Statistics View."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.medicines.permissions import CanViewMedicines
from apps.medicines.selectors import MedicineSelector


class MedicineStatsView(APIView):
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext, CanViewMedicines]

    @extend_schema(tags=["medicines"], summary="Retrieve medicine master catalog statistics")
    def get(self, request):
        stats = MedicineSelector().get_medicine_stats(request.tenant)
        return Response(stats)
