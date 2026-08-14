"""SaaSAnalyticsSelector calculating MRR, ARR, active subscription metrics, and revenue analytics."""

from __future__ import annotations

from decimal import Decimal
from typing import Any
from django.db import models
from django.db.models import Count, Sum

from apps.saas.models import (
    SaaSBillingCycle,
    SaaSInvoice,
    SaaSInvoiceStatus,
    SaaSSubscription,
    SaaSSubscriptionStatus,
)


class SaaSAnalyticsSelector:
    """Selector calculating commercial SaaS metrics: MRR, ARR, Churn, ARPU, and active plan distribution."""

    def get_saas_metrics_summary(self, *, currency: str = "USD") -> dict[str, Any]:
        """Compute key SaaS subscription performance indicators."""
        active_subs = SaaSSubscription.objects.filter(
            status__in=[SaaSSubscriptionStatus.ACTIVE, SaaSSubscriptionStatus.TRIALING],
            currency=currency,
        )

        total_active_count = active_subs.filter(status=SaaSSubscriptionStatus.ACTIVE).count()
        total_trial_count = active_subs.filter(status=SaaSSubscriptionStatus.TRIALING).count()

        # Calculate MRR (Monthly Recurring Revenue)
        mrr = Decimal("0.0000")
        for sub in active_subs.filter(status=SaaSSubscriptionStatus.ACTIVE):
            price = sub.plan_version.prices.filter(billing_cycle=sub.billing_cycle, currency=currency).first()
            if price:
                if sub.billing_cycle == SaaSBillingCycle.MONTHLY:
                    mrr += price.price_amount
                elif sub.billing_cycle == SaaSBillingCycle.ANNUAL:
                    mrr += (price.price_amount / Decimal("12.0000"))

        arr = mrr * Decimal("12.0000")

        # Total revenue paid to date
        total_revenue = SaaSInvoice.objects.filter(
            status=SaaSInvoiceStatus.PAID,
            currency=currency,
        ).aggregate(tot=Sum("total_amount"))["tot"] or Decimal("0.0000")

        arpu = (mrr / Decimal(str(total_active_count))) if total_active_count > 0 else Decimal("0.0000")

        return {
            "currency": currency,
            "mrr": float(mrr),
            "arr": float(arr),
            "arpu": float(arpu),
            "total_active_subscriptions": total_active_count,
            "total_trialing_subscriptions": total_trial_count,
            "total_historical_revenue": float(total_revenue),
        }
