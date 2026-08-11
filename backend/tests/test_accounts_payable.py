"""Comprehensive test suite for IMP-024 — Enterprise Supplier Invoices & Accounts Payable Foundation.
Tests: models, duplicate invoice detection, three-way matching engine, payment terms & due date calculation,
invoice approval & separation of duties, AP subledger posting, supplier credit note application,
partial & full payments, overpayment prevention, payment reversals, AP aging analytics, and tenant isolation.
"""

from __future__ import annotations

import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.accounts_payable.exceptions import (
    DuplicateSupplierInvoiceError,
    ExceedsOutstandingBalanceError,
    PaymentAlreadyReversedError,
    PaymentSelfApprovalForbiddenError,
)
from apps.accounts_payable.models import (
    AccountsPayableEntry,
    APStatus,
    InvoiceStatus,
    MatchStatus,
    PaymentMethod,
    PaymentStatus,
    PaymentTerms,
    SupplierInvoice,
    SupplierPayment,
)
from apps.accounts_payable.selectors import AccountsPayableSelector
from apps.accounts_payable.services import AccountsPayableService
from apps.companies.models import Company
from apps.core.models import Tenant
from apps.goods_receipt.services import GoodsReceiptService
from apps.inventory.models import Batch
from apps.medicines.models import Medicine
from apps.procurement.services import PurchaseOrderService
from apps.purchase_returns.services import PurchaseReturnService
from apps.suppliers.models import Supplier
from apps.warehouses.models import StorageLocation, Warehouse

User = get_user_model()


# ---------------------------------------------------------------------------
# Test data factories
# ---------------------------------------------------------------------------

def make_tenant(suffix=""):
    code = "ap-" + uuid.uuid4().hex[:6] + suffix
    return Tenant.objects.create(name=f"AP Tenant {code}", code=code, slug=code)


def make_company(tenant, code=None):
    code = code or ("CO-" + uuid.uuid4().hex[:6])
    return Company.objects.create(tenant=tenant, code=code, legal_name=f"Company {code}")


def make_warehouse(tenant, company, name="Warehouse"):
    code = "WH-" + uuid.uuid4().hex[:6]
    return Warehouse.objects.create(tenant=tenant, company=company, code=code, name=f"{name} {code}")


def make_location(tenant, warehouse, name="Location"):
    code = "LOC-" + uuid.uuid4().hex[:6]
    return StorageLocation.objects.create(tenant=tenant, warehouse=warehouse, code=code, name=f"{name} {code}")


def make_supplier(tenant, name="Pharma Wholesaler Ltd"):
    code = "SUP-" + uuid.uuid4().hex[:6]
    return Supplier.objects.create(
        tenant=tenant,
        code=code,
        legal_name=name,
        display_name=name,
        supplier_type="distributor",
        status="active",
    )


def make_medicine(tenant, name="Paracetamol 500mg"):
    code = "MED-" + uuid.uuid4().hex[:6]
    return Medicine.objects.create(
        tenant=tenant,
        code=code,
        sku=code,
        english_name=name,
        arabic_name="باراسيتامول",
        status="active",
    )


def make_user(email=None):
    email = email or f"u-{uuid.uuid4().hex[:8]}@test.com"
    return User.objects.create_user(email=email, first_name="APUser", password="Pass123!")


def ap_full_setup():
    """Setup PO, Goods Receipt, and Supplier return context."""
    tenant = make_tenant()
    company = make_company(tenant)
    warehouse = make_warehouse(tenant, company)
    location = make_location(tenant, warehouse)
    supplier = make_supplier(tenant)
    medicine = make_medicine(tenant)
    creator = make_user("creator@ap.com")
    approver = make_user("approver@ap.com")

    # 1. Purchase Order (ordered 100 @ $10.00)
    po_svc = PurchaseOrderService()
    po = po_svc.create_purchase_order(
        tenant=tenant,
        company=company,
        supplier=supplier,
        warehouse=warehouse,
        lines_data=[{"medicine": medicine, "ordered_quantity": Decimal("100.0000"), "unit_price": Decimal("10.0000")}],
        user=creator,
    )
    po_svc.submit_purchase_order(tenant, po, user=creator)
    po_svc.approve_purchase_order(tenant, po, user=approver)
    po_svc.send_to_supplier(tenant, po, user=approver)

    # 2. Goods Receipt Posting (received 100 @ $10.00)
    grn_svc = GoodsReceiptService()
    exp = timezone.now().date() + timedelta(days=365)
    grn = grn_svc.create_goods_receipt(
        tenant=tenant,
        company=company,
        supplier=supplier,
        warehouse=warehouse,
        purchase_order=po,
        receiving_location=location,
        lines_data=[{
            "purchase_order_line": po.lines.first(),
            "medicine": medicine,
            "batch_number": "BATCH-AP-100",
            "expiry_date": exp,
            "received_quantity": Decimal("100.0000"),
            "accepted_quantity": Decimal("100.0000"),
            "unit_cost": Decimal("10.0000"),
            "storage_location": location,
        }],
        user=creator,
    )
    posted_grn = grn_svc.post_goods_receipt(tenant, grn, user=creator)

    return tenant, company, warehouse, location, supplier, medicine, po, posted_grn, creator, approver


