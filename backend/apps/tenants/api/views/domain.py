"""Tenant Domain ViewSet for custom domain and subdomain routing management."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.tenants.permissions import CanManageTenantSettings
from apps.tenants.repositories import TenantDomainRepository
from apps.tenants.serializers import TenantDomainSerializer
from apps.tenants.services import TenantDomainService


class TenantDomainViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext, CanManageTenantSettings]
    serializer_class = TenantDomainSerializer

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.domain_repository = TenantDomainRepository()
        self.domain_service = TenantDomainService()

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if not tenant:
            return self.domain_repository.model.objects.none()
        return self.domain_repository.filter(tenant=tenant)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        domain = self.domain_service.add_domain(
            tenant=request.tenant,
            domain_name=serializer.validated_data["domain_name"],
            domain_type=serializer.validated_data.get("domain_type", "custom"),
            is_primary=serializer.validated_data.get("is_primary", False),
        )
        return Response(TenantDomainSerializer(domain).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="verify")
    def verify(self, request, pk=None):
        domain = self.domain_service.verify_domain(request.tenant, pk)
        return Response(TenantDomainSerializer(domain).data)

    @action(detail=True, methods=["post"], url_path="set-primary")
    def set_primary(self, request, pk=None):
        domain = self.domain_service.set_primary_domain(request.tenant, pk)
        return Response(TenantDomainSerializer(domain).data)

    def destroy(self, request, *args, **kwargs):
        self.domain_service.remove_domain(request.tenant, kwargs.get("pk"))
        return Response(status=status.HTTP_204_NO_CONTENT)
