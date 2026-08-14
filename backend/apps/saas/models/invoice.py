"""SaaSInvoice and SaaSInvoiceLine models for subscription billing statements."""

from __future__ import annotations

from typing import Any
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.saas.models.enums import SaaSInvoiceStatus, SaaSLineItemType
from apps.saas.models.subscription import SaaSSubscription


class SaaSInvoice(TenantAwareModel, FullAuditModel):
    """Authoritative commercial SaaS invoice statement issued to a tenant."""

    invoice_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Invoice Number (SINV)"))

    subscription = models.ForeignKey(
        SaaSSubscription,
        on_delete=models.SET_NULL,
        related_name="invoices",
        null=True,
        blank=True,
        verbose_name=_("Subscription"),
    )

    billing_period_start = models.DateTimeField(verbose_name=_("Billing Period Start"))
    billing_period_end = models.DateTimeField(verbose_name=_("Billing Period End"))

    issue_date = models.DateField(default=timezone.now, verbose_name=_("Issue Date"))
    due_date = models.DateField(verbose_name=_("Due Date"))

    subtotal = models.DecimalField(max_digits=12, decimal_places=4, default=0, verbose_name=_("Subtotal Amount"))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=4, default=0, verbose_name=_("Discount Amount"))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=4, default=0, verbose_name=_("Tax Amount"))
    credits_applied = models.DecimalField(max_digits=12, decimal_places=4, default=0, verbose_name=_("Credits Applied"))
    total_amount = models.DecimalField(max_digits=12, decimal_places=4, default=0, verbose_name=_("Total Amount"))

    currency = models.CharField(max_length=3, default="USD", verbose_name=_("Currency Code"))

    status = models.CharField(
        max_length=30,
        choices=SaaSInvoiceStatus.choices,
        default=SaaSInvoiceStatus.OPEN,
        db_index=True,
        verbose_name=_("Invoice Status"),
    )

    paid_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Paid Timestamp"))

    class Meta:
        db_table = "saas_invoices"
        verbose_name = _("SaaS Invoice")
        verbose_name_plural = _("SaaS Invoices")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.invoice_number} - {self.tenant.name}: {self.total_amount} {self.currency} [{self.status}]"


class SaaSInvoiceLine(TenantAwareModel, FullAuditModel):
    """Detailed line item breakdown on a SaaS invoice."""

    invoice = models.ForeignKey(
        SaaSInvoice,
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name=_("SaaS Invoice"),
    )

    line_type = models.CharField(
        max_length=30,
        choices=SaaSLineItemType.choices,
        default=SaaSLineItemType.PLAN_FEE,
        verbose_name=_("Line Item Type"),
    )

    description = models.CharField(max_length=255, verbose_name=_("Line Description"))
    quantity = models.DecimalField(max_digits=12, decimal_places=4, default=1, verbose_name=_("Quantity"))
    unit_price = models.DecimalField(max_digits=12, decimal_places=4, verbose_name=_("Unit Price"))
    amount = models.DecimalField(max_digits=12, decimal_places=4, verbose_name=_("Line Total Amount"))
    currency = models.CharField(max_length=3, default="USD", verbose_name=_("Currency Code"))

    class Meta:
        db_table = "saas_invoice_lines"
        verbose_name = _("SaaS Invoice Line")
        verbose_name_plural = _("SaaS Invoice Lines")

    def __str__(self) -> str:
        return f"{self.invoice.invoice_number} Line: {self.description} ({self.amount} {self.currency})"
