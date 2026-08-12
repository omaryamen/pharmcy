"""REST API ViewSet for AccountingPeriod management."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.general_ledger.api.serializers import AccountingPeriodSerializer, ClosePeriodSerializer
from apps.general_ledger.models import AccountingPeriod, PeriodStatus


class AccountingPeriodViewSet(viewsets.ModelViewSet):
    """ViewSet managing AccountingPeriod fiscal locks."""

    permission_classes = [IsAuthenticated]
    serializer_class = AccountingPeriodSerializer

    def get_queryset(self):
        tenant = getattr(self.request.user, "tenant", None)
        return AccountingPeriod.objects.filter(tenant=tenant)

    @action(detail=True, methods=["post"], url_path="close")
    def close_period(self, request: Request, pk: str = None) -> Response:
        period = self.get_object()
        period.status = PeriodStatus.CLOSED
        period.save(update_fields=["status", "updated_at"])
        return Response(AccountingPeriodSerializer(period).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reopen")
    def reopen_period(self, request: Request, pk: str = None) -> Response:
        period = self.get_object()
        period.status = PeriodStatus.OPEN
        period.save(update_fields=["status", "updated_at"])
        return Response(AccountingPeriodSerializer(period).data, status=status.HTTP_200_OK)
