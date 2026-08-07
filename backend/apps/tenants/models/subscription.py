"""Tenant subscription plan and resource quota limits."""

from __future__ import annotations

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel


class SubscriptionPlan(models.TextChoices):
    TRIAL = "trial", _("Trial")
    STARTER = "starter", _("Starter")
    PROFESSIONAL = "professional", _("Professional")
    ENTERPRISE = "enterprise", _("Enterprise")


class BillingCycle(models.TextChoices):
    MONTHLY = "monthly", _("Monthly")
    ANNUAL = "annual", _("Annual")


class SubscriptionStatus(models.TextChoices):
    TRIALING = "trialing", _("Trialing")
    ACTIVE = "active", _("Active")
    PAST_DUE = "past_due", _("Past due")
    CANCELED = "canceled", _("Canceled")
    EXPIRED = "expired", _("Expired")


class TenantSubscription(FullAuditModel):
    """Entitlement plan and resource quotas bound to a tenant."""

    tenant = models.OneToOneField(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="subscription",
        verbose_name="Tenant",
    )
    plan = models.CharField(
        max_length=50,
        choices=SubscriptionPlan.choices,
        default=SubscriptionPlan.TRIAL,
        verbose_name="Plan",
    )
    billing_cycle = models.CharField(
        max_length=20,
        choices=BillingCycle.choices,
        default=BillingCycle.MONTHLY,
        verbose_name="Billing cycle",
    )
    start_date = models.DateTimeField(default=timezone.now, verbose_name="Start date")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="End date")
    is_trial = models.BooleanField(default=True, verbose_name="Is trial")
    grace_period_days = models.PositiveSmallIntegerField(default=7, verbose_name="Grace period days")
    max_users = models.PositiveIntegerField(default=5, verbose_name="Maximum users limit")
    max_branches = models.PositiveIntegerField(default=1, verbose_name="Maximum branches limit")
    storage_limit_mb = models.PositiveIntegerField(default=1024, verbose_name="Storage limit (MB)")
    api_rate_limit_per_min = models.PositiveIntegerField(default=1000, verbose_name="API rate limit per min")
    feature_limits = models.JSONField(default=dict, blank=True, verbose_name="Feature limits")
    status = models.CharField(
        max_length=30,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.TRIALING,
        db_index=True,
        verbose_name="Status",
    )

    class Meta:
        verbose_name = "Tenant Subscription"
        verbose_name_plural = "Tenant Subscriptions"

    def __str__(self) -> str:
        return f"{self.plan} for {self.tenant.name}"

    @property
    def is_active_subscription(self) -> bool:
        if self.status in {SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING}:
            if self.end_date and self.end_date < timezone.now():
                return False
            return True
        return False
