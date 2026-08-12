"""Sequence number generator for Accounts Receivable records, payments, adjustments, and disputes."""

from __future__ import annotations

import logging
from typing import Any

from django.utils import timezone

from apps.accounts_receivable.models import (
    CustomerPayment,
    CustomerReceivable,
    ReceivableAdjustment,
    ReceivableDispute,
    ReceivableWriteOff,
)

logger = logging.getLogger(__name__)


class ARNumberGenerator:
    """Generates unique AR-YYYY-XXXXXX, CPY-YYYY-XXXXXX, ADJ-YYYY-XXXXXX, WOF-YYYY-XXXXXX, DSP-YYYY-XXXXXX sequence numbers."""

    def generate_receivable_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"AR-{year}-"
        last = (
            CustomerReceivable.objects.filter(tenant=tenant, receivable_number__startswith=prefix)
            .order_by("-receivable_number")
            .first()
        )
        if last and last.receivable_number:
            try:
                seq = int(last.receivable_number.rsplit("-", 1)[-1]) + 1
            except ValueError:
                seq = 1
        else:
            seq = 1
        return f"{prefix}{seq:06d}"

    def generate_payment_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"CPY-{year}-"
        last = (
            CustomerPayment.objects.filter(tenant=tenant, payment_number__startswith=prefix)
            .order_by("-payment_number")
            .first()
        )
        if last and last.payment_number:
            try:
                seq = int(last.payment_number.rsplit("-", 1)[-1]) + 1
            except ValueError:
                seq = 1
        else:
            seq = 1
        return f"{prefix}{seq:06d}"

    def generate_adjustment_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"ADJ-{year}-"
        last = (
            ReceivableAdjustment.objects.filter(tenant=tenant, adjustment_number__startswith=prefix)
            .order_by("-adjustment_number")
            .first()
        )
        if last and last.adjustment_number:
            try:
                seq = int(last.adjustment_number.rsplit("-", 1)[-1]) + 1
            except ValueError:
                seq = 1
        else:
            seq = 1
        return f"{prefix}{seq:06d}"

    def generate_write_off_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"WOF-{year}-"
        last = (
            ReceivableWriteOff.objects.filter(tenant=tenant, write_off_number__startswith=prefix)
            .order_by("-write_off_number")
            .first()
        )
        if last and last.write_off_number:
            try:
                seq = int(last.write_off_number.rsplit("-", 1)[-1]) + 1
            except ValueError:
                seq = 1
        else:
            seq = 1
        return f"{prefix}{seq:06d}"

    def generate_dispute_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"DSP-{year}-"
        last = (
            ReceivableDispute.objects.filter(tenant=tenant, dispute_number__startswith=prefix)
            .order_by("-dispute_number")
            .first()
        )
        if last and last.dispute_number:
            try:
                seq = int(last.dispute_number.rsplit("-", 1)[-1]) + 1
            except ValueError:
                seq = 1
        else:
            seq = 1
        return f"{prefix}{seq:06d}"
