"""PurchaseReturn header and line item models."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.procurement.models import ProcurementPriority
from apps.purchase_returns.models.enums import ProductCondition, ReturnReason, ReturnStatus


class PurchaseReturn(TenantAwareModel, FullAuditModel):
    """Header document for supplier purchase returns."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="purchase_returns",
        verbose_name=_("Company"),
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="purchase_returns",
        null=True,
        blank=True,
        verbose_name=_("Branch"),
    )
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.PROTECT,
        related_name="purchase_returns",
        verbose_name=_("Supplier"),
        db_index=True,
    )
    purchase_order = models.ForeignKey(
        "procurement.PurchaseOrder",
        on_delete=models.SET_NULL,
        related_name="purchase_returns",
        null=True,
        blank=True,
        verbose_name=_("Purchase Order"),
    )
    goods_receipt = models.ForeignKey(
        "goods_receipt.GoodsReceipt",
        on_delete=models.SET_NULL,
        related_name="purchase_returns",
        null=True,
        blank=True,
        verbose_name=_("Goods Receipt"),
        db_index=True,
    )
    warehouse = models.ForeignKey(
        "warehouses.Warehouse",
        on_delete=models.PROTECT,
        related_name="purchase_returns",
        verbose_name=_("Source Warehouse"),
        db_index=True,
    )

    return_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Return Number (PRT)"))
    return_date = models.DateField(verbose_name=_("Return Date"))

    status = models.CharField(
        max_length=30,
        choices=ReturnStatus.choices,
        default=ReturnStatus.DRAFT,
        db_index=True,
        verbose_name=_("Return Status"),
    )
    return_reason = models.CharField(
        max_length=40,
        choices=ReturnReason.choices,
        default=ReturnReason.DAMAGED,
        verbose_name=_("Primary Return Reason"),
    )
    priority = models.CharField(
        max_length=20,
        choices=ProcurementPriority.choices,
        default=ProcurementPriority.NORMAL,
        verbose_name=_("Priority"),
    )

    currency = models.CharField(max_length=10, default="USD", verbose_name=_("Currency Code"))
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, default=Decimal("1.000000"), verbose_name=_("Exchange Rate"))

    # Financial Totals
    subtotal = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Subtotal"))
    discount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Discount"))
    tax = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Tax"))
    other_charges = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Other Charges"))
    grand_total = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Grand Total"))

    idempotency_key = models.CharField(max_length=100, blank=True, default="", db_index=True, verbose_name=_("Idempotency Key"))

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="requested_purchase_returns",
        null=True,
        blank=True,
        verbose_name=_("Requested By"),
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_purchase_returns",
        null=True,
        blank=True,
        verbose_name=_("Approved By"),
    )
    dispatched_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="dispatched_purchase_returns",
        null=True,
        blank=True,
        verbose_name=_("Dispatched By"),
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="supplier_received_purchase_returns",
        null=True,
        blank=True,
        verbose_name=_("Supplier Acceptance Logged By"),
    )

    approved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Approved At"))
    dispatched_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Dispatched At"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Completed At"))

    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        db_table = "purchase_returns"
        verbose_name = _("Purchase Return")
        verbose_name_plural = _("Purchase Returns")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "return_number"],
                name="purchase_return_tenant_number_uniq",
            )
        ]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "supplier"]),
            models.Index(fields=["tenant", "goods_receipt"]),
        ]

    def __str__(self) -> str:
        return f"{self.return_number} - {self.supplier.legal_name} ({self.status})"


class PurchaseReturnLine(TenantAwareModel, FullAuditModel):
    """Line item for individual medicine batch return inside a PurchaseReturn."""

    purchase_return = models.ForeignKey(
        PurchaseReturn,
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name=_("Purchase Return"),
        db_index=True,
    )
    medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.PROTECT,
        related_name="purchase_return_lines",
        verbose_name=_("Medicine"),
        db_index=True,
    )
    batch = models.ForeignKey(
        "inventory.Batch",
        on_delete=models.PROTECT,
        related_name="purchase_return_lines",
        verbose_name=_("Medicine Batch"),
        db_index=True,
    )
    goods_receipt_line = models.ForeignKey(
        "goods_receipt.GoodsReceiptLine",
        on_delete=models.SET_NULL,
        related_name="purchase_return_lines",
        null=True,
        blank=True,
        verbose_name=_("Source Goods Receipt Line"),
    )
    purchase_order_line = models.ForeignKey(
        "procurement.PurchaseOrderLine",
        on_delete=models.SET_NULL,
        related_name="purchase_return_lines",
        null=True,
        blank=True,
        verbose_name=_("Source Purchase Order Line"),
    )
    storage_location = models.ForeignKey(
        "warehouses.StorageLocation",
        on_delete=models.PROTECT,
        related_name="purchase_return_lines",
        verbose_name=_("Source Storage Location"),
    )

    available_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Available Returnable Quantity"))
    requested_return_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("1.0000"), verbose_name=_("Requested Return Quantity"))
    approved_return_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("1.0000"), verbose_name=_("Approved Return Quantity"))
    dispatched_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Dispatched Quantity"))

    supplier_accepted_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Supplier Accepted Quantity"))
    supplier_rejected_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Supplier Rejected Quantity"))
    damaged_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Damaged Quantity"))

    unit = models.CharField(max_length=50, default="Pcs", verbose_name=_("Unit of Measure"))
    unit_cost = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Unit Return Cost"))
    discount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Discount"))
    tax = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Tax"))
    total_value = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Total Line Value"))

    return_reason = models.CharField(
        max_length=40,
        choices=ReturnReason.choices,
        default=ReturnReason.DAMAGED,
        verbose_name=_("Return Reason"),
    )
    condition = models.CharField(
        max_length=30,
        choices=ProductCondition.choices,
        default=ProductCondition.SEALED,
        verbose_name=_("Product Condition"),
    )
    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        db_table = "purchase_return_lines"
        verbose_name = _("Purchase Return Line")
        verbose_name_plural = _("Purchase Return Lines")
        ordering = ["created_at"]

    def calculate_total_value(self) -> None:
        """Calculate line financial value based on approved return quantity."""
        sub = self.approved_return_quantity * self.unit_cost
        self.total_value = (sub - self.discount) + self.tax
