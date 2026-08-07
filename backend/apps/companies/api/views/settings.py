"""Company Settings ViewSet."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.response import Response

from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.companies.permissions import CanManageCompany, CanViewCompany
from apps.companies.repositories import CompanyRepository, CompanySettingsRepository
from apps.companies.serializers import CompanySettingsSerializer
from apps.companies.services import CompanySettingsService


class CompanySettingsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext]
    serializer_class = CompanySettingsSerializer

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.company_repository = CompanyRepository()
        self.settings_repository = CompanySettingsRepository()
        self.settings_service = CompanySettingsService()

    def get_permissions(self):
        if self.action in {"partial_update", "update"}:
            return [(IsAuthenticatedAndActive & HasTenantContext & CanManageCompany)()]
        return [(IsAuthenticatedAndActive & HasTenantContext & CanViewCompany)()]

    @extend_schema(tags=["companies"], summary="Retrieve company settings")
    def retrieve(self, request, company_id=None):
        company = self.company_repository.get_or_none(tenant=request.tenant, pk=company_id)
        if not company:
            return Response({"detail": "Company not found."}, status=status.HTTP_404_NOT_FOUND)
        settings_obj, _ = self.settings_repository.get_or_create(company=company, defaults={"tenant": request.tenant})
        return Response(CompanySettingsSerializer(settings_obj).data)

    @extend_schema(tags=["companies"], summary="Update company settings")
    def partial_update(self, request, company_id=None):
        company = self.company_repository.get_or_none(tenant=request.tenant, pk=company_id)
        if not company:
            return Response({"detail": "Company not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CompanySettingsSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = self.settings_service.update_settings(company, **serializer.validated_data)
        return Response(CompanySettingsSerializer(updated).data)
