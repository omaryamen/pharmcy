"""REST API ViewSet for ExpenseRequest workflow."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.expenses.api.serializers import ExpenseRequestSerializer
from apps.expenses.models import ExpenseRequest, RequestStatus
from apps.expenses.services import ExpenseNumberGenerator


class ExpenseRequestViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ExpenseRequestSerializer
    number_generator = ExpenseNumberGenerator()

    def get_queryset(self):
        tenant = getattr(self.request.user, "tenant", None)
        return ExpenseRequest.objects.filter(tenant=tenant)

    def perform_create(self, serializer):
        tenant = getattr(self.request.user, "tenant", None)
        req_num = self.number_generator.generate_request_number(tenant)
        serializer.save(
            tenant=tenant,
            request_number=req_num,
            requester=self.request.user,
            created_by=self.request.user,
        )

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request: Request, pk: str = None) -> Response:
        req_obj = self.get_object()
        req_obj.status = RequestStatus.APPROVED
        req_obj.approved_by = request.user
        req_obj.save()
        return Response(ExpenseRequestSerializer(req_obj).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request: Request, pk: str = None) -> Response:
        req_obj = self.get_object()
        req_obj.status = RequestStatus.REJECTED
        req_obj.rejected_by = request.user
        req_obj.approval_notes = request.data.get("notes", "")
        req_obj.save()
        return Response(ExpenseRequestSerializer(req_obj).data, status=status.HTTP_200_OK)
