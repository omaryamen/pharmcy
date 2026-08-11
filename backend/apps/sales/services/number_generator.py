"""Collision-safe sequence number generator for sales and POS documents."""

from __future__ import annotations

from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.sales.models import CashRegister, RegisterSession, SalesInvoice, SalesPayment


class SalesNumberGenerator:
    """Generates sequential invoice (INV-), payment (PAY-), register (REG-), and session (SES-) numbers."""

    @transaction.atomic
    def generate_invoice_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"INV-{year}-"

        last_inv = (
            SalesInvoice.objects.filter(tenant=tenant, invoice_number__startswith=prefix)
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
    def generate_payment_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"PAY-{year}-"

        last_pmt = (
            SalesPayment.objects.filter(tenant=tenant, payment_number__startswith=prefix)
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
    def generate_register_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"REG-{year}-"

        last_reg = (
            CashRegister.objects.filter(tenant=tenant, register_number__startswith=prefix)
            .order_by("-register_number")
            .select_for_update()
            .first()
        )

        if not last_reg:
            seq = 1
        else:
            try:
                seq = int(last_reg.register_number.split("-")[-1]) + 1
            except (ValueError, IndexError):
                seq = 1

        return f"{prefix}{seq:06d}"

    @transaction.atomic
    def generate_session_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"SES-{year}-"

        last_ses = (
            RegisterSession.objects.filter(tenant=tenant, session_number__startswith=prefix)
            .order_by("-session_number")
            .select_for_update()
            .first()
        )

        if not last_ses:
            seq = 1
        else:
            try:
                seq = int(last_ses.session_number.split("-")[-1]) + 1
            except (ValueError, IndexError):
                seq = 1

        return f"{prefix}{seq:06d}"
