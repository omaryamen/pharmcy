"""ProrationCalculatorService computing remaining vs used days for mid-cycle plan upgrades and downgrades."""

from __future__ import annotations

from decimal import Decimal
from typing import Any
from django.utils import timezone

from apps.saas.models import SaaSSubscription


class ProrationCalculatorService:
    """Service layer calculating unused subscription period credit and new plan prorated charges."""

    def calculate_proration(
        self,
        subscription: SaaSSubscription,
        new_plan_price: Decimal,
    ) -> tuple[Decimal, Decimal, Decimal]:
        """Calculate (unused_credit, new_plan_prorated_charge, net_amount_due)."""
        now = timezone.now()
        total_seconds = (subscription.current_period_end - subscription.current_period_start).total_seconds()
        remaining_seconds = (subscription.current_period_end - now).total_seconds()

        if total_seconds <= 0 or remaining_seconds <= 0:
            return Decimal("0.0000"), new_plan_price, new_plan_price

        fraction_remaining = Decimal(str(remaining_seconds / total_seconds))

        # Current price paid for remaining period
        current_price = Decimal("0.0000")
        price_obj = subscription.plan_version.prices.filter(
            billing_cycle=subscription.billing_cycle,
            currency=subscription.currency,
        ).first()
        if price_obj:
            current_price = price_obj.price_amount

        unused_credit = (current_price * fraction_remaining).quantize(Decimal("0.0001"))
        new_charge = (new_plan_price * fraction_remaining).quantize(Decimal("0.0001"))

        net_due = (new_charge - unused_credit).quantize(Decimal("0.0001"))
        if net_due < 0:
            net_due = Decimal("0.0000")

        return unused_credit, new_charge, net_due
