"""CustomerReturn header and line item models."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.sales_returns.models.enums import (
    InspectionResult,
    ProductCondition,
    ReturnReason,
    ReturnStatus,
)


class CustomerReturn(TenantAwareModel, FullAuditModel):
    """Header document representing a customer return request against a SalesInvoice."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="customer_returns",
        verbose_name=_("Company"),
        db_index=True,
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.PROTECT,
        related_name="customer_returns",
        verbose_name=_("Branch"),
        db_index=True,
    )
    warehouse = models.ForeignKey(
        "warehouses.Warehouse",
        on_delete=models.PROTECT,
        related_name="customer_returns",
        verbose_name=_("Warehouse"),
        db_index=True,
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.SET_NULL,
        related_name="customer_returns",
        null=True,
        blank=True,
        verbose_name=_("Customer"),
        db_index=True,
    )
    sales_invoice = models.ForeignKey(
        "sales.SalesInvoice",
        on_delete=models.PROTECT,
        related_name="customer_returns",
        verbose_name=_("Original Sales Invoice"),
        db_index=True,
    )

    return_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Return Number (CRT)"))
    return_date = models.DateField(verbose_name=_("Return Date"), db_index=True)

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
        default=ReturnReason.OTHER,
        verbose_name=_("Primary Return Reason"),
    )

    currency = models.CharField(max_length=10, default="USD", verbose_name=_("Currency Code"))
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, default=Decimal("1.000000"), verbose_name=_("Exchange Rate"))

    subtotal = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Subtotal"))
    discount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Discount"))
    tax = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Tax"))

    refund_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Eligible Refund Amount"))
    store_credit_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Issued Store Credit Amount"))

    idempotency_key = models.CharField(max_length=100, blank=True, default="", db_index=True, verbose_name=_("Idempotency Key"))

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_customer_returns",
        null=True,
        blank=True,
        verbose_name=_("Created By"),
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_customer_returns",
        null=True,
        blank=True,
        verbose_name=_("Approved By"),
    )
    inspected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="inspected_customer_returns",
        null=True,
        blank=True,
        verbose_name=_("Inspected By"),
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="processed_customer_returns",
        null=True,
        blank=True,
        verbose_name=_("Processed By"),
    )

    approved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Approved At"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Completed At"))

    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        db_table = "customer_returns"
        verbose_name = _("Customer Return")
        verbose_name_plural = _("Customer Returns")
        ordering = ["-return_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "return_number"],
                name="customer_return_tenant_number_uniq",
            )
        ]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "sales_invoice"]),
            models.Index(fields=["tenant", "customer"]),
        ]

    def __str__(self) -> str:
        return f"{self.return_number} - Invoice {self.sales_invoice.invoice_number} [{self.status}]"


class CustomerReturnLine(TenantAwareModel, FullAuditModel):
    """Line item inside a CustomerReturn representing returned medicine units."""

    customer_return = models.ForeignKey(
        CustomerReturn,
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name=_("Customer Return"),
        db_index=True,
    )
    sales_invoice_line = models.ForeignKey(
        "sales.SalesInvoiceLine",
        on_delete=models.PROTECT,
        related_name="return_lines",
        verbose_name=_("Original Sales Invoice Line"),
        db_index=True,
    )

    medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.PROTECT,
        related_name="customer_return_lines",
        verbose_name=_("Medicine"),
    )
    batch = models.ForeignKey(
        "inventory.Batch",
        on_delete=models.PROTECT,
        related_name="customer_return_lines",
        verbose_name=_("Medicine Batch"),
    )
    warehouse = models.ForeignKey(
        "warehouses.Warehouse",
        on_delete=models.PROTECT,
        related_name="customer_return_lines",
        verbose_name=_("Warehouse"),
    )
    storage_location = models.ForeignKey(
        "warehouses.StorageLocation",
        on_delete=models.PROTECT,
        related_name="customer_return_lines",
        verbose_name=_("Storage Location"),
    )

    original_sold_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Original Sold Quantity"))
    previously_returned_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Previously Returned Quantity"))
    returnable_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Returnable Quantity"))

    requested_return_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Requested Return Quantity"))
    accepted_return_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Accepted Return Quantity"))
    rejected_return_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Rejected Return Quantity"))

    unit = models.CharField(max_length=50, default="Pcs", verbose_name=_("Unit of Measure"))
    original_unit_price = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Original Unit Selling Price"))
    refund_unit_price = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Refund Unit Price"))

    discount_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Discount Portion"))
    tax_amount = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Tax Portion"))
    refund_line_total = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Refund Line Grand Total"))

    condition = models.CharField(
        max_length=30,
        choices=ProductCondition.choices,
        default=ProductCondition.SEALED,
        verbose_name=_("Returned Product Condition"),
    )
    return_reason = models.CharField(
        max_length=40,
        choices=ReturnReason.choices,
        default=ReturnReason.OTHER,
        verbose_name=_("Line Return Reason"),
    )
    inspection_result = models.CharField(
        max_length=30,
        choices=InspectionResult.choices,
        default=InspectionResult.ACCEPTED,
        verbose_name=_("Quality Inspection Result"),
    )

    notes = models.TextField(blank=True, default="", verbose_name=_("Notes"))

    class Meta:
        db_table = "customer_return_lines"
        verbose_name = _("Customer Return Line")
        verbose_name_plural = _("Customer Return Lines")
        ordering = ["created_at"]

    def calculate_line_refund(self) -> None:
        """Calculate line refund total based on accepted return quantity and original selling price."""
        sub = self.accepted_return_quantity * self.original_unit_price
        self.refund_line_total = (sub - self.discount_amount) + self.tax_amount
