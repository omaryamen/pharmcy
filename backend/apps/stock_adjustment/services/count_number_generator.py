"""Sequence code generator for Stock Count documents."""

from __future__ import annotations

from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.stock_adjustment.models import StockCount, StockCountRecount, StockCountSession


class CountNumberGenerator:
    """Generates unique document numbers for Stock Counts, Sessions, and Recounts per tenant."""

    @transaction.atomic
    def generate_count_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"CNT-{year}-"

        last_doc = (
            StockCount.objects.filter(tenant=tenant, count_number__startswith=prefix)
            .select_for_update()
            .order_by("-count_number")
            .first()
        )

        seq = 1
        if last_doc and last_doc.count_number:
            try:
                part = last_doc.count_number.split("-")[-1]
                seq = int(part) + 1
            except (ValueError, IndexError):
                seq = 1

        return f"{prefix}{seq:06d}"

    @transaction.atomic
    def generate_session_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"SES-{year}-"

        last_doc = (
            StockCountSession.objects.filter(tenant=tenant, session_number__startswith=prefix)
            .select_for_update()
            .order_by("-session_number")
            .first()
        )

        seq = 1
        if last_doc and last_doc.session_number:
            try:
                part = last_doc.session_number.split("-")[-1]
                seq = int(part) + 1
            except (ValueError, IndexError):
                seq = 1

        return f"{prefix}{seq:06d}"

    @transaction.atomic
    def generate_recount_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"REC-{year}-"

        last_doc = (
            StockCountRecount.objects.filter(tenant=tenant, recount_number__startswith=prefix)
            .select_for_update()
            .order_by("-recount_number")
            .first()
        )

        seq = 1
        if last_doc and last_doc.recount_number:
            try:
                part = last_doc.recount_number.split("-")[-1]
                seq = int(part) + 1
            except (ValueError, IndexError):
                seq = 1

        return f"{prefix}{seq:06d}"
