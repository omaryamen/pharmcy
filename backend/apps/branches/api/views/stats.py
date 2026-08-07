"""Branch Statistics View."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.branches.permissions import CanViewBranch
from apps.branches.repositories import BranchRepository
from apps.branches.selectors import BranchSelector


class BranchStatsView(APIView):
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext, CanViewBranch]

    @extend_schema(tags=["branches"], summary="Retrieve branch statistics")
    def get(self, request, branch_id=None):
        branch = BranchRepository().get_or_none(tenant=request.tenant, pk=branch_id)
        if not branch:
            return Response({"detail": "Branch not found."}, status=status.HTTP_404_NOT_FOUND)
        stats = BranchSelector().get_branch_stats(branch)
        return Response(stats)
