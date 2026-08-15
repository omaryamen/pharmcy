"""REST API ViewSet for CommerceOrder tracking and management."""

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.commerce.api.serializers import CommerceOrderSerializer
from apps.commerce.models import CommerceOrder
from apps.commerce.selectors import CommerceOrderSelector
from apps.commerce.services import OrderFulfillmentService


class CommerceOrderViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = CommerceOrderSerializer
    selector = CommerceOrderSelector()
    fulfillment_service = OrderFulfillmentService()

    def get_queryset(self):
        customer_id = self.request.query_params.get("customer_id")
        if customer_id:
            return CommerceOrder.objects.filter(customer_id=customer_id)
        return CommerceOrder.objects.all()

    @action(detail=True, methods=["get"], url_path="track")
    def track_order(self, request: Request, pk: str = None) -> Response:
        order = self.get_object()
        tracking = self.selector.get_order_tracking_details(order)
        return Response(tracking, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="fulfill")
    def fulfill_order(self, request: Request, pk: str = None) -> Response:
        order = self.get_object()
        courier = request.data.get("courier_name", "PharmaExpress")
        delivery = self.fulfillment_service.fulfill_and_dispatch_order(
            order,
            courier_name=courier,
            user=request.user if request.user.is_authenticated else None,
        )
        return Response({"tracking_number": delivery.tracking_number, "status": order.status}, status=status.HTTP_200_OK)
