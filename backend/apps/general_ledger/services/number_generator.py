"""Sequence number generator for General Ledger journal entries."""

from __future__ import annotations

import logging
from typing import Any

from django.utils import timezone

from apps.general_ledger.models import JournalEntry

logger = logging.getLogger(__name__)


class GLNumberGenerator:
    """Generates unique JRN-YYYY-XXXXXX sequence numbers."""

    def generate_journal_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"JRN-{year}-"
        last = (
            JournalEntry.objects.filter(tenant=tenant, journal_number__startswith=prefix)
            .order_by("-journal_number")
            .first()
        )
        if last and last.journal_number:
            try:
                seq = int(last.journal_number.rsplit("-", 1)[-1]) + 1
            except ValueError:
                seq = 1
        else:
            seq = 1
        return f"{prefix}{seq:06d}"
