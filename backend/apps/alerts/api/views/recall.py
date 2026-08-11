"""REST API ViewSet for BatchRecall management."""

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.alerts.api.serializers import BatchRecallSerializer, RecallCompleteSerializer, RecallInitiateSerializer
from apps.alerts.selectors import BatchRecallSelector
from apps.alerts.services import BatchRecallService


class BatchRecallViewSet(viewsets.ModelViewSet):
    """API endpoints for managing pharmaceutical batch recall orders and automated quarantining."""

    serializer_class = BatchRecallSerializer
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selector = BatchRecallSelector()
        self.recall_service = BatchRecallService()

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        return self.selector.list_recalls(
            tenant=tenant,
            company_id=self.request.query_params.get("company"),
            medicine_id=self.request.query_params.get("medicine"),
            batch_id=self.request.query_params.get("batch"),
            recall_class=self.request.query_params.get("recall_class"),
            status=self.request.query_params.get("status"),
            search=self.request.query_params.get("search"),
        )

    def perform_create(self, serializer):
        tenant = getattr(self.request, "tenant", None)
        recall = self.recall_service.create_recall(
            tenant=tenant,
            company=serializer.validated_data["company"],
            medicine=serializer.validated_data["medicine"],
            batch=serializer.validated_data["batch"],
            reason=serializer.validated_data["reason"],
            recall_type=serializer.validated_data.get("recall_type"),
            recall_class=serializer.validated_data.get("recall_class"),
            action_required=serializer.validated_data.get("action_required", ""),
            regulatory_reference=serializer.validated_data.get("regulatory_reference", ""),
            user=self.request.user,
        )
        serializer.instance = recall

    @action(detail=True, methods=["post"], url_path="initiate")
    def initiate(self, request: Request, pk: str = None) -> Response:
        """Initiate recall order and trigger automatic batch stock quarantine."""
        tenant = getattr(request, "tenant", None)
        recall = self.selector.get_recall_by_id(tenant, pk)
        if not recall:
            return Response({"detail": "Recall order not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RecallInitiateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        initiated = self.recall_service.initiate_recall(
            tenant=tenant,
            recall=recall,
            auto_quarantine=serializer.validated_data["auto_quarantine"],
            user=request.user,
        )
        return Response(self.get_serializer(initiated).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="quarantine")
    def quarantine_stock(self, request: Request, pk: str = None) -> Response:
        """Execute automated stock quarantine for recalled batch."""
        tenant = getattr(request, "tenant", None)
        recall = self.selector.get_recall_by_id(tenant, pk)
        if not recall:
            return Response({"detail": "Recall order not found."}, status=status.HTTP_404_NOT_FOUND)

        qty_quarantined = self.recall_service.auto_quarantine_stock(tenant=tenant, recall=recall, user=request.user)
        return Response({"quarantined_quantity": str(qty_quarantined)}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="complete")
    def complete(self, request: Request, pk: str = None) -> Response:
        """Finalize and close recall order."""
        tenant = getattr(request, "tenant", None)
        recall = self.selector.get_recall_by_id(tenant, pk)
        if not recall:
            return Response({"detail": "Recall order not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RecallCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        completed = self.recall_service.complete_recall(
            tenant=tenant,
            recall=recall,
            disposed_quantity=serializer.validated_data["disposed_quantity"],
            returned_quantity=serializer.validated_data["returned_quantity"],
            user=request.user,
        )
        return Response(self.get_serializer(completed).data, status=status.HTTP_200_OK)
