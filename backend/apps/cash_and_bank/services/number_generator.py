"""Sequence number generator for Cash and Bank domain entities."""

from __future__ import annotations

import logging
from typing import Any

from django.utils import timezone

from apps.cash_and_bank.models import (
    BankReconciliation,
    BankTransaction,
    CashDeposit,
    CashMovement,
    CashTransfer,
    CashVariance,
    CashWithdrawal,
)

logger = logging.getLogger(__name__)


class TreasuryNumberGenerator:
    """Generates unique collision-safe sequence numbers for cash and bank operations."""

    def _generate_seq(self, tenant: Any, model_cls: Any, field_name: str, prefix_str: str) -> str:
        year = timezone.now().year
        prefix = f"{prefix_str}-{year}-"
        filter_kwargs = {f"{field_name}__startswith": prefix, "tenant": tenant}
        last = model_cls.objects.filter(**filter_kwargs).order_by(f"-{field_name}").first()
        if last:
            val = getattr(last, field_name, "")
            try:
                seq = int(val.rsplit("-", 1)[-1]) + 1
            except ValueError:
                seq = 1
        else:
            seq = 1
        return f"{prefix}{seq:06d}"

    def generate_deposit_number(self, tenant: Any) -> str:
        return self._generate_seq(tenant, CashDeposit, "deposit_number", "DEP")

    def generate_withdrawal_number(self, tenant: Any) -> str:
        return self._generate_seq(tenant, CashWithdrawal, "withdrawal_number", "WTH")

    def generate_transfer_number(self, tenant: Any) -> str:
        return self._generate_seq(tenant, CashTransfer, "transfer_number", "CTF")

    def generate_bank_tx_number(self, tenant: Any) -> str:
        return self._generate_seq(tenant, BankTransaction, "transaction_number", "BTX")

    def generate_reconciliation_number(self, tenant: Any) -> str:
        return self._generate_seq(tenant, BankReconciliation, "reconciliation_number", "REC")

    def generate_variance_number(self, tenant: Any) -> str:
        return self._generate_seq(tenant, CashVariance, "variance_number", "CVR")

    def generate_movement_number(self, tenant: Any) -> str:
        return self._generate_seq(tenant, CashMovement, "movement_number", "CSM")
