"""Sequence number generator for customer returns and refunds."""

from __future__ import annotations

import logging
from typing import Any

from django.utils import timezone

from apps.sales_returns.models import CustomerRefund, CustomerReturn

logger = logging.getLogger(__name__)


class SalesReturnNumberGenerator:
    """Generates unique CRT-YYYY-XXXXXX and REF-YYYY-XXXXXX sequence document numbers."""

    def generate_return_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"CRT-{year}-"
        last = (
            CustomerReturn.objects.filter(tenant=tenant, return_number__startswith=prefix)
            .order_by("-return_number")
            .first()
        )
        if last and last.return_number:
            try:
                seq_str = last.return_number.rsplit("-", 1)[-1]
                seq = int(seq_str) + 1
            except ValueError:
                seq = 1
        else:
            seq = 1
        return f"{prefix}{seq:06d}"

    def generate_refund_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"REF-{year}-"
        last = (
            CustomerRefund.objects.filter(tenant=tenant, refund_number__startswith=prefix)
            .order_by("-refund_number")
            .first()
        )
        if last and last.refund_number:
            try:
                seq_str = last.refund_number.rsplit("-", 1)[-1]
                seq = int(seq_str) + 1
            except ValueError:
                seq = 1
        else:
            seq = 1
        return f"{prefix}{seq:06d}"
