"""Company Statistics View."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.companies.permissions import CanViewCompany
from apps.companies.repositories import CompanyRepository
from apps.companies.selectors import CompanySelector


class CompanyStatsView(APIView):
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext, CanViewCompany]

    @extend_schema(tags=["companies"], summary="Retrieve company statistics")
    def get(self, request, company_id=None):
        company = CompanyRepository().get_or_none(tenant=request.tenant, pk=company_id)
        if not company:
            return Response({"detail": "Company not found."}, status=status.HTTP_404_NOT_FOUND)
        stats = CompanySelector().get_company_stats(company)
        return Response(stats)