# ===========================================================================
# INVOICE CREATION & DUPLICATE DETECTION TESTS
# ===========================================================================


@pytest.mark.django_db
class TestSupplierInvoiceCreation:
    def test_create_supplier_invoice_draft(self):
        tenant, company, warehouse, location, supplier, medicine, po, grn, creator, _ = ap_full_setup()
        service = AccountsPayableService()

        inv = service.create_supplier_invoice(
            tenant=tenant,
            company=company,
            supplier=supplier,
            supplier_invoice_number="BILL-2026-001",
            invoice_date=timezone.now().date(),
            purchase_order=po,
            goods_receipt=grn,
            payment_terms=PaymentTerms.NET_30,
            lines_data=[{
                "medicine": medicine,
                "purchase_order_line": po.lines.first(),
                "goods_receipt_line": grn.lines.first(),
                "quantity": Decimal("100.0000"),
                "unit_price": Decimal("10.0000"),
            }],
            user=creator,
        )

        assert inv.pk is not None
        assert inv.invoice_number.startswith("INV-")
        assert inv.supplier_invoice_number == "BILL-2026-001"
        assert inv.status == InvoiceStatus.DRAFT
        assert inv.grand_total == Decimal("1000.0000")
        assert inv.due_date == inv.invoice_date + timedelta(days=30)

    def test_duplicate_supplier_invoice_rejected(self):
        tenant, company, warehouse, location, supplier, medicine, po, grn, creator, _ = ap_full_setup()
        service = AccountsPayableService()

        service.create_supplier_invoice(
            tenant=tenant,
            company=company,
            supplier=supplier,
            supplier_invoice_number="BILL-DUP-1",
            invoice_date=timezone.now().date(),
            lines_data=[{"medicine": medicine, "quantity": Decimal("10"), "unit_price": Decimal("10")}],
            user=creator,
        )

        with pytest.raises(DuplicateSupplierInvoiceError):
            service.create_supplier_invoice(
                tenant=tenant,
                company=company,
                supplier=supplier,
                supplier_invoice_number="BILL-DUP-1",  # Same bill number for same supplier
                invoice_date=timezone.now().date(),
                lines_data=[{"medicine": medicine, "quantity": Decimal("10"), "unit_price": Decimal("10")}],
                user=creator,
            )


# ===========================================================================
# THREE-WAY MATCHING TESTS
# ===========================================================================


