"""GlobalFeatureFlag model governing platform-wide or tiered progressive rollout of new features."""

from __future__ import annotations

from typing import Any
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel


class GlobalFeatureFlag(FullAuditModel):
    """Platform-wide feature flag supporting progressive rollout percentage, whitelists, and tier targeting."""

    feature_key = models.CharField(max_length=100, unique=True, db_index=True, verbose_name=_("Feature Key"))
    name = models.CharField(max_length=150, verbose_name=_("Feature Name"))
    description = models.TextField(blank=True, default="", verbose_name=_("Feature Description"))

    is_globally_enabled = models.BooleanField(default=False, verbose_name=_("Is Globally Enabled"))
    rollout_percentage = models.IntegerField(default=0, verbose_name=_("Rollout Percentage (0-100)"))

    target_tiers = models.JSONField(default=list, blank=True, verbose_name=_("Target Subscription Tiers (e.g. ['enterprise'])"))
    whitelisted_tenants = models.JSONField(default=list, blank=True, verbose_name=_("Whitelisted Tenant Slugs/Codes"))
    blacklisted_tenants = models.JSONField(default=list, blank=True, verbose_name=_("Blacklisted Tenant Slugs/Codes"))

    class Meta:
        db_table = "platform_feature_flags"
        verbose_name = _("Global Feature Flag")
        verbose_name_plural = _("Global Feature Flags")

    def __str__(self) -> str:
        return f"{self.feature_key} [Global={self.is_globally_enabled}, Rollout={self.rollout_percentage}%]"
