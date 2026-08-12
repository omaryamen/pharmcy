"""BankStatementImportService executing bank statement imports with strict hash duplicate protection."""

from __future__ import annotations

import hashlib
import logging
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.cash_and_bank.exceptions import DuplicateBankImportError
from apps.cash_and_bank.models import BankAccount, BankTransaction, BankTransactionType, ReconciliationMatchStatus
from apps.cash_and_bank.services.number_generator import TreasuryNumberGenerator

logger = logging.getLogger(__name__)


class BankStatementImportService:
    """Service layer importing bank statement transactions with duplicate import protection."""

    def __init__(self, number_generator: TreasuryNumberGenerator | None = None) -> None:
        self.number_generator = number_generator or TreasuryNumberGenerator()

    @transaction.atomic
    def import_bank_transactions(
        self,
        tenant: Any,
        bank_account: BankAccount,
        statement_lines: list[dict[str, Any]],
        *,
        user: Any | None = None,
    ) -> list[BankTransaction]:
        """Import batch of bank statement lines enforcing sha256 import_hash duplicate prevention."""
        bank_acc = BankAccount.objects.select_for_update().get(pk=bank_account.pk, tenant=tenant)
        imported_records = []

        for line in statement_lines:
            tx_date = line["transaction_date"]
            val_date = line.get("value_date", tx_date)
            amount = Decimal(str(line["amount"]))
            ref = line.get("reference", "")
            ext_id = line.get("external_id", "")
            tx_type = line.get("transaction_type", BankTransactionType.DEPOSIT)
            desc = line.get("description", "")

            # Compute sha256 fingerprint hash
            raw_fingerprint = f"{bank_acc.pk}:{tx_date}:{amount}:{ref}:{ext_id}"
            import_hash = hashlib.sha256(raw_fingerprint.encode("utf-8")).hexdigest()

            # Duplicate check
            existing = BankTransaction.objects.filter(tenant=tenant, bank_account=bank_acc, import_hash=import_hash).first()
            if existing:
                logger.info(f"Skipping duplicate bank statement line {ref} (Hash: {import_hash[:8]})")
                continue

            btx_num = self.number_generator.generate_bank_tx_number(tenant)

            tx = BankTransaction.objects.create(
                tenant=tenant,
                bank_account=bank_acc,
                transaction_number=btx_num,
                external_id=ext_id,
                import_hash=import_hash,
                transaction_date=tx_date,
                value_date=val_date,
                transaction_type=tx_type,
                amount=amount,
                reference=ref,
                description=desc,
                reconciliation_status=ReconciliationMatchStatus.UNMATCHED,
                imported_at=timezone.now(),
            )
            imported_records.append(tx)

        logger.info(f"Successfully imported {len(imported_records)} bank transactions for account {bank_acc.bank_name}")
        return imported_records
