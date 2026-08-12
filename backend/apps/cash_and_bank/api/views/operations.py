"""REST API ViewSets for Treasury cash deposits, withdrawals, and transfers."""

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.cash_and_bank.api.serializers import (
    CashDepositSerializer,
    CashTransferSerializer,
    CashWithdrawalSerializer,
    CreateDepositSerializer,
    CreateWithdrawalSerializer,
)
from apps.cash_and_bank.models import BankAccount, CashAccount, CashDeposit, CashTransfer, CashWithdrawal
from apps.cash_and_bank.services import TreasuryOperationsService
from apps.companies.models import Company


class CashDepositViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CashDepositSerializer
    service = TreasuryOperationsService()

    def get_queryset(self):
        tenant = getattr(self.request.user, "tenant", None)
        return CashDeposit.objects.filter(tenant=tenant)

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = CreateDepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        tenant = getattr(request.user, "tenant", None)
        company = Company.objects.get(pk=data["company_id"], tenant=tenant)
        cash_acc = CashAccount.objects.get(pk=data["cash_account_id"], tenant=tenant)
        bank_acc = BankAccount.objects.get(pk=data["bank_account_id"], tenant=tenant)

        deposit = self.service.create_cash_deposit(
            tenant=tenant,
            company=company,
            cash_account=cash_acc,
            bank_account=bank_acc,
            amount=data["amount"],
            reference=data.get("reference", ""),
            user=request.user,
        )
        return Response(CashDepositSerializer(deposit).data, status=status.HTTP_201_CREATED)


class CashWithdrawalViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CashWithdrawalSerializer
    service = TreasuryOperationsService()

    def get_queryset(self):
        tenant = getattr(self.request.user, "tenant", None)
        return CashWithdrawal.objects.filter(tenant=tenant)

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = CreateWithdrawalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        tenant = getattr(request.user, "tenant", None)
        company = Company.objects.get(pk=data["company_id"], tenant=tenant)
        bank_acc = BankAccount.objects.get(pk=data["bank_account_id"], tenant=tenant)
        cash_acc = CashAccount.objects.get(pk=data["cash_account_id"], tenant=tenant)

        withdrawal = self.service.create_cash_withdrawal(
            tenant=tenant,
            company=company,
            bank_account=bank_acc,
            cash_account=cash_acc,
            amount=data["amount"],
            purpose=data.get("purpose", ""),
            reference=data.get("reference", ""),
            user=request.user,
        )
        return Response(CashWithdrawalSerializer(withdrawal).data, status=status.HTTP_201_CREATED)


class CashTransferViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CashTransferSerializer

    def get_queryset(self):
        tenant = getattr(self.request.user, "tenant", None)
        return CashTransfer.objects.filter(tenant=tenant)
