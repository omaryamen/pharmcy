"""JournalReversalService managing immutable journal reversals via compensating double-entry entries."""

from __future__ import annotations

import logging
from typing import Any

from django.db import transaction

from apps.general_ledger.exceptions import InvalidJournalStateError
from apps.general_ledger.models import JournalEntry, JournalStatus
from apps.general_ledger.services.journal_posting_service import JournalPostingService

logger = logging.getLogger(__name__)


class JournalReversalService:
    """Service layer managing immutable journal reversals with compensating entries."""

    def __init__(self, posting_service: JournalPostingService | None = None) -> None:
        self.posting_service = posting_service or JournalPostingService()

    @transaction.atomic
    def reverse_journal_entry(
        self,
        tenant: Any,
        journal_entry: JournalEntry,
        reversal_reason: str,
        *,
        user: Any | None = None,
    ) -> JournalEntry:
        """Create compensating reversal journal entry and mark original journal as REVERSED."""
        jrn = JournalEntry.objects.select_for_update().get(pk=journal_entry.pk, tenant=tenant)

        if jrn.status != JournalStatus.POSTED:
            raise InvalidJournalStateError(f"Cannot reverse journal {jrn.journal_number} in status '{jrn.status}'.")

        reversal_lines = []
        for line in jrn.lines.select_related("account").all():
            reversal_lines.append({
                "account": line.account,
                "description": f"Reversal of {jrn.journal_number}: {line.description}",
                # Inverse debits and credits
                "debit": line.credit,
                "credit": line.debit,
                "branch": line.branch,
            })

        reversal_journal = self.posting_service.create_and_post_journal_entry(
            tenant=tenant,
            company=jrn.company,
            posting_date=jrn.posting_date,
            description=f"Compensating Reversal for Journal {jrn.journal_number}. Reason: {reversal_reason}",
            lines_data=reversal_lines,
            branch=jrn.branch,
            reference_type="JOURNAL_REVERSAL",
            reference_id=str(jrn.pk),
            reference_number=jrn.journal_number,
            source_module="general_ledger",
            user=user,
        )

        jrn.status = JournalStatus.REVERSED
        jrn.save(update_fields=["status", "updated_at"])

        logger.info(f"Reversed JournalEntry {jrn.journal_number} via compensating entry {reversal_journal.journal_number}")
        return reversal_journal
