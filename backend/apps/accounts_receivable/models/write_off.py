"""ReceivableWriteOff domain model."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel


class ReceivableWriteOff(TenantAwareModel, FullAuditModel):
    """Record of formal uncollectible bad debt write-off."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="ar_write_offs",
        verbose_name=_("Company"),
        db_index=True,
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="ar_write_offs",
        verbose_name=_("Customer"),
        db_index=True,
    )
    receivable = models.ForeignKey(
        "accounts_receivable.CustomerReceivable",
        on_delete=models.CASCADE,
        related_name="write_offs",
        verbose_name=_("Receivable"),
        db_index=True,
    )

    write_off_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Write-Off Number (WOF)"))
    amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Write-Off Amount"))
    reason = models.TextField(verbose_name=_("Write-Off Reason / Justification"))

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_ar_write_offs",
        null=True,
        blank=True,
        verbose_name=_("Approved By Finance Manager"),
    )

    class Meta:
        db_table = "receivable_write_offs"
        verbose_name = _("Receivable Write-Off")
        verbose_name_plural = _("Receivable Write-Offs")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "write_off_number"],
                name="ar_write_off_tenant_number_uniq",
            )
        ]