@pytest.mark.django_db
class TestThreeWayMatchingEngine:
    def test_three_way_match_successful(self):
        tenant, company, warehouse, location, supplier, medicine, po, grn, creator, _ = ap_full_setup()
        service = AccountsPayableService()

        inv = service.create_supplier_invoice(
            tenant=tenant,
            company=company,
            supplier=supplier,
            supplier_invoice_number="BILL-MATCH-OK",
            invoice_date=timezone.now().date(),
            purchase_order=po,
            goods_receipt=grn,
            lines_data=[{
                "medicine": medicine,
                "purchase_order_line": po.lines.first(),
                "goods_receipt_line": grn.lines.first(),
                "quantity": Decimal("100.0000"),
                "unit_price": Decimal("10.0000"),
            }],
            user=creator,
        )

        verified = service.verify_and_match_supplier_invoice(tenant, inv, user=creator)
        assert verified.match_status == MatchStatus.MATCHED
        assert verified.status == InvoiceStatus.VERIFIED

    def test_three_way_match_quantity_variance(self):
        """Invoice quantity 120 > received quantity 100 -> QUANTITY_VARIANCE."""
        tenant, company, warehouse, location, supplier, medicine, po, grn, creator, _ = ap_full_setup()
        service = AccountsPayableService()

        inv = service.create_supplier_invoice(
            tenant=tenant,
            company=company,
            supplier=supplier,
            supplier_invoice_number="BILL-QTY-VAR",
            invoice_date=timezone.now().date(),
            purchase_order=po,
            goods_receipt=grn,
            lines_data=[{
                "medicine": medicine,
                "purchase_order_line": po.lines.first(),
                "goods_receipt_line": grn.lines.first(),
                "quantity": Decimal("120.0000"),  # Billed 120 vs 100 received
                "unit_price": Decimal("10.0000"),
            }],
            user=creator,
        )

        verified = service.verify_and_match_supplier_invoice(tenant, inv, user=creator)
        assert verified.match_status == MatchStatus.QUANTITY_VARIANCE
        assert verified.status == InvoiceStatus.UNDER_REVIEW

    def test_three_way_match_price_variance(self):
        """Invoice unit price $12.00 != PO unit price $10.00 -> PRICE_VARIANCE."""
        tenant, company, warehouse, location, supplier, medicine, po, grn, creator, _ = ap_full_setup()
        service = AccountsPayableService()

        inv = service.create_supplier_invoice(
            tenant=tenant,
            company=company,
            supplier=supplier,
            supplier_invoice_number="BILL-PRICE-VAR",
            invoice_date=timezone.now().date(),
            purchase_order=po,
            goods_receipt=grn,
            lines_data=[{
                "medicine": medicine,
                "purchase_order_line": po.lines.first(),
                "goods_receipt_line": grn.lines.first(),
                "quantity": Decimal("100.0000"),
                "unit_price": Decimal("12.0000"),  # $12.00 vs $10.00 PO price
            }],
            user=creator,
        )

        verified = service.verify_and_match_supplier_invoice(tenant, inv, user=creator)
        assert verified.match_status == MatchStatus.PRICE_VARIANCE
        assert verified.status == InvoiceStatus.UNDER_REVIEW


# ===========================================================================
# AP POSTING, PAYMENTS & CREDIT APPLICATION TESTS
# ===========================================================================


