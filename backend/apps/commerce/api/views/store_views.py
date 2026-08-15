"""REST API ViewSet for TenantStore management."""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.commerce.api.serializers import TenantStoreSerializer
from apps.commerce.models import TenantStore


class TenantStoreViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TenantStoreSerializer

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if tenant:
            return TenantStore.objects.filter(tenant=tenant)
        return TenantStore.objects.none()
