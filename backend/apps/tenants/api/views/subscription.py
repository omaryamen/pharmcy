"""Tenant Subscription ViewSet for entitlement and quota management."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.response import Response

from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.tenants.permissions import CanManageTenantSubscription
from apps.tenants.repositories import TenantSubscriptionRepository
from apps.tenants.serializers import TenantSubscriptionSerializer
from apps.tenants.services import TenantSubscriptionService


class TenantSubscriptionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext, CanManageTenantSubscription]
    serializer_class = TenantSubscriptionSerializer

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.subscription_repository = TenantSubscriptionRepository()
        self.subscription_service = TenantSubscriptionService()

    @extend_schema(tags=["tenants"], summary="Retrieve tenant subscription and resource limits")
    def retrieve(self, request):
        tenant = request.tenant
        subscription = self.subscription_repository.get_for_tenant(tenant)
        if not subscription:
            subscription = self.subscription_repository.create(tenant=tenant)
        return Response(TenantSubscriptionSerializer(subscription).data)

    @extend_schema(tags=["tenants"], summary="Update tenant subscription plan")
    def partial_update(self, request):
        tenant = request.tenant
        serializer = TenantSubscriptionSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        plan = serializer.validated_data.get("plan", tenant.subscription_tier)
        updated = self.subscription_service.update_subscription(
            tenant,
            plan=plan,
            billing_cycle=serializer.validated_data.get("billing_cycle"),
            custom_quotas=serializer.validated_data,
        )
        return Response(TenantSubscriptionSerializer(updated).data)
