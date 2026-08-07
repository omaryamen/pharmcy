"""Tenant Profile ViewSet for self-service profile management."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.response import Response

from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.tenants.models import TenantProfile
from apps.tenants.permissions import CanManageTenantSettings
from apps.tenants.repositories import TenantProfileRepository
from apps.tenants.serializers import TenantProfileSerializer


class TenantProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext, CanManageTenantSettings]
    serializer_class = TenantProfileSerializer

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.profile_repository = TenantProfileRepository()

    @extend_schema(tags=["tenants"], summary="Retrieve current tenant profile")
    def retrieve(self, request):
        tenant = request.tenant
        profile, _ = self.profile_repository.get_or_create(tenant=tenant, defaults={"legal_name": tenant.name})
        return Response(TenantProfileSerializer(profile).data)

    @extend_schema(tags=["tenants"], summary="Update current tenant profile")
    def partial_update(self, request):
        tenant = request.tenant
        profile, _ = self.profile_repository.get_or_create(tenant=tenant, defaults={"legal_name": tenant.name})
        serializer = TenantProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
