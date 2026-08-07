"""Company Settings model for legal entity operational configuration."""

from __future__ import annotations

from django.db import models

from apps.common.models import FullAuditModel
from apps.common.models.tenancy import TenantAwareModel


def default_company_tax_config() -> dict:
    return {
        "tax_enabled": True,
        "default_tax_rate": 15.0,
        "tax_inclusive": False,
        "tax_registration_number": "",
    }


def default_document_prefixes() -> dict:
    return {
        "invoice_prefix": "INV",
        "sale_prefix": "SAL",
        "purchase_order_prefix": "PO",
        "goods_receipt_prefix": "GRN",
        "quotation_prefix": "QUO",
        "receipt_prefix": "REC",
    }


class CompanySettings(FullAuditModel, TenantAwareModel):
    """Hierarchical operational and financial settings for a Company."""

    company = models.OneToOneField(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="settings",
        verbose_name="Company",
    )
    general_settings = models.JSONField(default=dict, blank=True, verbose_name="General settings")
    financial_settings = models.JSONField(default=dict, blank=True, verbose_name="Financial settings")
    inventory_settings = models.JSONField(default=dict, blank=True, verbose_name="Inventory settings")
    sales_settings = models.JSONField(default=dict, blank=True, verbose_name="Sales settings")
    purchase_settings = models.JSONField(default=dict, blank=True, verbose_name="Purchase settings")
    pos_settings = models.JSONField(default=dict, blank=True, verbose_name="POS settings")
    barcode_settings = models.JSONField(default=dict, blank=True, verbose_name="Barcode settings")
    receipt_settings = models.JSONField(default=dict, blank=True, verbose_name="Receipt settings")
    tax_configuration = models.JSONField(default=default_company_tax_config, blank=True, verbose_name="Tax configuration")
    invoice_numbering = models.JSONField(default=dict, blank=True, verbose_name="Invoice numbering")
    document_prefixes = models.JSONField(default=default_document_prefixes, blank=True, verbose_name="Document prefixes")
    default_currency = models.CharField(max_length=10, default="YER", verbose_name="Default currency")
    default_language = models.CharField(max_length=10, default="en", verbose_name="Default language")
    theme_configuration = models.JSONField(default=dict, blank=True, verbose_name="Theme configuration")

    class Meta:
        verbose_name = "Company Settings"
        verbose_name_plural = "Company Settings"

    def __str__(self) -> str:
        return f"Settings for {self.company.legal_name}"
