"""Purchase Requisition header and line models."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.procurement.models.enums import ProcurementPriority, ProcurementReason, RequisitionStatus


class PurchaseRequisition(TenantAwareModel, FullAuditModel):
    """Header record for internal purchase requests prior to PO creation."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="purchase_requisitions",
        verbose_name=_("Company"),
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="purchase_requisitions",
        null=True,
        blank=True,
        verbose_name=_("Branch"),
    )
    warehouse = models.ForeignKey(
        "warehouses.Warehouse",
        on_delete=models.CASCADE,
        related_name="purchase_requisitions",
        verbose_name=_("Target Warehouse"),
        db_index=True,
    )

    requisition_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Requisition Number"))
    department = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Department"))

    priority = models.CharField(
        max_length=20,
        choices=ProcurementPriority.choices,
        default=ProcurementPriority.NORMAL,
        verbose_name=_("Priority"),
    )
    reason = models.CharField(
        max_length=40,
        choices=ProcurementReason.choices,
        default=ProcurementReason.REGULAR_REPLENISHMENT,
        verbose_name=_("Requisition Reason"),
    )
    status = models.CharField(
        max_length=30,
        choices=RequisitionStatus.choices,
        default=RequisitionStatus.DRAFT,
        db_index=True,
        verbose_name=_("Requisition Status"),
    )

    required_date = models.DateField(null=True, blank=True, verbose_name=_("Required Date"))

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="requested_requisitions",
        null=True,
        blank=True,
        verbose_name=_("Requested By"),
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_requisitions",
        null=True,
        blank=True,
        verbose_name=_("Approved By"),
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Approved At"))

    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="rejected_requisitions",
        null=True,
        blank=True,
        verbose_name=_("Rejected By"),
    )
    rejected_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Rejected At"))
    rejection_reason = models.TextField(blank=True, default="", verbose_name=_("Rejection Reason"))

    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))
    total_estimated_cost = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Total Estimated Cost"))

    class Meta:
        db_table = "procurement_requisitions"
        verbose_name = _("Purchase Requisition")
        verbose_name_plural = _("Purchase Requisitions")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "requisition_number"],
                name="purchase_requisition_tenant_number_uniq",
            )
        ]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "warehouse"]),
        ]

    def __str__(self) -> str:
        return f"{self.requisition_number} ({self.status})"


class PurchaseRequisitionLine(TenantAwareModel, FullAuditModel):
    """Line item for individual medicine request inside a PurchaseRequisition."""

    requisition = models.ForeignKey(
        PurchaseRequisition,
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name=_("Purchase Requisition"),
        db_index=True,
    )
    medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.PROTECT,
        related_name="requisition_lines",
        verbose_name=_("Medicine"),
        db_index=True,
    )
    preferred_supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.SET_NULL,
        related_name="requisition_lines",
        null=True,
        blank=True,
        verbose_name=_("Preferred Supplier"),
    )

    requested_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("1.0000"), verbose_name=_("Requested Quantity"))
    approved_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("1.0000"), verbose_name=_("Approved Quantity"))
    unit = models.CharField(max_length=50, default="Pcs", verbose_name=_("Unit of Measure"))

    estimated_unit_cost = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Estimated Unit Cost"))
    estimated_total_cost = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Estimated Total Cost"))

    required_date = models.DateField(null=True, blank=True, verbose_name=_("Required Date"))
    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        db_table = "procurement_requisition_lines"
        verbose_name = _("Purchase Requisition Line")
        verbose_name_plural = _("Purchase Requisition Lines")
        ordering = ["created_at"]

    def recalculate_total_cost(self) -> None:
        self.estimated_total_cost = self.requested_quantity * self.estimated_unit_cost
