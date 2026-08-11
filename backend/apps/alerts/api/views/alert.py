"""REST API ViewSet for InventoryAlert management."""

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.alerts.api.serializers import AlertResolveSerializer, AlertScanRequestSerializer, InventoryAlertSerializer
from apps.alerts.selectors import InventoryAlertSelector
from apps.alerts.services import AlertScannerService


class InventoryAlertViewSet(viewsets.ModelViewSet):
    """API endpoints for managing inventory alerts, scans, acknowledgments, and resolutions."""

    serializer_class = InventoryAlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selector = InventoryAlertSelector()
        self.scanner_service = AlertScannerService()

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        return self.selector.list_alerts(
            tenant=tenant,
            company_id=self.request.query_params.get("company"),
            warehouse_id=self.request.query_params.get("warehouse"),
            medicine_id=self.request.query_params.get("medicine"),
            alert_type=self.request.query_params.get("alert_type"),
            severity=self.request.query_params.get("severity"),
            status=self.request.query_params.get("status"),
            search=self.request.query_params.get("search"),
        )

    @action(detail=False, methods=["post"], url_path="scan")
    def scan_inventory(self, request: Request) -> Response:
        """Trigger an on-demand scan of inventory balances and batch expiries."""
        serializer = AlertScanRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tenant = getattr(request, "tenant", None)
        res = self.scanner_service.scan_inventory_alerts(
            tenant=tenant,
            near_expiry_days=serializer.validated_data["near_expiry_days"],
            critical_expiry_days=serializer.validated_data["critical_expiry_days"],
            user=request.user,
        )
        return Response(res, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="acknowledge")
    def acknowledge(self, request: Request, pk: str = None) -> Response:
        """Acknowledge an active inventory alert."""
        tenant = getattr(request, "tenant", None)
        alert = self.selector.get_alert_by_id(tenant, pk)
        if not alert:
            return Response({"detail": "Alert not found."}, status=status.HTTP_404_NOT_FOUND)

        ack_alert = self.scanner_service.acknowledge_alert(tenant, alert, user=request.user)
        return Response(self.get_serializer(ack_alert).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="resolve")
    def resolve(self, request: Request, pk: str = None) -> Response:
        """Resolve an active or acknowledged alert."""
        tenant = getattr(request, "tenant", None)
        alert = self.selector.get_alert_by_id(tenant, pk)
        if not alert:
            return Response({"detail": "Alert not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AlertResolveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        res_alert = self.scanner_service.resolve_alert(
            tenant, alert, resolution_notes=serializer.validated_data["resolution_notes"], user=request.user
        )
        return Response(self.get_serializer(res_alert).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="statistics")
    def statistics(self, request: Request) -> Response:
        """Get operational summary statistics of active inventory alerts."""
        tenant = getattr(request, "tenant", None)
        stats = self.selector.get_alert_statistics(tenant, company_id=request.query_params.get("company"))
        return Response(stats, status=status.HTTP_200_OK)
