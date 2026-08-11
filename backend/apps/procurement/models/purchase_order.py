"""Purchase Order header and line item models."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.procurement.models.enums import ProcurementPriority, PurchaseOrderStatus
from apps.procurement.models.requisition import PurchaseRequisition


class PurchaseOrder(TenantAwareModel, FullAuditModel):
    """Authoritative Purchase Order header document for supplier procurement."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="purchase_orders",
        verbose_name=_("Company"),
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="purchase_orders",
        null=True,
        blank=True,
        verbose_name=_("Branch"),
    )
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.PROTECT,
        related_name="purchase_orders",
        verbose_name=_("Supplier"),
        db_index=True,
    )
    warehouse = models.ForeignKey(
        "warehouses.Warehouse",
        on_delete=models.PROTECT,
        related_name="purchase_orders",
        verbose_name=_("Destination Warehouse"),
        db_index=True,
    )
    requisition = models.ForeignKey(
        PurchaseRequisition,
        on_delete=models.SET_NULL,
        related_name="purchase_orders",
        null=True,
        blank=True,
        verbose_name=_("Source Requisition"),
    )

    po_number = models.CharField(max_length=60, db_index=True, verbose_name=_("PO Number"))
    supplier_reference = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Supplier Quote / Ref No."))

    order_date = models.DateField(verbose_name=_("Order Date"))
    expected_delivery_date = models.DateField(null=True, blank=True, verbose_name=_("Expected Delivery Date"))
    actual_delivery_date = models.DateField(null=True, blank=True, verbose_name=_("Actual Delivery Date"))

    currency = models.CharField(max_length=10, default="USD", verbose_name=_("Currency Code"))
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, default=Decimal("1.000000"), verbose_name=_("Exchange Rate to Base Currency"))
    payment_terms = models.CharField(max_length=100, blank=True, default="Net 30", verbose_name=_("Payment Terms"))

    status = models.CharField(
        max_length=30,
        choices=PurchaseOrderStatus.choices,
        default=PurchaseOrderStatus.DRAFT,
        db_index=True,
        verbose_name=_("PO Status"),
    )
    priority = models.CharField(
        max_length=20,
        choices=ProcurementPriority.choices,
        default=ProcurementPriority.NORMAL,
        verbose_name=_("Priority"),
    )

    # Financial Summary
    subtotal = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Subtotal"))
    discount_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Discount Amount"))
    tax_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Tax Amount"))
    shipping_cost = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Shipping Cost"))
    other_charges = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Other Charges"))
    grand_total = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Grand Total"))

    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))
    terms_and_conditions = models.TextField(blank=True, default="", verbose_name=_("Terms and Conditions"))

    idempotency_key = models.CharField(max_length=100, blank=True, default="", db_index=True, verbose_name=_("Idempotency Key"))

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_purchase_orders",
        null=True,
        blank=True,
        verbose_name=_("Created By"),
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_purchase_orders",
        null=True,
        blank=True,
        verbose_name=_("Approved By"),
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Approved At"))

    sent_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Sent To Supplier At"))
    acknowledged_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Acknowledged At"))

    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="cancelled_purchase_orders",
        null=True,
        blank=True,
        verbose_name=_("Cancelled By"),
    )
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Cancelled At"))
    cancellation_reason = models.TextField(blank=True, default="", verbose_name=_("Cancellation Reason"))

    class Meta:
        db_table = "procurement_purchase_orders"
        verbose_name = _("Purchase Order")
        verbose_name_plural = _("Purchase Orders")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "po_number"],
                name="purchase_order_tenant_number_uniq",
            )
        ]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "supplier"]),
            models.Index(fields=["tenant", "warehouse"]),
            models.Index(fields=["tenant", "order_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.po_number} - {self.supplier.name} ({self.status})"


class PurchaseOrderLine(TenantAwareModel, FullAuditModel):
    """Individual line item inside a PurchaseOrder."""

    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name=_("Purchase Order"),
        db_index=True,
    )
    medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.PROTECT,
        related_name="purchase_order_lines",
        verbose_name=_("Medicine"),
        db_index=True,
    )
    warehouse = models.ForeignKey(
        "warehouses.Warehouse",
        on_delete=models.SET_NULL,
        related_name="purchase_order_lines",
        null=True,
        blank=True,
        verbose_name=_("Line Warehouse"),
    )
    storage_location = models.ForeignKey(
        "warehouses.StorageLocation",
        on_delete=models.SET_NULL,
        related_name="purchase_order_lines",
        null=True,
        blank=True,
        verbose_name=_("Storage Location Foundation"),
    )

    supplier_product_code = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Supplier SKU / Product Code"))
    supplier_barcode = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Supplier Barcode"))
    description = models.CharField(max_length=255, blank=True, default="", verbose_name=_("Line Description"))

    ordered_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("1.0000"), verbose_name=_("Ordered Quantity"))
    free_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Free Bonus Quantity"))
    unit = models.CharField(max_length=50, default="Pcs", verbose_name=_("Unit of Measure"))

    unit_price = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Unit Purchase Price"))
    discount_percentage = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Discount Percentage"))
    discount_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Discount Amount"))

    tax_percentage = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Tax Percentage"))
    tax_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Tax Amount"))

    line_subtotal = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Line Subtotal"))
    line_total = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Line Grand Total"))

    # Receiving Status Foundation (Consumed by Goods Receipt IMP-022 - NO DIRECT INVENTORY MUTATIONS HERE)
    received_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Received Quantity"))
    free_quantity_received = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Free Quantity Received"))

    expected_date = models.DateField(null=True, blank=True, verbose_name=_("Expected Line Date"))
    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        db_table = "procurement_purchase_order_lines"
        verbose_name = _("Purchase Order Line")
        verbose_name_plural = _("Purchase Order Lines")
        ordering = ["created_at"]

    @property
    def remaining_quantity(self) -> Decimal:
        """Calculate remaining un-received quantity."""
        return max(Decimal("0.0000"), self.ordered_quantity - self.received_quantity)

    def calculate_totals(self) -> None:
        """Deterministically calculate subtotal, discount, tax, and total for this line."""
        sub = self.ordered_quantity * self.unit_price

        if self.discount_percentage > Decimal("0.00"):
            self.discount_amount = sub * (self.discount_percentage / Decimal("100.00"))

        taxable = sub - self.discount_amount
        if self.tax_percentage > Decimal("0.00"):
            self.tax_amount = taxable * (self.tax_percentage / Decimal("100.00"))

        self.line_subtotal = sub
        self.line_total = taxable + self.tax_amount
