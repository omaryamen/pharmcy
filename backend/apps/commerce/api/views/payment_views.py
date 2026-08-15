"""REST API ViewSet for CommercePayment & Refunds."""

from decimal import Decimal
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.commerce.api.serializers import CommercePaymentSerializer, CommerceRefundSerializer
from apps.commerce.models import CommerceOrder, CommercePayment
from apps.commerce.services import CommercePaymentService


class CommercePaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = CommercePaymentSerializer
    queryset = CommercePayment.objects.all()
    payment_service = CommercePaymentService()

    @action(detail=False, methods=["post"], url_path="charge")
    def charge_order(self, request: Request) -> Response:
        order_id = request.data.get("order_id")
        amount = Decimal(str(request.data.get("amount", "0")))
        method = request.data.get("payment_method", "card")
        ext_tx = request.data.get("external_tx_id", "")

        order = CommerceOrder.objects.filter(pk=order_id).first()
        if not order:
            return Response({"error": "Valid order_id required."}, status=status.HTTP_400_BAD_REQUEST)

        payment = self.payment_service.process_payment(order, amount=amount, payment_method=method, external_tx_id=ext_tx)
        return Response(CommercePaymentSerializer(payment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="refund")
    def refund_payment(self, request: Request, pk: str = None) -> Response:
        payment = self.get_object()
        refund_amount = Decimal(str(request.data.get("amount", payment.amount)))
        reason = request.data.get("reason", "Customer Refund")

        refund = self.payment_service.refund_payment(payment, refund_amount=refund_amount, reason=reason)
        return Response(CommerceRefundSerializer(refund).data, status=status.HTTP_201_CREATED)
