"""Collision-safe sequence number generator for accounts payable documents."""

from __future__ import annotations

from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.accounts_payable.models import (
    AccountsPayableEntry,
    InvoiceDispute,
    SupplierInvoice,
    SupplierPayment,
)


class AccountsPayableNumberGenerator:
    """Generates sequential invoice (INV-), AP entry (AP-), payment (PAY-), and dispute (DISP-) numbers."""

    @transaction.atomic
    def generate_invoice_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"INV-{year}-"

        last_inv = (
            SupplierInvoice.objects.filter(tenant=tenant, invoice_number__startswith=prefix)
            .order_by("-invoice_number")
            .select_for_update()
            .first()
        )

        if not last_inv:
            seq = 1
        else:
            try:
                seq = int(last_inv.invoice_number.split("-")[-1]) + 1
            except (ValueError, IndexError):
                seq = 1

        return f"{prefix}{seq:06d}"

    @transaction.atomic
    def generate_payable_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"AP-{year}-"

        last_ap = (
            AccountsPayableEntry.objects.filter(tenant=tenant, payable_number__startswith=prefix)
            .order_by("-payable_number")
            .select_for_update()
            .first()
        )

        if not last_ap:
            seq = 1
        else:
            try:
                seq = int(last_ap.payable_number.split("-")[-1]) + 1
            except (ValueError, IndexError):
                seq = 1

        return f"{prefix}{seq:06d}"

    @transaction.atomic
    def generate_payment_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"PAY-{year}-"

        last_pmt = (
            SupplierPayment.objects.filter(tenant=tenant, payment_number__startswith=prefix)
            .order_by("-payment_number")
            .select_for_update()
            .first()
        )

        if not last_pmt:
            seq = 1
        else:
            try:
                seq = int(last_pmt.payment_number.split("-")[-1]) + 1
            except (ValueError, IndexError):
                seq = 1

        return f"{prefix}{seq:06d}"

    @transaction.atomic
    def generate_dispute_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"DISP-{year}-"

        last_disp = (
            InvoiceDispute.objects.filter(tenant=tenant, dispute_number__startswith=prefix)
            .order_by("-dispute_number")
            .select_for_update()
            .first()
        )

        if not last_disp:
            seq = 1
        else:
            try:
                seq = int(last_disp.dispute_number.split("-")[-1]) + 1
            except (ValueError, IndexError):
                seq = 1

        return f"{prefix}{seq:06d}"
