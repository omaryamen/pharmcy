"""REST API ViewSet for SaaS Subscription management."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.saas.api.serializers import SaaSSubscriptionSerializer, SubscriptionUpgradeSerializer
from apps.saas.models import SaaSSubscription
from apps.saas.selectors import EntitlementSelector
from apps.saas.services import SubscriptionLifecycleService


class SubscriptionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SaaSSubscriptionSerializer
    selector = EntitlementSelector()
    service = SubscriptionLifecycleService()

    def get_queryset(self):
        tenant = getattr(self.request.user, "tenant", None)
        return SaaSSubscription.objects.filter(tenant=tenant).order_by("-created_at")

    @action(detail=False, methods=["get"], url_path="current")
    def current_subscription(self, request: Request) -> Response:
        tenant = getattr(request.user, "tenant", None)
        sub = self.selector.get_active_subscription(tenant)
        if not sub:
            return Response({"detail": "No active subscription found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(SaaSSubscriptionSerializer(sub).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="upgrade")
    def upgrade(self, request: Request) -> Response:
        serializer = SubscriptionUpgradeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tenant = getattr(request.user, "tenant", None)
        sub = self.selector.get_active_subscription(tenant)
        if not sub:
            return Response({"detail": "No active subscription to upgrade."}, status=status.HTTP_400_BAD_REQUEST)

        invoice = self.service.upgrade_subscription(
            sub,
            serializer.validated_data["new_plan_code"],
            actor=request.user,
        )
        return Response(
            {
                "message": "Subscription upgraded successfully.",
                "invoice_number": invoice.invoice_number,
                "amount_due": str(invoice.total_amount),
            },
            status=status.HTTP_200_OK,
        )
