"""GoodsReceipt header and line item models."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.goods_receipt.models.enums import QualityStatus, ReceiptStatus


class GoodsReceipt(TenantAwareModel, FullAuditModel):
    """Header record for physical goods receiving documents."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="goods_receipts",
        verbose_name=_("Company"),
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="goods_receipts",
        null=True,
        blank=True,
        verbose_name=_("Branch"),
    )
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.PROTECT,
        related_name="goods_receipts",
        verbose_name=_("Supplier"),
        db_index=True,
    )
    purchase_order = models.ForeignKey(
        "procurement.PurchaseOrder",
        on_delete=models.SET_NULL,
        related_name="goods_receipts",
        null=True,
        blank=True,
        verbose_name=_("Purchase Order"),
        db_index=True,
    )
    warehouse = models.ForeignKey(
        "warehouses.Warehouse",
        on_delete=models.PROTECT,
        related_name="goods_receipts",
        verbose_name=_("Warehouse"),
        db_index=True,
    )
    receiving_location = models.ForeignKey(
        "warehouses.StorageLocation",
        on_delete=models.SET_NULL,
        related_name="goods_receipts",
        null=True,
        blank=True,
        verbose_name=_("Default Receiving Location"),
    )

    receipt_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Receipt Number (GRN)"))
    supplier_delivery_number = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Supplier Delivery Note No."))
    supplier_invoice_reference = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Supplier Invoice Reference"))

    receipt_date = models.DateField(verbose_name=_("Receipt Date"))
    delivery_date = models.DateField(null=True, blank=True, verbose_name=_("Supplier Delivery Date"))

    status = models.CharField(
        max_length=30,
        choices=ReceiptStatus.choices,
        default=ReceiptStatus.DRAFT,
        db_index=True,
        verbose_name=_("Receipt Status"),
    )

    currency = models.CharField(max_length=10, default="USD", verbose_name=_("Currency Code"))
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, default=Decimal("1.000000"), verbose_name=_("Exchange Rate"))

    # Financial Summary
    subtotal = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Subtotal"))
    discount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Discount"))
    tax = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Tax"))
    shipping_cost = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Shipping Cost"))
    other_charges = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Other Charges"))
    grand_total = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Grand Total"))

    idempotency_key = models.CharField(max_length=100, blank=True, default="", db_index=True, verbose_name=_("Idempotency Key"))

    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="received_goods_receipts",
        null=True,
        blank=True,
        verbose_name=_("Received By"),
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="verified_goods_receipts",
        null=True,
        blank=True,
        verbose_name=_("Verified By"),
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_goods_receipts",
        null=True,
        blank=True,
        verbose_name=_("Approved By"),
    )

    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Completed At"))
    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        db_table = "goods_receipts"
        verbose_name = _("Goods Receipt")
        verbose_name_plural = _("Goods Receipts")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "receipt_number"],
                name="goods_receipt_tenant_number_uniq",
            )
        ]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "supplier"]),
            models.Index(fields=["tenant", "purchase_order"]),
            models.Index(fields=["tenant", "warehouse"]),
        ]

    def __str__(self) -> str:
        return f"{self.receipt_number} - {self.supplier.legal_name} ({self.status})"


class GoodsReceiptLine(TenantAwareModel, FullAuditModel):
    """Line item for individual medicine batch physical receipt inside a GoodsReceipt."""

    goods_receipt = models.ForeignKey(
        GoodsReceipt,
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name=_("Goods Receipt"),
        db_index=True,
    )
    purchase_order_line = models.ForeignKey(
        "procurement.PurchaseOrderLine",
        on_delete=models.SET_NULL,
        related_name="goods_receipt_lines",
        null=True,
        blank=True,
        verbose_name=_("Purchase Order Line"),
    )
    medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.PROTECT,
        related_name="goods_receipt_lines",
        verbose_name=_("Medicine"),
        db_index=True,
    )
    batch = models.ForeignKey(
        "inventory.Batch",
        on_delete=models.SET_NULL,
        related_name="goods_receipt_lines",
        null=True,
        blank=True,
        verbose_name=_("Created / Reused Batch"),
    )

    batch_number = models.CharField(max_length=100, db_index=True, verbose_name=_("Batch Number"))
    manufacturing_date = models.DateField(null=True, blank=True, verbose_name=_("Manufacturing Date"))
    expiry_date = models.DateField(verbose_name=_("Expiry Date"), db_index=True)

    received_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("1.0000"), verbose_name=_("Total Received Quantity"))
    accepted_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("1.0000"), verbose_name=_("Accepted Quantity"))
    rejected_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Rejected Quantity"))
    damaged_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Damaged Quantity"))
    free_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Free Quantity Received"))
    unit = models.CharField(max_length=50, default="Pcs", verbose_name=_("Unit of Measure"))

    unit_cost = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Purchase Unit Cost"))
    discount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Line Discount"))
    tax = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Line Tax"))
    total_cost = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Total Line Cost"))

    storage_location = models.ForeignKey(
        "warehouses.StorageLocation",
        on_delete=models.PROTECT,
        related_name="goods_receipt_lines",
        verbose_name=_("Destination Storage Location"),
    )

    quality_status = models.CharField(
        max_length=30,
        choices=QualityStatus.choices,
        default=QualityStatus.ACCEPTED,
        db_index=True,
        verbose_name=_("Quality Inspection Status"),
    )

    # Cold-chain inspection fields
    temperature_at_receipt = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name=_("Temperature At Receipt (°C)"))
    min_temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name=_("Min Allowed Temperature (°C)"))
    max_temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name=_("Max Allowed Temperature (°C)"))
    temperature_excursion_flag = models.BooleanField(default=False, verbose_name=_("Temperature Excursion Flag"))
    inspection_result = models.TextField(blank=True, default="", verbose_name=_("Inspection Notes"))

    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        db_table = "goods_receipt_lines"
        verbose_name = _("Goods Receipt Line")
        verbose_name_plural = _("Goods Receipt Lines")
        ordering = ["created_at"]

    def calculate_total_cost(self) -> None:
        """Calculate line financial cost based on accepted quantity."""
        sub = self.accepted_quantity * self.unit_cost
        self.total_cost = (sub - self.discount) + self.tax
