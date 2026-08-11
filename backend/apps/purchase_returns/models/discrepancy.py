"""Return discrepancy tracking model."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.purchase_returns.models.enums import DiscrepancyReason


class DiscrepancyStatus(models.TextChoices):
    PENDING = "pending", _("Pending Review")
    REVIEWED = "reviewed", _("Reviewed")
    RESOLVED = "resolved", _("Resolved")


class ReturnDiscrepancy(TenantAwareModel, FullAuditModel):
    """Discrepancy record when supplier acceptance differs from dispatched return quantities."""

    purchase_return = models.ForeignKey(
        "purchase_returns.PurchaseReturn",
        on_delete=models.CASCADE,
        related_name="discrepancies",
        verbose_name=_("Purchase Return"),
        db_index=True,
    )
    return_line = models.ForeignKey(
        "purchase_returns.PurchaseReturnLine",
        on_delete=models.CASCADE,
        related_name="discrepancies",
        verbose_name=_("Return Line"),
    )

    discrepancy_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Discrepancy Number"))

    expected_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Expected Quantity"))
    dispatched_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Dispatched Quantity"))
    supplier_accepted_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Supplier Accepted Quantity"))
    supplier_rejected_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Supplier Rejected Quantity"))
    difference = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Quantity Difference"))

    reason = models.CharField(
        max_length=30,
        choices=DiscrepancyReason.choices,
        default=DiscrepancyReason.SHORTAGE,
        verbose_name=_("Discrepancy Reason"),
    )
    evidence = models.TextField(blank=True, default="", verbose_name=_("Evidence / Supplier Statement"))

    status = models.CharField(
        max_length=20,
        choices=DiscrepancyStatus.choices,
        default=DiscrepancyStatus.PENDING,
        db_index=True,
        verbose_name=_("Status"),
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="discrepancies_created",
        null=True,
        blank=True,
        verbose_name=_("Created By"),
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="discrepancies_reviewed",
        null=True,
        blank=True,
        verbose_name=_("Reviewed By"),
    )

    resolution = models.TextField(blank=True, default="", verbose_name=_("Resolution Notes"))
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Resolved At"))

    class Meta:
        db_table = "purchase_return_discrepancies"
        verbose_name = _("Return Discrepancy")
        verbose_name_plural = _("Return Discrepancies")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.discrepancy_number} - {self.reason} (Diff: {self.difference})"
