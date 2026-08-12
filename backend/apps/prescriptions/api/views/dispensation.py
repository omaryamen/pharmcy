"""REST API ViewSet for Pharmacy Dispensing log inspection and reversals."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.prescriptions.api.serializers import PrescriptionDispenseSerializer
from apps.prescriptions.models import PrescriptionDispense
from apps.prescriptions.selectors import PrescriptionSelector
from apps.prescriptions.services import PharmacyDispensingService


class PrescriptionDispenseViewSet(viewsets.ReadOnlyModelViewSet):
    """ReadOnly ViewSet for inspecting Pharmacy Dispensing logs and executing reversals."""

    permission_classes = [IsAuthenticated]
    serializer_class = PrescriptionDispenseSerializer
    selector = PrescriptionSelector()
    service = PharmacyDispensingService()

    def get_queryset(self):
        tenant = getattr(self.request.user, "tenant", None)
        return self.selector.list_dispensations(
            tenant=tenant,
            prescription_id=self.request.query_params.get("prescription_id"),
            status=self.request.query_params.get("status"),
        )

    @action(detail=True, methods=["post"], url_path="reverse")
    def reverse(self, request: Request, pk: str = None) -> Response:
        tenant = getattr(request.user, "tenant", None)
        dispense = self.get_object()
        reason = request.data.get("reason", "")
        reversed_dispense = self.service.reverse_dispensation(tenant, dispense, pharmacist=request.user, reason=reason)
        return Response(PrescriptionDispenseSerializer(reversed_dispense).data, status=status.HTTP_200_OK)