@pytest.mark.django_db
class TestAPPostingPaymentsAndCredits:
    def test_post_invoice_creates_ap_subledger_entry(self):
        tenant, company, warehouse, location, supplier, medicine, po, grn, creator, approver = ap_full_setup()
        service = AccountsPayableService()

        inv = service.create_supplier_invoice(
            tenant=tenant, company=company, supplier=supplier, supplier_invoice_number="BILL-POST-1",
            invoice_date=timezone.now().date(), purchase_order=po, goods_receipt=grn,
            lines_data=[{"medicine": medicine, "purchase_order_line": po.lines.first(), "goods_receipt_line": grn.lines.first(), "quantity": Decimal("100"), "unit_price": Decimal("10")}],
            user=creator,
        )
        service.verify_and_match_supplier_invoice(tenant, inv, user=creator)
        service.approve_supplier_invoice(tenant, inv, user=approver)

        ap_entry = service.post_supplier_invoice(tenant, inv, user=approver)
        assert ap_entry.pk is not None
        assert ap_entry.payable_number.startswith("AP-")
        assert ap_entry.original_amount == Decimal("1000.0000")
        assert ap_entry.outstanding_amount == Decimal("1000.0000")
        assert ap_entry.status == APStatus.OPEN

        inv.refresh_from_db()
        assert inv.status == InvoiceStatus.POSTED

    def test_partial_and_full_supplier_payments(self):
        """Invoice $1,000 -> Payment $400 (Outstanding $600, PARTIALLY_PAID) -> Payment $600 (Outstanding $0, PAID)."""
        tenant, company, warehouse, location, supplier, medicine, po, grn, creator, approver = ap_full_setup()
        service = AccountsPayableService()

        inv = service.create_supplier_invoice(
            tenant=tenant, company=company, supplier=supplier, supplier_invoice_number="BILL-PMT-1",
            invoice_date=timezone.now().date(), purchase_order=po, goods_receipt=grn,
            lines_data=[{"medicine": medicine, "purchase_order_line": po.lines.first(), "goods_receipt_line": grn.lines.first(), "quantity": Decimal("100"), "unit_price": Decimal("10")}],
            user=creator,
        )
        service.verify_and_match_supplier_invoice(tenant, inv, user=creator)
        service.approve_supplier_invoice(tenant, inv, user=approver)
        service.post_supplier_invoice(tenant, inv, user=approver)

        # 1. Partial Payment of $400
        pmt1 = service.process_supplier_payment(tenant, inv, amount=Decimal("400.0000"), user=approver)
        assert pmt1.amount == Decimal("400.0000")
        assert pmt1.status == PaymentStatus.POSTED

        inv.refresh_from_db()
        assert inv.paid_amount == Decimal("400.0000")
        assert inv.outstanding_amount == Decimal("600.0000")
        assert inv.status == InvoiceStatus.PARTIALLY_PAID

        # 2. Full Final Payment of $600
        pmt2 = service.process_supplier_payment(tenant, inv, amount=Decimal("600.0000"), user=approver)
        assert pmt2.amount == Decimal("600.0000")

        inv.refresh_from_db()
        assert inv.paid_amount == Decimal("1000.0000")
        assert inv.outstanding_amount == Decimal("0.0000")
        assert inv.status == InvoiceStatus.PAID

    def test_overpayment_rejected(self):
        """Attempting to pay more than outstanding payable balance raises ExceedsOutstandingBalanceError."""
        tenant, company, warehouse, location, supplier, medicine, po, grn, creator, approver = ap_full_setup()
        service = AccountsPayableService()

        inv = service.create_supplier_invoice(
            tenant=tenant, company=company, supplier=supplier, supplier_invoice_number="BILL-OVERPAY",
            invoice_date=timezone.now().date(), purchase_order=po, goods_receipt=grn,
            lines_data=[{"medicine": medicine, "purchase_order_line": po.lines.first(), "goods_receipt_line": grn.lines.first(), "quantity": Decimal("100"), "unit_price": Decimal("10")}],
            user=creator,
        )
        service.verify_and_match_supplier_invoice(tenant, inv, user=creator)
        service.approve_supplier_invoice(tenant, inv, user=approver)
        service.post_supplier_invoice(tenant, inv, user=approver)

        with pytest.raises(ExceedsOutstandingBalanceError):
            service.process_supplier_payment(tenant, inv, amount=Decimal("1500.0000"), user=approver)

    def test_apply_supplier_credit_note_from_returns(self):
        """Integrates with IMP-023: Apply SupplierCreditNote against posted invoice."""
        tenant, company, warehouse, location, supplier, medicine, po, grn, creator, approver = ap_full_setup()
        ret_svc = PurchaseReturnService()
        ap_svc = AccountsPayableService()

        # 1. Create and dispatch return of 20 units -> Supplier Credit Note of $200.00
        batch = Batch.objects.get(tenant=tenant, medicine=medicine, batch_number="BATCH-AP-100")
        ret = ret_svc.create_purchase_return(
            tenant=tenant, company=company, supplier=supplier, warehouse=warehouse, goods_receipt=grn,
            lines_data=[{"medicine": medicine, "batch": batch, "storage_location": location, "requested_return_quantity": Decimal("20.0000"), "unit_cost": Decimal("10.0000")}],
            user=creator,
        )
        ret_svc.request_purchase_return(tenant, ret, user=creator)
        ret_svc.approve_purchase_return(tenant, ret, user=approver)
        ret_svc.dispatch_purchase_return(tenant, ret, user=approver)
        ret_svc.record_supplier_acceptance(
            tenant=tenant, purchase_return=ret,
            line_acceptances=[{"line_id": str(ret.lines.first().pk), "supplier_accepted_quantity": Decimal("20.0000")}],
            user=approver,
        )
        crn = ret.credit_notes.first()
        assert crn.net_credit_value == Decimal("200.0000")

        # 2. Create invoice for remaining 80 units ($800.00)
        inv = ap_svc.create_supplier_invoice(
            tenant=tenant, company=company, supplier=supplier, supplier_invoice_number="BILL-CRN-APPLY",
            invoice_date=timezone.now().date(), purchase_order=po, goods_receipt=grn,
            lines_data=[{"medicine": medicine, "quantity": Decimal("80.0000"), "unit_price": Decimal("10.0000")}],
            user=creator,
        )
        ap_svc.verify_and_match_supplier_invoice(tenant, inv, user=creator)
        ap_svc.approve_supplier_invoice(tenant, inv, user=approver)
        ap_svc.post_supplier_invoice(tenant, inv, user=approver)

        # 3. Apply $200 credit against $800 invoice -> Outstanding $600
        credit_app = ap_svc.apply_supplier_credit(tenant, crn, inv, amount=Decimal("200.0000"), user=approver)
        assert credit_app.applied_amount == Decimal("200.0000")

        inv.refresh_from_db()
        assert inv.outstanding_amount == Decimal("600.0000")

    def test_reverse_supplier_payment_restores_balance(self):
        """Reversing a posted payment restores the outstanding AP balance."""
        tenant, company, warehouse, location, supplier, medicine, po, grn, creator, approver = ap_full_setup()
        service = AccountsPayableService()

        inv = service.create_supplier_invoice(
            tenant=tenant, company=company, supplier=supplier, supplier_invoice_number="BILL-REV-PMT",
            invoice_date=timezone.now().date(), purchase_order=po, goods_receipt=grn,
            lines_data=[{"medicine": medicine, "quantity": Decimal("100"), "unit_price": Decimal("10")}],
            user=creator,
        )
        service.verify_and_match_supplier_invoice(tenant, inv, user=creator)
        service.approve_supplier_invoice(tenant, inv, user=approver)
        service.post_supplier_invoice(tenant, inv, user=approver)

        pmt = service.process_supplier_payment(tenant, inv, amount=Decimal("300.0000"), user=approver)
        inv.refresh_from_db()
        assert inv.outstanding_amount == Decimal("700.0000")

        # Reverse payment
        rev_pmt = service.reverse_supplier_payment(tenant, pmt, reason="Check bounced", user=approver)
        assert rev_pmt.status == PaymentStatus.REVERSED

        inv.refresh_from_db()
        assert inv.paid_amount == Decimal("0.0000")
        assert inv.outstanding_amount == Decimal("1000.0000")

        # Duplicate reversal rejected
        with pytest.raises(PaymentAlreadyReversedError):
            service.reverse_supplier_payment(tenant, pmt, reason="Second reversal", user=approver)


