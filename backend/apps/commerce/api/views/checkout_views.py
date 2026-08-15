"""REST API View for Checkout operations."""

from rest_framework import permissions, status, views
from rest_framework.request import Request
from rest_framework.response import Response

from apps.commerce.api.serializers import CommerceOrderSerializer
from apps.commerce.models import Cart
from apps.commerce.services import CheckoutService
from apps.customers.models import Customer


class CheckoutViewSet(views.APIView):
    permission_classes = [permissions.AllowAny]
    checkout_service = CheckoutService()

    def post(self, request: Request) -> Response:
        cart_id = request.data.get("cart_id")
        customer_id = request.data.get("customer_id")
        shipping_addr = request.data.get("shipping_address", "")
        coupon = request.data.get("coupon_code")
        idempotency_key = request.headers.get("X-Idempotency-Key", request.data.get("idempotency_key", ""))
        rx_url = request.data.get("prescription_url")

        cart = Cart.objects.filter(pk=cart_id).first()
        customer = Customer.objects.filter(pk=customer_id).first()
        if not cart or not customer:
            return Response({"error": "Valid cart_id and customer_id required."}, status=status.HTTP_400_BAD_REQUEST)

        order = self.checkout_service.checkout_cart(
            cart,
            customer=customer,
            shipping_address=shipping_addr,
            coupon_code=coupon,
            idempotency_key=idempotency_key,
            prescription_file_url=rx_url,
        )
        return Response(CommerceOrderSerializer(order).data, status=status.HTTP_201_CREATED)
