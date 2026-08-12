"""JournalPostingService orchestrating double-entry journal validation, period checks, and atomic posting."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.branches.models import Branch
from apps.companies.models import Company
from apps.general_ledger.models import (
    AccountingPeriod,
    ChartOfAccount,
    JournalEntry,
    JournalEntryLine,
    JournalStatus,
    PeriodStatus,
)
from apps.general_ledger.repositories import (
    AccountingPeriodRepository,
    ChartOfAccountRepository,
    JournalEntryRepository,
)
from apps.general_ledger.services.number_generator import GLNumberGenerator
from apps.general_ledger.validators import (
    validate_account_postable,
    validate_double_entry_balance,
    validate_period_is_open,
)

logger = logging.getLogger(__name__)


class JournalPostingService:
    """Core accounting service executing double-entry validation, period lock verification, and atomic journal posting."""

    def __init__(
        self,
        repository: JournalEntryRepository | None = None,
        period_repository: AccountingPeriodRepository | None = None,
        number_generator: GLNumberGenerator | None = None,
    ) -> None:
        self.repository = repository or JournalEntryRepository()
        self.period_repository = period_repository or AccountingPeriodRepository()
        self.number_generator = number_generator or GLNumberGenerator()

    @transaction.atomic
    def create_and_post_journal_entry(
        self,
        tenant: Any,
        company: Company,
        posting_date: Any,
        description: str,
        lines_data: list[dict[str, Any]],
        *,
        branch: Branch | None = None,
        reference_type: str = "",
        reference_id: str = "",
        reference_number: str = "",
        source_module: str = "",
        idempotency_key: str = "",
        user: Any | None = None,
    ) -> JournalEntry:
        """Create and atomically post an immutable double-entry accounting journal transaction."""
        if idempotency_key:
            existing = self.repository.find_by_idempotency_key(tenant, idempotency_key)
            if existing:
                logger.info("Found existing JournalEntry %s for idempotency_key %s", existing.journal_number, idempotency_key)
                return existing

        # Ensure active open accounting period
        period = self.period_repository.find_open_period(tenant, str(company.pk), posting_date)
        if not period:
            period, _ = AccountingPeriod.objects.get_or_create(
                tenant=tenant,
                company=company,
                fiscal_year=posting_date.year,
                period_number=posting_date.month,
                defaults={
                    "name": f"{posting_date.year}-{posting_date.month:02d}",
                    "start_date": posting_date.replace(day=1),
                    "end_date": posting_date,
                    "status": PeriodStatus.OPEN,
                },
            )
        validate_period_is_open(period)

        # Pre-validate lines and calculate totals
        total_debit = Decimal("0.0000")
        total_credit = Decimal("0.0000")

        prepared_lines = []

        for line_item in lines_data:
            acc = line_item["account"]
            if isinstance(acc, str):
                acc = ChartOfAccount.objects.get(pk=acc, tenant=tenant)

            validate_account_postable(acc)

            deb = Decimal(str(line_item.get("debit", "0.0000")))
            cred = Decimal(str(line_item.get("credit", "0.0000")))

            total_debit += deb
            total_credit += cred

            prepared_lines.append({
                "account": acc,
                "description": line_item.get("description", description),
                "debit": deb,
                "credit": cred,
                "branch": line_item.get("branch", branch),
            })

        # CRITICAL DOUBLE-ENTRY VALIDATION: Total Debits MUST Equal Total Credits
        validate_double_entry_balance(total_debit, total_credit)

        jrn_num = self.number_generator.generate_journal_number(tenant)
        now = timezone.now()

        journal = self.repository.create(
            tenant=tenant,
            company=company,
            branch=branch,
            accounting_period=period,
            journal_number=jrn_num,
            journal_date=posting_date,
            posting_date=posting_date,
            reference_type=reference_type,
            reference_id=str(reference_id),
            reference_number=reference_number,
            source_module=source_module,
            description=description,
            status=JournalStatus.POSTED,
            total_debit=total_debit,
            total_credit=total_credit,
            is_balanced=True,
            idempotency_key=idempotency_key,
            posted_at=now,
            posted_by=user,
            created_by=user,
        )

        for line_data in prepared_lines:
            JournalEntryLine.objects.create(
                tenant=tenant,
                journal_entry=journal,
                account=line_data["account"],
                description=line_data["description"],
                debit=line_data["debit"],
                credit=line_data["credit"],
                base_debit=line_data["debit"],
                base_credit=line_data["credit"],
                branch=line_data["branch"],
            )

        logger.info(f"Successfully posted double-entry JournalEntry {jrn_num} [Debits/Credits: ${total_debit}]")
        return journal
