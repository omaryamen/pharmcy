"""Pharmaceutical Reference Statistics View."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.references.permissions import CanViewReferences
from apps.references.selectors import ReferenceSelector


class ReferenceStatsView(APIView):
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext, CanViewReferences]

    @extend_schema(tags=["references"], summary="Retrieve reference data statistics")
    def get(self, request):
        stats = ReferenceSelector().get_reference_stats(request.tenant)
        return Response(stats)
