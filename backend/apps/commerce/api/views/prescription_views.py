"""REST API ViewSet for OrderPrescription reviews."""

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.commerce.api.serializers import OrderPrescriptionSerializer
from apps.commerce.models import OrderPrescription
from apps.commerce.services import PrescriptionReviewService


class OrderPrescriptionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderPrescriptionSerializer
    queryset = OrderPrescription.objects.all()
    review_service = PrescriptionReviewService()

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request: Request, pk: str = None) -> Response:
        rx = self.get_object()
        notes = request.data.get("notes", "Approved by Pharmacist")
        self.review_service.approve_prescription(rx, pharmacist_user=request.user, notes=notes)
        return Response({"message": "Prescription approved successfully.", "status": rx.review_status}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request: Request, pk: str = None) -> Response:
        rx = self.get_object()
        reason = request.data.get("reason", "Illegible or expired prescription")
        self.review_service.reject_prescription(rx, pharmacist_user=request.user, reason=reason)
        return Response({"message": "Prescription rejected.", "status": rx.review_status}, status=status.HTTP_200_OK)
