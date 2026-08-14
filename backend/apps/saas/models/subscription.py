"""SaaSSubscription model tracking tenant subscriptions, lifecycle states, and renewals."""

from __future__ import annotations

from typing import Any
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.saas.models.enums import SaaSBillingCycle, SaaSSubscriptionStatus
from apps.saas.models.plan import Plan, PlanVersion


class SaaSSubscription(TenantAwareModel, FullAuditModel):
    """Authoritative commercial subscription record for a SaaS tenant."""

    subscription_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Subscription Number (SUB)"))

    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name="subscriptions",
        verbose_name=_("Subscribed Plan"),
    )

    plan_version = models.ForeignKey(
        PlanVersion,
        on_delete=models.PROTECT,
        related_name="subscriptions",
        verbose_name=_("Subscribed Plan Version"),
    )

    status = models.CharField(
        max_length=30,
        choices=SaaSSubscriptionStatus.choices,
        default=SaaSSubscriptionStatus.TRIALING,
        db_index=True,
        verbose_name=_("Subscription Status"),
    )

    billing_cycle = models.CharField(
        max_length=20,
        choices=SaaSBillingCycle.choices,
        default=SaaSBillingCycle.MONTHLY,
        verbose_name=_("Billing Cycle"),
    )

    currency = models.CharField(max_length=3, default="USD", verbose_name=_("Currency Code"))

    start_date = models.DateTimeField(default=timezone.now, verbose_name=_("Start Date"))
    trial_start = models.DateTimeField(null=True, blank=True, verbose_name=_("Trial Start Date"))
    trial_end = models.DateTimeField(null=True, blank=True, verbose_name=_("Trial End Date"))

    current_period_start = models.DateTimeField(default=timezone.now, verbose_name=_("Current Period Start"))
    current_period_end = models.DateTimeField(verbose_name=_("Current Period End"))
    next_billing_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Next Billing Date"))

    cancel_at_period_end = models.BooleanField(default=False, verbose_name=_("Cancel At Period End"))
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Cancelled At"))
    cancellation_reason = models.TextField(blank=True, default="", verbose_name=_("Cancellation Reason"))

    grace_period_end = models.DateTimeField(null=True, blank=True, verbose_name=_("Grace Period End"))
    external_provider_id = models.CharField(max_length=150, blank=True, default="", verbose_name=_("External Provider Sub ID"))

    metadata = models.JSONField(default=dict, blank=True, verbose_name=_("Subscription Metadata"))

    class Meta:
        db_table = "saas_subscriptions"
        verbose_name = _("SaaS Subscription")
        verbose_name_plural = _("SaaS Subscriptions")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.subscription_number} - {self.tenant.name} [{self.plan.code} / {self.status}]"

    @property
    def is_active_entitled(self) -> bool:
        """Return True if subscription is currently entitled to feature access."""
        if self.status in {SaaSSubscriptionStatus.ACTIVE, SaaSSubscriptionStatus.TRIALING, SaaSSubscriptionStatus.GRACE_PERIOD}:
            if self.current_period_end and self.current_period_end < timezone.now() and self.status != SaaSSubscriptionStatus.GRACE_PERIOD:
                return False
            return True
        return False
