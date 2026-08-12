"""GLIntegrationPostingService integrating POS sales, payments, supplier bills, and inventory movements into General Ledger double-entry journals."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.db import transaction

from apps.accounts_payable.models import SupplierInvoice, SupplierPayment
from apps.accounts_receivable.models import CustomerPayment
from apps.general_ledger.models import AccountMapping, MappingPurpose
from apps.general_ledger.services.coa_service import ChartOfAccountsService
from apps.general_ledger.services.journal_posting_service import JournalPostingService
from apps.sales.models import SalesInvoice

logger = logging.getLogger(__name__)


class GLIntegrationPostingService:
    """Authoritative integration service posting balanced double-entry accounting journals for operational domain events."""

    def __init__(self, posting_service: JournalPostingService | None = None) -> None:
        self.posting_service = posting_service or JournalPostingService()
        self.coa_service = ChartOfAccountsService()

    def _get_mapped_account(self, tenant: Any, company: Any, purpose: str):
        mapping = AccountMapping.objects.filter(tenant=tenant, company=company, purpose=purpose).first()
        if not mapping:
            # Auto seed if missing
            seeded = self.coa_service.seed_default_chart_of_accounts(tenant, company)
            mapping = AccountMapping.objects.filter(tenant=tenant, company=company, purpose=purpose).first()
        return mapping.account

    @transaction.atomic
    def post_sales_invoice_journal(self, tenant: Any, sales_invoice: SalesInvoice, user: Any | None = None) -> None:
        """Create GL double-entry journals for POS sales invoice (Revenue + Tax + COGS)."""
        company = sales_invoice.company
        grand_total = sales_invoice.grand_total
        tax_amount = sales_invoice.tax
        revenue_amount = grand_total - tax_amount

        cash_paid = sales_invoice.paid_amount
        credit_amount = sales_invoice.outstanding_amount

        lines = []

        # 1. Debit Cash & Credit AR
        if cash_paid > Decimal("0.0000"):
            cash_acc = self._get_mapped_account(tenant, company, MappingPurpose.DEFAULT_CASH)
            lines.append({"account": cash_acc, "debit": cash_paid, "credit": Decimal("0.0000"), "description": f"Cash received for Sale {sales_invoice.invoice_number}"})
        if credit_amount > Decimal("0.0000"):
            ar_acc = self._get_mapped_account(tenant, company, MappingPurpose.DEFAULT_AR)
            lines.append({"account": ar_acc, "debit": credit_amount, "credit": Decimal("0.0000"), "description": f"Credit AR for Sale {sales_invoice.invoice_number}"})

        # 2. Credit Sales Revenue
        rev_acc = self._get_mapped_account(tenant, company, MappingPurpose.DEFAULT_SALES_REVENUE)
        lines.append({"account": rev_acc, "debit": Decimal("0.0000"), "credit": revenue_amount, "description": f"Sales Revenue for Sale {sales_invoice.invoice_number}"})

        # 3. Credit Output Tax Payable if applicable
        if tax_amount > Decimal("0.0000"):
            tax_acc = self._get_mapped_account(tenant, company, MappingPurpose.DEFAULT_OUTPUT_TAX)
            lines.append({"account": tax_acc, "debit": Decimal("0.0000"), "credit": tax_amount, "description": f"Output Tax for Sale {sales_invoice.invoice_number}"})

        # Post Revenue Journal
        self.posting_service.create_and_post_journal_entry(
            tenant=tenant,
            company=company,
            branch=sales_invoice.branch,
            posting_date=sales_invoice.invoice_date,
            description=f"Revenue Journal for Sales Invoice {sales_invoice.invoice_number}",
            lines_data=lines,
            reference_type="SALES_INVOICE",
            reference_id=str(sales_invoice.pk),
            reference_number=sales_invoice.invoice_number,
            source_module="sales",
            idempotency_key=f"GL-SALE-{sales_invoice.pk}",
            user=user,
        )

        # 4. COGS & Inventory Stock Reduction Journal
        total_cogs = Decimal("0.0000")
        for inv_line in sales_invoice.lines.all():
            total_cogs += (inv_line.quantity * inv_line.cost_price)

        if total_cogs > Decimal("0.0000"):
            cogs_acc = self._get_mapped_account(tenant, company, MappingPurpose.DEFAULT_COGS)
            inv_acc = self._get_mapped_account(tenant, company, MappingPurpose.DEFAULT_INVENTORY)

            cogs_lines = [
                {"account": cogs_acc, "debit": total_cogs, "credit": Decimal("0.0000"), "description": f"COGS for Sale {sales_invoice.invoice_number}"},
                {"account": inv_acc, "debit": Decimal("0.0000"), "credit": total_cogs, "description": f"Inventory Reduction for Sale {sales_invoice.invoice_number}"},
            ]

            self.posting_service.create_and_post_journal_entry(
                tenant=tenant,
                company=company,
                branch=sales_invoice.branch,
                posting_date=sales_invoice.invoice_date,
                description=f"COGS & Inventory Journal for Sales Invoice {sales_invoice.invoice_number}",
                lines_data=cogs_lines,
                reference_type="SALES_COGS",
                reference_id=str(sales_invoice.pk),
                reference_number=sales_invoice.invoice_number,
                source_module="sales",
                idempotency_key=f"GL-COGS-{sales_invoice.pk}",
                user=user,
            )

    @transaction.atomic
    def post_customer_payment_journal(self, tenant: Any, payment: CustomerPayment, user: Any | None = None) -> None:
        """Create GL double-entry journal for Customer Payment (Debit Cash/Bank, Credit AR)."""
        company = payment.company
        pmt_amount = payment.amount

        bank_or_cash_purpose = MappingPurpose.DEFAULT_BANK if payment.payment_method == "bank_transfer" else MappingPurpose.DEFAULT_CASH
        asset_acc = self._get_mapped_account(tenant, company, bank_or_cash_purpose)
        ar_acc = self._get_mapped_account(tenant, company, MappingPurpose.DEFAULT_AR)

        lines = [
            {"account": asset_acc, "debit": pmt_amount, "credit": Decimal("0.0000"), "description": f"Received Payment {payment.payment_number}"},
            {"account": ar_acc, "debit": Decimal("0.0000"), "credit": pmt_amount, "description": f"Applied Payment {payment.payment_number} to AR"},
        ]

        self.posting_service.create_and_post_journal_entry(
            tenant=tenant,
            company=company,
            branch=payment.branch,
            posting_date=payment.payment_date,
            description=f"Customer Payment Journal {payment.payment_number}",
            lines_data=lines,
            reference_type="CUSTOMER_PAYMENT",
            reference_id=str(payment.pk),
            reference_number=payment.payment_number,
            source_module="accounts_receivable",
            idempotency_key=f"GL-CPAY-{payment.pk}",
            user=user,
        )

    @transaction.atomic
    def post_supplier_invoice_journal(self, tenant: Any, supplier_invoice: SupplierInvoice, user: Any | None = None) -> None:
        """Create GL double-entry journal for Supplier Bill (Debit Inventory, Credit AP)."""
        company = supplier_invoice.company
        inv_total = supplier_invoice.grand_total

        inv_acc = self._get_mapped_account(tenant, company, MappingPurpose.DEFAULT_INVENTORY)
        ap_acc = self._get_mapped_account(tenant, company, MappingPurpose.DEFAULT_AP)

        lines = [
            {"account": inv_acc, "debit": inv_total, "credit": Decimal("0.0000"), "description": f"Inventory Purchase for Bill {supplier_invoice.invoice_number}"},
            {"account": ap_acc, "debit": Decimal("0.0000"), "credit": inv_total, "description": f"AP Liability for Bill {supplier_invoice.invoice_number}"},
        ]

        self.posting_service.create_and_post_journal_entry(
            tenant=tenant,
            company=company,
            branch=supplier_invoice.branch,
            posting_date=supplier_invoice.invoice_date,
            description=f"Supplier Invoice Journal {supplier_invoice.invoice_number}",
            lines_data=lines,
            reference_type="SUPPLIER_INVOICE",
            reference_id=str(supplier_invoice.pk),
            reference_number=supplier_invoice.invoice_number,
            source_module="accounts_payable",
            idempotency_key=f"GL-SINV-{supplier_invoice.pk}",
            user=user,
        )

    @transaction.atomic
    def post_supplier_payment_journal(self, tenant: Any, payment: SupplierPayment, user: Any | None = None) -> None:
        """Create GL double-entry journal for Supplier Payment (Debit AP, Credit Cash/Bank)."""
        company = payment.company
        pmt_amount = payment.amount

        bank_or_cash_purpose = MappingPurpose.DEFAULT_BANK if payment.payment_method == "bank_transfer" else MappingPurpose.DEFAULT_CASH
        asset_acc = self._get_mapped_account(tenant, company, bank_or_cash_purpose)
        ap_acc = self._get_mapped_account(tenant, company, MappingPurpose.DEFAULT_AP)

        lines = [
            {"account": ap_acc, "debit": pmt_amount, "credit": Decimal("0.0000"), "description": f"Settled AP for Payment {payment.payment_number}"},
            {"account": asset_acc, "debit": Decimal("0.0000"), "credit": pmt_amount, "description": f"Disbursed Payment {payment.payment_number}"},
        ]

        self.posting_service.create_and_post_journal_entry(
            tenant=tenant,
            company=company,
            branch=payment.branch,
            posting_date=payment.payment_date,
            description=f"Supplier Payment Journal {payment.payment_number}",
            lines_data=lines,
            reference_type="SUPPLIER_PAYMENT",
            reference_id=str(payment.pk),
            reference_number=payment.payment_number,
            source_module="accounts_payable",
            idempotency_key=f"GL-SPAY-{payment.pk}",
            user=user,
        )
