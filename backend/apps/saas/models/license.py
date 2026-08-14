"""SaaSLicense model for entitlement key verification and hybrid/cloud license identity."""

from __future__ import annotations

from typing import Any
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.saas.models.enums import SaaSLicenseStatus, SaaSLicenseType
from apps.saas.models.subscription import SaaSSubscription


class SaaSLicense(TenantAwareModel, FullAuditModel):
    """Authoritative commercial license record bound to a tenant subscription."""

    license_number = models.CharField(max_length=60, db_index=True, verbose_name=_("License Number (LIC)"))
    license_key = models.CharField(max_length=255, unique=True, db_index=True, verbose_name=_("Secure License Key"))

    subscription = models.OneToOneField(
        SaaSSubscription,
        on_delete=models.CASCADE,
        related_name="license",
        verbose_name=_("Associated SaaS Subscription"),
    )

    license_type = models.CharField(
        max_length=30,
        choices=SaaSLicenseType.choices,
        default=SaaSLicenseType.SUBSCRIPTION,
        verbose_name=_("License Type"),
    )

    status = models.CharField(
        max_length=30,
        choices=SaaSLicenseStatus.choices,
        default=SaaSLicenseStatus.ACTIVE,
        db_index=True,
        verbose_name=_("License Status"),
    )

    issued_at = models.DateTimeField(default=timezone.now, verbose_name=_("Issued Timestamp"))
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Expiry Timestamp"))

    entitlements_snapshot = models.JSONField(default=dict, blank=True, verbose_name=_("Entitlements Snapshot JSON"))

    class Meta:
        db_table = "saas_licenses"
        verbose_name = _("SaaS License")
        verbose_name_plural = _("SaaS Licenses")

    def __str__(self) -> str:
        return f"{self.license_number} - {self.tenant.name} [{self.license_type} / {self.status}]"

    @property
    def is_valid(self) -> bool:
        if self.status in {SaaSLicenseStatus.ACTIVE, SaaSLicenseStatus.TRIAL}:
            if self.expires_at and self.expires_at < timezone.now():
                return False
            return True
        return False
