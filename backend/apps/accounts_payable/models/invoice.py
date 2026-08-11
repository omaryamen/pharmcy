"""SupplierInvoice header and line item models."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts_payable.models.enums import InvoiceStatus, MatchStatus, PaymentTerms
from apps.common.models import FullAuditModel, TenantAwareModel


class SupplierInvoice(TenantAwareModel, FullAuditModel):
    """Header document for supplier invoices and vendor bills."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="supplier_invoices",
        verbose_name=_("Company"),
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="supplier_invoices",
        null=True,
        blank=True,
        verbose_name=_("Branch"),
    )
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.PROTECT,
        related_name="supplier_invoices",
        verbose_name=_("Supplier"),
        db_index=True,
    )
    purchase_order = models.ForeignKey(
        "procurement.PurchaseOrder",
        on_delete=models.SET_NULL,
        related_name="supplier_invoices",
        null=True,
        blank=True,
        verbose_name=_("Purchase Order"),
    )
    goods_receipt = models.ForeignKey(
        "goods_receipt.GoodsReceipt",
        on_delete=models.SET_NULL,
        related_name="supplier_invoices",
        null=True,
        blank=True,
        verbose_name=_("Goods Receipt"),
        db_index=True,
    )

    invoice_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Internal Invoice Number (INV)"))
    supplier_invoice_number = models.CharField(max_length=100, db_index=True, verbose_name=_("Supplier Bill Number"))

    invoice_date = models.DateField(verbose_name=_("Invoice Date"))
    due_date = models.DateField(verbose_name=_("Due Date"))
    payment_terms = models.CharField(
        max_length=20,
        choices=PaymentTerms.choices,
        default=PaymentTerms.NET_30,
        verbose_name=_("Payment Terms"),
    )

    status = models.CharField(
        max_length=30,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.DRAFT,
        db_index=True,
        verbose_name=_("Invoice Status"),
    )
    match_status = models.CharField(
        max_length=30,
        choices=MatchStatus.choices,
        default=MatchStatus.NOT_MATCHED,
        db_index=True,
        verbose_name=_("Three-Way Match Status"),
    )

    currency = models.CharField(max_length=10, default="USD", verbose_name=_("Currency Code"))
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, default=Decimal("1.000000"), verbose_name=_("Exchange Rate"))

    # Financial Totals
    subtotal = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Subtotal"))
    discount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Discount"))
    tax = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Tax"))
    shipping = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Shipping / Freight"))
    other_charges = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Other Charges"))
    grand_total = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Grand Total"))

    paid_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Paid Amount"))
    outstanding_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Outstanding Balance"))

    idempotency_key = models.CharField(max_length=100, blank=True, default="", db_index=True, verbose_name=_("Idempotency Key"))

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_supplier_invoices",
        null=True,
        blank=True,
        verbose_name=_("Created By"),
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="verified_supplier_invoices",
        null=True,
        blank=True,
        verbose_name=_("Verified By"),
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_supplier_invoices",
        null=True,
        blank=True,
        verbose_name=_("Approved By"),
    )

    verified_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Verified At"))
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Approved At"))
    posted_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Posted At"))

    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        db_table = "supplier_invoices"
        verbose_name = _("Supplier Invoice")
        verbose_name_plural = _("Supplier Invoices")
        ordering = ["-invoice_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "supplier", "supplier_invoice_number"],
                name="supplier_invoice_tenant_supplier_bill_uniq",
            ),
            models.UniqueConstraint(
                fields=["tenant", "invoice_number"],
                name="supplier_invoice_tenant_number_uniq",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "supplier"]),
            models.Index(fields=["tenant", "due_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.invoice_number} ({self.supplier_invoice_number}) - {self.supplier.legal_name} ({self.grand_total} {self.currency})"


class SupplierInvoiceLine(TenantAwareModel, FullAuditModel):
    """Line item for individual medicine / service billed on a SupplierInvoice."""

    supplier_invoice = models.ForeignKey(
        SupplierInvoice,
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name=_("Supplier Invoice"),
        db_index=True,
    )
    medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.SET_NULL,
        related_name="supplier_invoice_lines",
        null=True,
        blank=True,
        verbose_name=_("Medicine"),
        db_index=True,
    )
    purchase_order_line = models.ForeignKey(
        "procurement.PurchaseOrderLine",
        on_delete=models.SET_NULL,
        related_name="supplier_invoice_lines",
        null=True,
        blank=True,
        verbose_name=_("Purchase Order Line"),
    )
    goods_receipt_line = models.ForeignKey(
        "goods_receipt.GoodsReceiptLine",
        on_delete=models.SET_NULL,
        related_name="supplier_invoice_lines",
        null=True,
        blank=True,
        verbose_name=_("Goods Receipt Line"),
    )

    description = models.CharField(max_length=255, verbose_name=_("Line Description"))
    quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("1.0000"), verbose_name=_("Invoiced Quantity"))
    unit = models.CharField(max_length=50, default="Pcs", verbose_name=_("Unit of Measure"))
    unit_price = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Unit Price"))
    discount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Discount"))
    tax = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Tax Amount"))

    line_subtotal = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Line Subtotal"))
    line_total = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Line Grand Total"))

    received_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Matched Received Quantity"))
    invoiced_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Invoiced Quantity Copy"))

    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        db_table = "supplier_invoice_lines"
        verbose_name = _("Supplier Invoice Line")
        verbose_name_plural = _("Supplier Invoice Lines")
        ordering = ["created_at"]

    def calculate_totals(self) -> None:
        """Calculate subtotal and grand total for line."""
        sub = self.quantity * self.unit_price
        self.line_subtotal = sub
        self.line_total = (sub - self.discount) + self.tax
        self.invoiced_quantity = self.quantity
