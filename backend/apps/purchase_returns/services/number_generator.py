"""Collision-safe sequence number generator for purchase return documents."""

from __future__ import annotations

from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.purchase_returns.models import PurchaseReturn, ReturnDiscrepancy, SupplierCreditNote


class PurchaseReturnNumberGenerator:
    """Generates sequential return (PRT-), discrepancy (DISC-), and credit note (CRN-) numbers."""

    @transaction.atomic
    def generate_return_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"PRT-{year}-"

        last_ret = (
            PurchaseReturn.objects.filter(tenant=tenant, return_number__startswith=prefix)
            .order_by("-return_number")
            .select_for_update()
            .first()
        )

        if not last_ret:
            seq = 1
        else:
            try:
                seq = int(last_ret.return_number.split("-")[-1]) + 1
            except (ValueError, IndexError):
                seq = 1

        return f"{prefix}{seq:06d}"

    @transaction.atomic
    def generate_discrepancy_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"DISC-{year}-"

        last_disc = (
            ReturnDiscrepancy.objects.filter(tenant=tenant, discrepancy_number__startswith=prefix)
            .order_by("-discrepancy_number")
            .select_for_update()
            .first()
        )

        if not last_disc:
            seq = 1
        else:
            try:
                seq = int(last_disc.discrepancy_number.split("-")[-1]) + 1
            except (ValueError, IndexError):
                seq = 1

        return f"{prefix}{seq:06d}"

    @transaction.atomic
    def generate_credit_note_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"CRN-{year}-"

        last_crn = (
            SupplierCreditNote.objects.filter(tenant=tenant, credit_note_number__startswith=prefix)
            .order_by("-credit_note_number")
            .select_for_update()
            .first()
        )

        if not last_crn:
            seq = 1
        else:
            try:
                seq = int(last_crn.credit_note_number.split("-")[-1]) + 1
            except (ValueError, IndexError):
                seq = 1

        return f"{prefix}{seq:06d}"