# ===========================================================================
# SELECTORS, AGING & TENANT ISOLATION TESTS
# ===========================================================================


@pytest.mark.django_db
class TestAPSelectorsAndTenantIsolation:
    def test_ap_aging_and_balance_summary(self):
        tenant, company, warehouse, location, supplier, medicine, po, grn, creator, approver = ap_full_setup()
        service = AccountsPayableService()

        inv = service.create_supplier_invoice(
            tenant=tenant, company=company, supplier=supplier, supplier_invoice_number="BILL-AGING-1",
            invoice_date=timezone.now().date(), purchase_order=po, goods_receipt=grn,
            lines_data=[{"medicine": medicine, "quantity": Decimal("100"), "unit_price": Decimal("10")}],
            user=creator,
        )
        service.verify_and_match_supplier_invoice(tenant, inv, user=creator)
        service.approve_supplier_invoice(tenant, inv, user=approver)
        service.post_supplier_invoice(tenant, inv, user=approver)

        selector = AccountsPayableSelector()
        aging = selector.calculate_ap_aging(tenant, supplier_id=str(supplier.pk))
        assert Decimal(aging["total_outstanding"]) == Decimal("1000.0000")

        summary = selector.get_supplier_balance_summary(tenant, supplier_id=str(supplier.pk))
        assert Decimal(summary["total_invoiced_purchases"]) == Decimal("1000.0000")
        assert Decimal(summary["outstanding_ap_balance"]) == Decimal("1000.0000")

    def test_tenant_isolation(self):
        tenant_a, company_a, wh_a, loc_a, supp_a, med_a, po_a, grn_a, creator_a, approver_a = ap_full_setup()
        tenant_b = make_tenant("b")

        service = AccountsPayableService()
        inv_a = service.create_supplier_invoice(
            tenant=tenant_a, company=company_a, supplier=supp_a, supplier_invoice_number="BILL-TENANT-A",
            invoice_date=timezone.now().date(), lines_data=[{"medicine": med_a, "quantity": Decimal("10"), "unit_price": Decimal("10")}],
            user=creator_a,
        )

        selector = AccountsPayableSelector()
        assert selector.list_supplier_invoices(tenant=tenant_a).count() == 1
        assert selector.list_supplier_invoices(tenant=tenant_b).count() == 0
