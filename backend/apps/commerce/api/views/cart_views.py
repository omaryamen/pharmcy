"""REST API ViewSet for Shopping Cart operations."""

from decimal import Decimal
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.commerce.api.serializers import CartSerializer
from apps.commerce.models import Cart, StoreProduct, TenantStore
from apps.commerce.selectors import CartSelector
from apps.commerce.services import CartService


class CartViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]
    cart_service = CartService()
    cart_selector = CartSelector()

    @action(detail=False, methods=["post"], url_path="add")
    def add_item(self, request: Request) -> Response:
        store_id = request.data.get("store_id")
        product_id = request.data.get("product_id")
        qty = Decimal(str(request.data.get("quantity", "1")))
        session_key = request.data.get("session_key", "")

        store = TenantStore.objects.filter(pk=store_id).first()
        product = StoreProduct.objects.filter(pk=product_id).first()
        if not store or not product:
            return Response({"error": "Valid store_id and product_id required."}, status=status.HTTP_400_BAD_REQUEST)

        customer = getattr(request.user, "customer_profile", None) if request.user.is_authenticated else None
        cart = self.cart_service.get_or_create_cart(store, customer=customer, session_key=session_key)
        self.cart_service.add_to_cart(cart, product, quantity=qty)

        summary = self.cart_selector.calculate_cart_summary(cart)
        return Response(summary, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request: Request) -> Response:
        cart_id = request.query_params.get("cart_id")
        cart = Cart.objects.filter(pk=cart_id).first()
        if not cart:
            return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)

        summary = self.cart_selector.calculate_cart_summary(cart)
        return Response(summary, status=status.HTTP_200_OK)
