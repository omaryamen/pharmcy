"""SalesInvoice header and line item models."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.sales.models.enums import InvoicePaymentStatus, SalesStatus


class SalesInvoice(TenantAwareModel, FullAuditModel):
    """Header document for POS retail sales and customer invoices."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="sales_invoices",
        verbose_name=_("Company"),
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.PROTECT,
        related_name="sales_invoices",
        verbose_name=_("Branch"),
        db_index=True,
    )
    warehouse = models.ForeignKey(
        "warehouses.Warehouse",
        on_delete=models.PROTECT,
        related_name="sales_invoices",
        verbose_name=_("Warehouse"),
        db_index=True,
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.SET_NULL,
        related_name="sales_invoices",
        null=True,
        blank=True,
        verbose_name=_("Customer"),
        db_index=True,
    )
    register_session = models.ForeignKey(
        "sales.RegisterSession",
        on_delete=models.SET_NULL,
        related_name="sales_invoices",
        null=True,
        blank=True,
        verbose_name=_("Cash Register Session"),
    )

    invoice_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Invoice Number (INV)"))
    invoice_date = models.DateField(verbose_name=_("Invoice Date"), db_index=True)
    invoice_time = models.TimeField(verbose_name=_("Invoice Time"))

    status = models.CharField(
        max_length=30,
        choices=SalesStatus.choices,
        default=SalesStatus.DRAFT,
        db_index=True,
        verbose_name=_("Sales Status"),
    )
    payment_status = models.CharField(
        max_length=30,
        choices=InvoicePaymentStatus.choices,
        default=InvoicePaymentStatus.UNPAID,
        db_index=True,
        verbose_name=_("Payment Status"),
    )

    currency = models.CharField(max_length=10, default="USD", verbose_name=_("Currency Code"))
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, default=Decimal("1.000000"), verbose_name=_("Exchange Rate"))

    # Financial Totals
    subtotal = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Subtotal"))
    discount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Discount"))
    tax = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Tax"))
    other_charges = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Other Charges"))
    grand_total = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Grand Total"))

    paid_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Paid Amount"))
    change_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Change Amount"))
    outstanding_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Outstanding Balance"))

    idempotency_key = models.CharField(max_length=100, blank=True, default="", db_index=True, verbose_name=_("Idempotency Key"))

    cashier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="cashier_sales_invoices",
        null=True,
        blank=True,
        verbose_name=_("Cashier"),
    )
    salesperson = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="salesperson_sales_invoices",
        null=True,
        blank=True,
        verbose_name=_("Salesperson"),
    )

    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Completed At"))
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Cancelled At"))

    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        db_table = "sales_invoices"
        verbose_name = _("Sales Invoice")
        verbose_name_plural = _("Sales Invoices")
        ordering = ["-invoice_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "invoice_number"],
                name="sales_invoice_tenant_number_uniq",
            )
        ]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "branch"]),
            models.Index(fields=["tenant", "customer"]),
            models.Index(fields=["tenant", "invoice_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.invoice_number} - ({self.grand_total} {self.currency}) [{self.status}]"


class SalesInvoiceLine(TenantAwareModel, FullAuditModel):
    """Line item inside a SalesInvoice representing a sold medicine batch."""

    sales_invoice = models.ForeignKey(
        SalesInvoice,
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name=_("Sales Invoice"),
        db_index=True,
    )
    medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.PROTECT,
        related_name="sales_invoice_lines",
        verbose_name=_("Medicine"),
        db_index=True,
    )
    batch = models.ForeignKey(
        "inventory.Batch",
        on_delete=models.PROTECT,
        related_name="sales_invoice_lines",
        verbose_name=_("Medicine Batch"),
        db_index=True,
    )
    warehouse = models.ForeignKey(
        "warehouses.Warehouse",
        on_delete=models.PROTECT,
        related_name="sales_invoice_lines",
        verbose_name=_("Warehouse"),
    )
    storage_location = models.ForeignKey(
        "warehouses.StorageLocation",
        on_delete=models.PROTECT,
        related_name="sales_invoice_lines",
        verbose_name=_("Storage Location"),
    )

    quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("1.0000"), verbose_name=_("Sold Quantity"))
    returned_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Returned Quantity"))
    unit = models.CharField(max_length=50, default="Pcs", verbose_name=_("Unit of Measure"))
    unit_price = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Unit Selling Price"))

    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Discount %"))
    discount_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Discount Amount"))

    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Tax %"))
    tax_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Tax Amount"))

    line_subtotal = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Line Subtotal"))
    line_total = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Line Grand Total"))

    # Financial & Profitability snapshots
    cost_price = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Historical Unit Cost"))
    profit_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Line Gross Profit"))

    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        db_table = "sales_invoice_lines"
        verbose_name = _("Sales Invoice Line")
        verbose_name_plural = _("Sales Invoice Lines")
        ordering = ["created_at"]

    def calculate_line_financials(self) -> None:
        """Calculate line subtotal, discount, tax, total value, and gross profit."""
        sub = self.quantity * self.unit_price
        self.line_subtotal = sub
        self.line_total = (sub - self.discount_amount) + self.tax_amount

        # Capture cost & gross profit
        total_cost = self.quantity * self.cost_price
        self.profit_amount = self.line_total - total_cost
