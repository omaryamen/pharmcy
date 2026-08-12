"""ExpenseAttachment document storage metadata model."""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel


class ExpenseAttachment(TenantAwareModel, FullAuditModel):
    """Secure attachment metadata for receipt scans, PDFs, and vendor invoices."""

    expense = models.ForeignKey(
        "expenses.Expense",
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name=_("Expense Header"),
    )

    document_type = models.CharField(max_length=50, default="receipt", verbose_name=_("Document Type (receipt, invoice, contract)"))
    file_name = models.CharField(max_length=255, verbose_name=_("Original File Name"))
    storage_path = models.CharField(max_length=500, verbose_name=_("Storage Reference Path"))
    checksum = models.CharField(max_length=64, blank=True, default="", verbose_name=_("SHA256 Checksum"))

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="uploaded_expense_attachments",
        null=True,
        blank=True,
        verbose_name=_("Uploaded By"),
    )

    class Meta:
        db_table = "expense_attachments"
        verbose_name = _("Expense Attachment")
        verbose_name_plural = _("Expense Attachments")

    def __str__(self) -> str:
        return f"{self.document_type}: {self.file_name}"
