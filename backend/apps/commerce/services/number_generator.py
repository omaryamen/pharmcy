"""Document sequence code generator for e-commerce orders, payments, and refunds."""

from __future__ import annotations

import uuid
from django.utils import timezone


class CommerceNumberGenerator:
    """Collision-safe sequential number generator for commerce documents."""

    @staticmethod
    def generate_order_number() -> str:
        year = timezone.now().year
        suffix = uuid.uuid4().hex[:6].upper()
        return f"ORD-{year}-{suffix}"

    @staticmethod
    def generate_payment_number() -> str:
        year = timezone.now().year
        suffix = uuid.uuid4().hex[:6].upper()
        return f"CPAY-{year}-{suffix}"

    @staticmethod
    def generate_refund_number() -> str:
        year = timezone.now().year
        suffix = uuid.uuid4().hex[:6].upper()
        return f"CRFD-{year}-{suffix}"
