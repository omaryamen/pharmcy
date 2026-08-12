"""REST API ViewSet for BankTransaction import and listing."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.cash_and_bank.api.serializers import BankTransactionSerializer, ImportBankStatementSerializer
from apps.cash_and_bank.models import BankAccount
from apps.cash_and_bank.selectors import TreasurySelector
from apps.cash_and_bank.services import BankStatementImportService


class BankTransactionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = BankTransactionSerializer
    selector = TreasurySelector()
    import_service = BankStatementImportService()

    def get_queryset(self):
        tenant = getattr(self.request.user, "tenant", None)
        return self.selector.list_bank_transactions(
            tenant=tenant,
            bank_account_id=self.request.query_params.get("bank_account_id"),
            reconciliation_status=self.request.query_params.get("reconciliation_status"),
        )

    @action(detail=False, methods=["post"], url_path="import")
    def import_statement(self, request: Request) -> Response:
        serializer = ImportBankStatementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        tenant = getattr(request.user, "tenant", None)
        bank_acc = BankAccount.objects.get(pk=data["bank_account_id"], tenant=tenant)

        lines_input = []
        for item in data["statement_lines"]:
            lines_input.append({
                "transaction_date": item["transaction_date"],
                "amount": item["amount"],
                "reference": item.get("reference", ""),
                "external_id": item.get("external_id", ""),
                "transaction_type": item.get("transaction_type", "deposit"),
                "description": item.get("description", ""),
            })

        imported = self.import_service.import_bank_transactions(
            tenant=tenant,
            bank_account=bank_acc,
            statement_lines=lines_input,
            user=request.user,
        )
        return Response(BankTransactionSerializer(imported, many=True).data, status=status.HTTP_201_CREATED)
