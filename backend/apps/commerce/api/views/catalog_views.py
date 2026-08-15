"""REST API ViewSet for StoreProduct public catalog & search."""

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.commerce.api.serializers import StoreProductSerializer
from apps.commerce.models import StoreProduct, TenantStore
from apps.commerce.selectors import StoreCatalogSelector


class StoreProductViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = StoreProductSerializer
    selector = StoreCatalogSelector()

    def get_queryset(self):
        store_id = self.request.query_params.get("store_id")
        if store_id:
            return StoreProduct.objects.filter(store_id=store_id, is_published=True)
        return StoreProduct.objects.filter(is_published=True)

    @action(detail=False, methods=["get"], url_path="search")
    def search_catalog(self, request: Request) -> Response:
        store_id = request.query_params.get("store_id")
        query = request.query_params.get("q", "")
        category_id = request.query_params.get("category_id")

        store = TenantStore.objects.filter(pk=store_id).first()
        if not store:
            return Response({"error": "store_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        results = self.selector.list_published_products(
            store,
            category_id=category_id,
            search_query=query,
        )
        return Response(results, status=status.HTTP_200_OK)
