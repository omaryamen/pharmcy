"""Tenant settings model for configuring tenant-specific parameters."""

from __future__ import annotations

from django.db import models

from apps.common.models import FullAuditModel


def default_password_policy() -> dict:
    return {
        "min_length": 10,
        "require_digits": True,
        "require_uppercase": True,
        "require_symbols": False,
        "max_login_attempts": 5,
        "lockout_duration_minutes": 15,
    }


def default_feature_flags() -> dict:
    return {
        "enable_pos": True,
        "enable_prescriptions": True,
        "enable_inventory_batch": True,
        "enable_multi_branch": False,
        "enable_accounting": True,
        "enable_ai_forecasting": False,
    }


def default_tax_config() -> dict:
    return {
        "tax_enabled": True,
        "default_tax_rate": 15.0,
        "tax_inclusive": False,
        "tax_number": "",
    }


class TenantSettings(FullAuditModel):
    """Hierarchical and domain-specific configuration for a tenant."""

    tenant = models.OneToOneField(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="settings",
        verbose_name="Tenant",
    )
    general_settings = models.JSONField(default=dict, blank=True, verbose_name="General settings")
    localization = models.JSONField(default=dict, blank=True, verbose_name="Localization")
    tax_configuration = models.JSONField(default=default_tax_config, blank=True, verbose_name="Tax configuration")
    business_hours = models.JSONField(default=dict, blank=True, verbose_name="Business hours")
    feature_flags = models.JSONField(default=default_feature_flags, blank=True, verbose_name="Feature flags")
    password_policy = models.JSONField(default=default_password_policy, blank=True, verbose_name="Password policy")
    security_settings = models.JSONField(default=dict, blank=True, verbose_name="Security settings")
    notification_settings = models.JSONField(default=dict, blank=True, verbose_name="Notification settings")
    theme = models.JSONField(default=dict, blank=True, verbose_name="Theme & branding")

    class Meta:
        verbose_name = "Tenant Settings"
        verbose_name_plural = "Tenant Settings"

    def __str__(self) -> str:
        return f"Settings for {self.tenant.name}"
