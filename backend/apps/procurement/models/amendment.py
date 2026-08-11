"""Purchase Order Amendment audit and change tracking model."""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel


class AmendmentStatus(models.TextChoices):
    PENDING_APPROVAL = "pending_approval", _("Pending Approval")
    APPROVED = "approved", _("Approved")
    REJECTED = "rejected", _("Rejected")


class PurchaseOrderAmendment(TenantAwareModel, FullAuditModel):
    """Audit log and approval workflow model for controlled Purchase Order amendments."""

    purchase_order = models.ForeignKey(
        "procurement.PurchaseOrder",
        on_delete=models.CASCADE,
        related_name="amendments",
        verbose_name=_("Purchase Order"),
        db_index=True,
    )

    amendment_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Amendment Number"))
    reason = models.TextField(verbose_name=_("Amendment Reason"))

    changed_fields = models.JSONField(default=dict, verbose_name=_("Changed Fields (Previous vs New)"))

    status = models.CharField(
        max_length=30,
        choices=AmendmentStatus.choices,
        default=AmendmentStatus.APPROVED,
        db_index=True,
        verbose_name=_("Amendment Status"),
    )

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="po_amendments_created",
        null=True,
        blank=True,
        verbose_name=_("Changed By"),
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="po_amendments_approved",
        null=True,
        blank=True,
        verbose_name=_("Approved By"),
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Approved At"))

    class Meta:
        db_table = "procurement_po_amendments"
        verbose_name = _("Purchase Order Amendment")
        verbose_name_plural = _("Purchase Order Amendments")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.amendment_number} for PO {self.purchase_order.po_number}"
