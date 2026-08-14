"""Sequence generator for SaaS subscriptions, invoices, payments, and licenses."""

import uuid
from typing import Any
from django.utils import timezone


class SaaSNumberGenerator:
    """Collision-safe sequence generator for commercial SaaS billing entities."""

    def generate_subscription_number(self, tenant: Any) -> str:
        year = timezone.now().year
        uid = uuid.uuid4().hex[:6].upper()
        return f"SUB-{year}-{uid}"

    def generate_invoice_number(self, tenant: Any) -> str:
        year = timezone.now().year
        uid = uuid.uuid4().hex[:6].upper()
        return f"SINV-{year}-{uid}"

    def generate_payment_number(self, tenant: Any) -> str:
        year = timezone.now().year
        uid = uuid.uuid4().hex[:6].upper()
        return f"SPAY-{year}-{uid}"

    def generate_refund_number(self, tenant: Any) -> str:
        year = timezone.now().year
        uid = uuid.uuid4().hex[:6].upper()
        return f"SRFD-{year}-{uid}"

    def generate_license_number(self, tenant: Any) -> str:
        year = timezone.now().year
        uid = uuid.uuid4().hex[:6].upper()
        return f"LIC-{year}-{uid}"
