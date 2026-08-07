"""Tenant Settings ViewSet for general and domain configurations."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.response import Response

from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.tenants.permissions import CanManageTenantSettings
from apps.tenants.repositories import TenantSettingsRepository
from apps.tenants.serializers import TenantSettingsSerializer
from apps.tenants.services import TenantSettingsService


class TenantSettingsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext, CanManageTenantSettings]
    serializer_class = TenantSettingsSerializer

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.settings_repository = TenantSettingsRepository()
        self.settings_service = TenantSettingsService()

    @extend_schema(tags=["tenants"], summary="Retrieve current tenant settings")
    def retrieve(self, request):
        tenant = request.tenant
        settings_obj, _ = self.settings_repository.get_or_create(tenant=tenant)
        return Response(TenantSettingsSerializer(settings_obj).data)

    @extend_schema(tags=["tenants"], summary="Update current tenant settings")
    def partial_update(self, request):
        tenant = request.tenant
        serializer = TenantSettingsSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_settings = self.settings_service.update_settings(tenant, **serializer.validated_data)
        return Response(TenantSettingsSerializer(updated_settings).data)
