"""Authoritative Accounts Payable domain service managing vendor bills, AP subledger, supplier credits, and payments."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.accounts_payable.exceptions import (
    DuplicateSupplierInvoiceError,
    ExceedsOutstandingBalanceError,
    InvalidInvoiceStateError,
    PaymentAlreadyReversedError,
)
from apps.accounts_payable.models import (
    AccountsPayableEntry,
    APStatus,
    CreditApplication,
    InvoiceStatus,
    MatchStatus,
    PaymentMethod,
    PaymentStatus,
    PaymentTerms,
    SupplierInvoice,
    SupplierInvoiceLine,
    SupplierPayment,
)
from apps.accounts_payable.repositories import (
    AccountsPayableRepository,
    CreditApplicationRepository,
    SupplierInvoiceRepository,
    SupplierPaymentRepository,
)
from apps.accounts_payable.services.number_generator import AccountsPayableNumberGenerator
from apps.accounts_payable.services.three_way_match_service import ThreeWayMatchService
from apps.accounts_payable.validators import (
    calculate_due_date_from_terms,
    validate_invoice_approval_separation_of_duties,
    validate_payment_amount,
)
from apps.purchase_returns.models import CreditNoteStatus, SupplierCreditNote

logger = logging.getLogger(__name__)


class AccountsPayableService:
    """Core domain service managing SupplierInvoices, AP Subledger entries, Supplier Credit Applications, Payments, and Reversals."""

    def __init__(self):
        self.invoice_repository = SupplierInvoiceRepository()
        self.ap_repository = AccountsPayableRepository()
        self.payment_repository = SupplierPaymentRepository()
        self.credit_app_repository = CreditApplicationRepository()
        self.number_generator = AccountsPayableNumberGenerator()
        self.match_service = ThreeWayMatchService()

    @transaction.atomic
    def create_supplier_invoice(
        self,
        tenant: Any,
        company: Any,
        supplier: Any,
        supplier_invoice_number: str,
        invoice_date: Any,
        lines_data: list[dict[str, Any]],
        *,
        branch: Any | None = None,
        purchase_order: Any | None = None,
        goods_receipt: Any | None = None,
        payment_terms: str = PaymentTerms.NET_30,
        custom_due_date: Any | None = None,
        currency: str = "USD",
        exchange_rate: Decimal | float | str = "1.000000",
        discount: Decimal | float | str = "0.0000",
        tax: Decimal | float | str = "0.0000",
        shipping: Decimal | float | str = "0.0000",
        other_charges: Decimal | float | str = "0.0000",
        notes: str = "",
        idempotency_key: str = "",
        user: Any | None = None,
    ) -> SupplierInvoice:
        """Create a SupplierInvoice header and line items in DRAFT status."""
        if idempotency_key:
            existing = self.invoice_repository.find_by_idempotency_key(tenant, idempotency_key)
            if existing:
                logger.info("Found existing SupplierInvoice %s for idempotency_key %s", existing.invoice_number, idempotency_key)
                return existing

        # Duplicate Supplier Invoice Check
        dup = self.invoice_repository.find_by_supplier_bill_number(tenant, str(supplier.pk), supplier_invoice_number)
        if dup:
            raise DuplicateSupplierInvoiceError(
                f"Supplier invoice '{supplier_invoice_number}' already exists for supplier {supplier.legal_name}."
            )

        due_dt = calculate_due_date_from_terms(invoice_date, payment_terms, custom_due_date)
        inv_num = self.number_generator.generate_invoice_number(tenant)

        invoice = self.invoice_repository.create(
            tenant=tenant,
            company=company,
            branch=branch,
            supplier=supplier,
            purchase_order=purchase_order,
            goods_receipt=goods_receipt,
            invoice_number=inv_num,
            supplier_invoice_number=supplier_invoice_number.strip(),
            invoice_date=invoice_date,
            due_date=due_dt,
            payment_terms=payment_terms,
            status=InvoiceStatus.DRAFT,
            match_status=MatchStatus.NOT_MATCHED,
            currency=currency,
            exchange_rate=Decimal(str(exchange_rate)),
            discount=Decimal(str(discount)),
            tax=Decimal(str(tax)),
            shipping=Decimal(str(shipping)),
            other_charges=Decimal(str(other_charges)),
            notes=notes,
            idempotency_key=idempotency_key,
            created_by=user,
        )

        subtotal = Decimal("0.0000")

        for line_data in lines_data:
            qty = Decimal(str(line_data["quantity"]))
            u_price = Decimal(str(line_data["unit_price"]))
            l_disc = Decimal(str(line_data.get("discount", "0.0000")))
            l_tax = Decimal(str(line_data.get("tax", "0.0000")))

            line = SupplierInvoiceLine.objects.create(
                tenant=tenant,
                supplier_invoice=invoice,
                medicine=line_data.get("medicine"),
                purchase_order_line=line_data.get("purchase_order_line"),
                goods_receipt_line=line_data.get("goods_receipt_line"),
                description=line_data.get("description", getattr(line_data.get("medicine"), "english_name", "Supplier Line Item")),
                quantity=qty,
                unit=line_data.get("unit", "Pcs"),
                unit_price=u_price,
                discount=l_disc,
                tax=l_tax,
                notes=line_data.get("notes", ""),
            )
            line.calculate_totals()
            line.save()

            subtotal += line.line_subtotal

        invoice.subtotal = subtotal
        invoice.grand_total = (subtotal - invoice.discount) + invoice.tax + invoice.shipping + invoice.other_charges
        invoice.outstanding_amount = invoice.grand_total
        invoice.save(update_fields=["subtotal", "grand_total", "outstanding_amount", "updated_at"])

        logger.info("Created SupplierInvoice %s (%s) for supplier %s", inv_num, supplier_invoice_number, supplier.legal_name)
        return invoice

    @transaction.atomic
    def verify_and_match_supplier_invoice(self, tenant: Any, invoice: SupplierInvoice, user: Any | None = None) -> SupplierInvoice:
        """Run three-way matching logic for invoice against PO & Goods Receipt."""
        match_res = self.match_service.verify_and_match_invoice(tenant, invoice, user=user)

        now = timezone.now()
        invoice.verified_at = now
        invoice.verified_by = user
        if match_res == MatchStatus.MATCHED:
            invoice.status = InvoiceStatus.VERIFIED
        else:
            invoice.status = InvoiceStatus.UNDER_REVIEW

        invoice.save(update_fields=["status", "verified_at", "verified_by", "updated_at"])
        return invoice

    @transaction.atomic
    def approve_supplier_invoice(self, tenant: Any, invoice: SupplierInvoice, user: Any | None = None) -> SupplierInvoice:
        """Approve a verified or reviewed supplier invoice, enforcing separation of duties."""
        if invoice.status not in [InvoiceStatus.VERIFIED, InvoiceStatus.UNDER_REVIEW, InvoiceStatus.DRAFT]:
            raise InvalidInvoiceStateError(f"Cannot approve invoice in status {invoice.status}.")

        validate_invoice_approval_separation_of_duties(
            invoice.created_by, user, is_superuser=getattr(user, "is_superuser", False)
        )

        now = timezone.now()
        invoice.status = InvoiceStatus.APPROVED
        invoice.approved_at = now
        invoice.approved_by = user
        invoice.save(update_fields=["status", "approved_at", "approved_by", "updated_at"])

        logger.info("Approved SupplierInvoice %s", invoice.invoice_number)
        return invoice

    @transaction.atomic
    def post_supplier_invoice(self, tenant: Any, invoice: SupplierInvoice, user: Any | None = None) -> AccountsPayableEntry:
        """AUTHORITATIVE POSTING ENGINE: Creates AccountsPayableEntry in AP subledger."""
        invoice = (
            SupplierInvoice.objects.filter(tenant=tenant, pk=invoice.pk)
            .select_for_update()
            .first()
        )
        if not invoice:
            raise InvalidInvoiceStateError("Supplier invoice does not exist.")

        if hasattr(invoice, "accounts_payable_entry"):
            logger.info("Invoice %s is already posted to AP.", invoice.invoice_number)
            return invoice.accounts_payable_entry

        if invoice.status not in [InvoiceStatus.APPROVED, InvoiceStatus.VERIFIED]:
            raise InvalidInvoiceStateError(f"Cannot post supplier invoice in status {invoice.status}.")

        ap_num = self.number_generator.generate_payable_number(tenant)
        ap_entry = self.ap_repository.create(
            tenant=tenant,
            company=invoice.company,
            branch=invoice.branch,
            supplier=invoice.supplier,
            supplier_invoice=invoice,
            payable_number=ap_num,
            original_amount=invoice.grand_total,
            paid_amount=Decimal("0.0000"),
            applied_credit_amount=Decimal("0.0000"),
            outstanding_amount=invoice.grand_total,
            currency=invoice.currency,
            exchange_rate=invoice.exchange_rate,
            due_date=invoice.due_date,
            status=APStatus.OPEN,
        )

        now = timezone.now()
        invoice.status = InvoiceStatus.POSTED
        invoice.posted_at = now
        invoice.outstanding_amount = invoice.grand_total
        invoice.save(update_fields=["status", "posted_at", "outstanding_amount", "updated_at"])

        logger.info("Posted SupplierInvoice %s to AP Subledger as %s", invoice.invoice_number, ap_num)
        return ap_entry

    @transaction.atomic
    def apply_supplier_credit(
        self,
        tenant: Any,
        credit_note: SupplierCreditNote,
        invoice: SupplierInvoice,
        amount: Decimal | float | str,
        user: Any | None = None,
    ) -> CreditApplication:
        """Apply available SupplierCreditNote balance against an open AccountsPayableEntry."""
        ap_entry = (
            AccountsPayableEntry.objects.filter(tenant=tenant, supplier_invoice=invoice)
            .select_for_update()
            .first()
        )
        if not ap_entry:
            raise InvalidInvoiceStateError("No open Accounts Payable Entry found for this invoice. Post invoice first.")

        credit_note = (
            SupplierCreditNote.objects.filter(tenant=tenant, pk=credit_note.pk)
            .select_for_update()
            .first()
        )

        apply_qty = validate_payment_amount(amount, ap_entry.outstanding_amount)

        # Create Credit Application record
        app_rec = self.credit_app_repository.create(
            tenant=tenant,
            supplier_credit_note=credit_note,
            supplier_invoice=invoice,
            accounts_payable_entry=ap_entry,
            applied_amount=apply_qty,
            currency=invoice.currency,
            applied_by=user,
        )

        # Update AP Entry & Invoice balances
        ap_entry.applied_credit_amount += apply_qty
        ap_entry.outstanding_amount -= apply_qty
        if ap_entry.outstanding_amount == Decimal("0.0000"):
            ap_entry.status = APStatus.PAID
        else:
            ap_entry.status = APStatus.PARTIALLY_PAID
        ap_entry.save(update_fields=["applied_credit_amount", "outstanding_amount", "status", "updated_at"])

        invoice.outstanding_amount -= apply_qty
        if invoice.outstanding_amount == Decimal("0.0000"):
            invoice.status = InvoiceStatus.PAID
        else:
            invoice.status = InvoiceStatus.PARTIALLY_PAID
        invoice.save(update_fields=["outstanding_amount", "status", "updated_at"])

        credit_note.status = CreditNoteStatus.POSTED
        credit_note.save(update_fields=["status", "updated_at"])

        logger.info("Applied supplier credit %s (%s) to invoice %s", credit_note.credit_note_number, apply_qty, invoice.invoice_number)
        return app_rec

    @transaction.atomic
    def process_supplier_payment(
        self,
        tenant: Any,
        invoice: SupplierInvoice,
        amount: Decimal | float | str,
        *,
        payment_date: Any | None = None,
        payment_method: str = PaymentMethod.BANK_TRANSFER,
        reference_number: str = "",
        idempotency_key: str = "",
        notes: str = "",
        user: Any | None = None,
    ) -> SupplierPayment:
        """Process and post a supplier payment against an open AP Entry."""
        if idempotency_key:
            existing = self.payment_repository.find_by_idempotency_key(tenant, idempotency_key)
            if existing:
                logger.info("Found existing SupplierPayment %s for idempotency_key %s", existing.payment_number, idempotency_key)
                return existing

        ap_entry = (
            AccountsPayableEntry.objects.filter(tenant=tenant, supplier_invoice=invoice)
            .select_for_update()
            .first()
        )
        if not ap_entry:
            raise InvalidInvoiceStateError("No open Accounts Payable Entry found for this invoice. Post invoice first.")

        pmt_amount = validate_payment_amount(amount, ap_entry.outstanding_amount)
        pmt_dt = payment_date or timezone.now().date()
        pmt_num = self.number_generator.generate_payment_number(tenant)

        now = timezone.now()
        payment = self.payment_repository.create(
            tenant=tenant,
            company=invoice.company,
            branch=invoice.branch,
            supplier=invoice.supplier,
            supplier_invoice=invoice,
            accounts_payable_entry=ap_entry,
            payment_number=pmt_num,
            payment_date=pmt_dt,
            amount=pmt_amount,
            currency=invoice.currency,
            payment_method=payment_method,
            reference_number=reference_number,
            status=PaymentStatus.POSTED,
            idempotency_key=idempotency_key,
            created_by=user,
            approved_by=user,
            posted_at=now,
            notes=notes,
        )

        # Update AP Entry balances
        ap_entry.paid_amount += pmt_amount
        ap_entry.outstanding_amount -= pmt_amount
        if ap_entry.outstanding_amount == Decimal("0.0000"):
            ap_entry.status = APStatus.PAID
        else:
            ap_entry.status = APStatus.PARTIALLY_PAID
        ap_entry.save(update_fields=["paid_amount", "outstanding_amount", "status", "updated_at"])

        # Update Invoice balances
        invoice.paid_amount += pmt_amount
        invoice.outstanding_amount -= pmt_amount
        if invoice.outstanding_amount == Decimal("0.0000"):
            invoice.status = InvoiceStatus.PAID
        else:
            invoice.status = InvoiceStatus.PARTIALLY_PAID
        invoice.save(update_fields=["paid_amount", "outstanding_amount", "status", "updated_at"])

        logger.info("Processed SupplierPayment %s (%s) for invoice %s", pmt_num, pmt_amount, invoice.invoice_number)
        return payment

    @transaction.atomic
    def reverse_supplier_payment(
        self, tenant: Any, payment: SupplierPayment, reason: str = "", user: Any | None = None
    ) -> SupplierPayment:
        """Reverse a posted supplier payment, restoring outstanding AP balances."""
        payment = (
            SupplierPayment.objects.filter(tenant=tenant, pk=payment.pk)
            .select_for_update()
            .first()
        )
        if not payment:
            raise InvalidInvoiceStateError("Supplier payment does not exist.")

        if payment.status == PaymentStatus.REVERSED:
            raise PaymentAlreadyReversedError("Payment has already been reversed.")

        ap_entry = (
            AccountsPayableEntry.objects.filter(tenant=tenant, pk=payment.accounts_payable_entry.pk)
            .select_for_update()
            .first()
        )
        invoice = (
            SupplierInvoice.objects.filter(tenant=tenant, pk=payment.supplier_invoice.pk)
            .select_for_update()
            .first()
        )

        pmt_amount = payment.amount

        # Restore AP Entry balances
        ap_entry.paid_amount -= pmt_amount
        ap_entry.outstanding_amount += pmt_amount
        if ap_entry.paid_amount == Decimal("0.0000") and ap_entry.applied_credit_amount == Decimal("0.0000"):
            ap_entry.status = APStatus.OPEN
        else:
            ap_entry.status = APStatus.PARTIALLY_PAID
        ap_entry.save(update_fields=["paid_amount", "outstanding_amount", "status", "updated_at"])

        # Restore Invoice balances
        invoice.paid_amount -= pmt_amount
        invoice.outstanding_amount += pmt_amount
        if invoice.paid_amount == Decimal("0.0000"):
            invoice.status = InvoiceStatus.POSTED
        else:
            invoice.status = InvoiceStatus.PARTIALLY_PAID
        invoice.save(update_fields=["paid_amount", "outstanding_amount", "status", "updated_at"])

        payment.status = PaymentStatus.REVERSED
        payment.notes = f"{payment.notes}\n[REVERSED]: {reason}".strip()
        payment.save(update_fields=["status", "notes", "updated_at"])

        logger.info("Reversed SupplierPayment %s (%s)", payment.payment_number, pmt_amount)
        return payment
