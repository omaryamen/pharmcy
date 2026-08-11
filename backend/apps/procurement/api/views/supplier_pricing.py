"""REST API ViewSet for SupplierProductPrice management."""

from rest_framework import permissions, viewsets

from apps.procurement.api.serializers import SupplierProductPriceSerializer
from apps.procurement.selectors import SupplierProductPriceSelector


class SupplierProductPriceViewSet(viewsets.ModelViewSet):
    """API endpoints for managing supplier contract prices, lead times, and preferred suppliers."""

    serializer_class = SupplierProductPriceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selector = SupplierProductPriceSelector()

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        return self.selector.list_prices(
            tenant=tenant,
            supplier_id=self.request.query_params.get("supplier"),
            medicine_id=self.request.query_params.get("medicine"),
            is_active=True if self.request.query_params.get("is_active") == "true" else None,
        )

    def perform_create(self, serializer):
        serializer.save(tenant=getattr(self.request, "tenant", None))
