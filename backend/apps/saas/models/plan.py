"""Plan, PlanVersion, PlanFeature, PlanPrice, and AddOn models for SaaS monetization."""

from __future__ import annotations

from typing import Any
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel
from apps.saas.models.enums import SaaSBillingCycle


class Plan(FullAuditModel):
    """SaaS Plan Definition (e.g., Starter, Professional, Enterprise)."""

    code = models.CharField(max_length=60, unique=True, db_index=True, verbose_name=_("Plan Code"))
    name = models.CharField(max_length=150, verbose_name=_("Plan Name"))
    description = models.TextField(blank=True, default="", verbose_name=_("Plan Description"))

    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    is_public = models.BooleanField(default=True, verbose_name=_("Is Publicly Available"))
    sort_order = models.IntegerField(default=0, verbose_name=_("Display Sort Order"))

    class Meta:
        db_table = "saas_plans"
        verbose_name = _("SaaS Plan")
        verbose_name_plural = _("SaaS Plans")
        ordering = ["sort_order", "code"]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class PlanVersion(FullAuditModel):
    """Immutable versioning for plans to preserve historical subscription entitlements."""

    plan = models.ForeignKey(
        Plan,
        on_delete=models.CASCADE,
        related_name="versions",
        verbose_name=_("SaaS Plan"),
    )
    version_number = models.IntegerField(default=1, verbose_name=_("Version Number"))
    effective_date = models.DateTimeField(default=timezone.now, verbose_name=_("Effective Date"))
    is_current = models.BooleanField(default=True, verbose_name=_("Is Current Active Version"))

    class Meta:
        db_table = "saas_plan_versions"
        verbose_name = _("Plan Version")
        verbose_name_plural = _("Plan Versions")
        constraints = [
            models.UniqueConstraint(
                fields=["plan", "version_number"],
                name="saas_plan_version_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.plan.code} v{self.version_number}"


class PlanFeature(FullAuditModel):
    """Entitlement feature or limit bound to a plan version."""

    plan_version = models.ForeignKey(
        PlanVersion,
        on_delete=models.CASCADE,
        related_name="features",
        verbose_name=_("Plan Version"),
    )

    feature_key = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name=_("Feature Key (e.g. max_users, max_branches, advanced_reports)"),
    )

    feature_name = models.CharField(max_length=150, verbose_name=_("Feature Name"))
    is_enabled = models.BooleanField(default=True, verbose_name=_("Is Feature Enabled"))
    limit_value = models.IntegerField(default=-1, verbose_name=_("Limit Value (-1 for Unlimited)"))
    metadata = models.JSONField(default=dict, blank=True, verbose_name=_("Feature Metadata"))

    class Meta:
        db_table = "saas_plan_features"
        verbose_name = _("Plan Feature")
        verbose_name_plural = _("Plan Features")
        constraints = [
            models.UniqueConstraint(
                fields=["plan_version", "feature_key"],
                name="saas_plan_ver_feature_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.plan_version} -> {self.feature_key} (Limit={self.limit_value})"


class PlanPrice(FullAuditModel):
    """Multi-currency & multi-cycle pricing for plan versions."""

    plan_version = models.ForeignKey(
        PlanVersion,
        on_delete=models.CASCADE,
        related_name="prices",
        verbose_name=_("Plan Version"),
    )

    billing_cycle = models.CharField(
        max_length=20,
        choices=SaaSBillingCycle.choices,
        default=SaaSBillingCycle.MONTHLY,
        verbose_name=_("Billing Cycle"),
    )

    currency = models.CharField(max_length=3, default="USD", verbose_name=_("Currency Code"))
    price_amount = models.DecimalField(max_digits=12, decimal_places=4, verbose_name=_("Recurring Price Amount"))
    setup_fee = models.DecimalField(max_digits=12, decimal_places=4, default=0, verbose_name=_("One-Time Setup Fee"))

    effective_from = models.DateTimeField(default=timezone.now, verbose_name=_("Effective From"))
    effective_until = models.DateTimeField(null=True, blank=True, verbose_name=_("Effective Until"))

    class Meta:
        db_table = "saas_plan_prices"
        verbose_name = _("Plan Price")
        verbose_name_plural = _("Plan Prices")

    def __str__(self) -> str:
        return f"{self.plan_version} - {self.billing_cycle}: {self.price_amount} {self.currency}"


class AddOn(FullAuditModel):
    """Optional recurring or one-time add-on features available for purchase."""

    code = models.CharField(max_length=60, unique=True, db_index=True, verbose_name=_("Add-On Code"))
    name = models.CharField(max_length=150, verbose_name=_("Add-On Name"))
    feature_key = models.CharField(max_length=100, verbose_name=_("Granted Feature Key"))
    grant_amount = models.IntegerField(default=1, verbose_name=_("Granted Limit Quantity"))

    price_amount = models.DecimalField(max_digits=12, decimal_places=4, verbose_name=_("Price Amount"))
    currency = models.CharField(max_length=3, default="USD", verbose_name=_("Currency Code"))
    billing_cycle = models.CharField(
        max_length=20,
        choices=SaaSBillingCycle.choices,
        default=SaaSBillingCycle.MONTHLY,
        verbose_name=_("Billing Cycle"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    class Meta:
        db_table = "saas_add_ons"
        verbose_name = _("Add-On")
        verbose_name_plural = _("Add-Ons")

    def __str__(self) -> str:
        return f"{self.name} (+{self.grant_amount} {self.feature_key}): {self.price_amount} {self.currency}"
