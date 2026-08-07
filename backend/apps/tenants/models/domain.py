"""Domain routing and custom domain mapping for tenants."""

from __future__ import annotations

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel


class DomainType(models.TextChoices):
    PRIMARY = "primary", _("Primary")
    SUBDOMAIN = "subdomain", _("Subdomain")
    CUSTOM = "custom", _("Custom")


class SSLStatus(models.TextChoices):
    PENDING = "pending", _("Pending")
    ACTIVE = "active", _("Active")
    FAILED = "failed", _("Failed")


class TenantDomain(FullAuditModel):
    """Host domain mapping and custom domain verification for a tenant."""

    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="domains",
        verbose_name="Tenant",
    )
    domain_name = models.CharField(max_length=255, unique=True, db_index=True, verbose_name="Domain name")
    domain_type = models.CharField(
        max_length=30,
        choices=DomainType.choices,
        default=DomainType.SUBDOMAIN,
        verbose_name="Domain type",
    )
    is_verified = models.BooleanField(default=False, db_index=True, verbose_name="Is verified")
    ssl_status = models.CharField(
        max_length=30,
        choices=SSLStatus.choices,
        default=SSLStatus.PENDING,
        verbose_name="SSL status",
    )
    verification_token = models.CharField(max_length=64, blank=True, default="", verbose_name="Verification token")
    is_primary = models.BooleanField(default=False, verbose_name="Is primary domain")

    class Meta:
        ordering = ["-is_primary", "domain_name"]
        verbose_name = "Tenant Domain"
        verbose_name_plural = "Tenant Domains"

    def __str__(self) -> str:
        return f"{self.domain_name} ({self.tenant.name})"

    def save(self, *args, **kwargs) -> None:
        if not self.verification_token:
            self.verification_token = uuid.uuid4().hex
        if self.is_primary:
            TenantDomain.objects.filter(tenant=self.tenant, is_primary=True).exclude(pk=self.pk).update(
                is_primary=False
            )
        super().save(*args, **kwargs)
