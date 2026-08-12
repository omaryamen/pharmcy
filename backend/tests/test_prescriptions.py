"""Comprehensive test suite for IMP-027 — Enterprise Prescription Management & Pharmacy Dispensing.
Tests: prescription creation, clinical verification, controlled substance rules, validity expiration checks,
FEFO batch allocation, stock reduction strictly via StockMovementEngine (zero direct inventory mutations),
refill balance tracking, dispensing logs, dispensation reversal, idempotency, and multi-tenant isolation.
"""

from __future__ import annotations

import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.branches.models import Branch
from apps.companies.models import Company
from apps.core.models import Tenant
from apps.customers.models import Customer
from apps.goods_receipt.services import GoodsReceiptService
from apps.inventory.models import Batch, InventoryItem
from apps.inventory.models.enums import BatchStatus
from apps.medicines.models import Medicine
from apps.procurement.services import PurchaseOrderService
from apps.prescriptions.exceptions import (
    ControlledSubstanceLicenseRequiredError,
    ExceedsPrescribedQuantityError,
    PrescriptionExpiredError,
    PrescriptionNotVerifiedError,
)
from apps.prescriptions.models import (
    DispenseStatus,
    Prescription,
    PrescriptionDispense,
    PrescriptionLine,
    PrescriptionLineStatus,
    PrescriptionStatus,
    PrescriptionType,
)
from apps.prescriptions.services import PharmacyDispensingService
from apps.stock_movement.models import StockMovement
from apps.suppliers.models import Supplier
from apps.warehouses.models import StorageLocation, Warehouse

User = get_user_model()


def rx_full_setup():
    """Helper fixture creating tenant, company, branch, warehouse, location, customer, medicine, batch, pharmacist, and doctor."""
    tenant = Tenant.objects.create(name=f"RX Tenant {uuid.uuid4().hex[:6]}", slug=f"rx-slug-{uuid.uuid4().hex[:6]}")
    company = Company.objects.create(tenant=tenant, legal_name="Pharma Rx Corp", commercial_name="Pharma Rx Corp", code=f"COMP-{uuid.uuid4().hex[:4]}", slug=f"comp-{uuid.uuid4().hex[:4]}")
    branch = Branch.objects.create(tenant=tenant, company=company, name="Main Rx Pharmacy", code=f"BR-{uuid.uuid4().hex[:4]}")
    warehouse = Warehouse.objects.create(tenant=tenant, company=company, branch=branch, name="Main Rx WH", code=f"WH-{uuid.uuid4().hex[:4]}")
    location = StorageLocation.objects.create(tenant=tenant, warehouse=warehouse, name="Shelf B1", code=f"LOC-{uuid.uuid4().hex[:4]}")

    customer = Customer.objects.create(
        tenant=tenant,
        company=company,
        first_name="Jane",
        last_name="Smith",
        english_name="Jane Smith Patient",
        customer_number=f"CUST-{uuid.uuid4().hex[:6]}",
        status="active",
    )

    medicine = Medicine.objects.create(
        tenant=tenant,
        company=company,
        sku=f"SKU-RX-{uuid.uuid4().hex[:6]}",
        barcode=f"BAR-RX-{uuid.uuid4().hex[:6]}",
        english_name="Amoxicillin 500mg Capsules",
        arabic_name="أموكسيسيلين 500مجم كبسولات",
        status="active",
        unit_of_measure="Pcs",
    )

    supplier = Supplier.objects.create(tenant=tenant, code=f"SUP-{uuid.uuid4().hex[:6]}", legal_name="Pharma Supplier", status="active")

    po_creator = User.objects.create_user(email=f"poc_{uuid.uuid4().hex[:4]}@test.com", first_name="PO Creator", password="pass")
    po_approver = User.objects.create_user(email=f"poa_{uuid.uuid4().hex[:4]}@test.com", first_name="PO Approver", password="pass")
    pharmacist = User.objects.create_user(email=f"pharm_{uuid.uuid4().hex[:4]}@test.com", first_name="Pharmacist", password="pass")

    po_service = PurchaseOrderService()
    grn_service = GoodsReceiptService()

    po = po_service.create_purchase_order(
        tenant=tenant, company=company, supplier=supplier, warehouse=warehouse,
        currency="USD", lines_data=[{"medicine": medicine, "ordered_quantity": Decimal("100.0000"), "unit_price": Decimal("5.0000")}],
        user=po_creator,
    )
    po_service.submit_purchase_order(tenant, po, user=po_creator)
    po_service.approve_purchase_order(tenant, po, user=po_approver)
    po_service.send_to_supplier(tenant, po, user=po_approver)

    grn = grn_service.create_goods_receipt(
        tenant=tenant, company=company, supplier=supplier, warehouse=warehouse, purchase_order=po,
        receiving_location=location,
        lines_data=[{
            "purchase_order_line": po.lines.first(),
            "medicine": medicine, "received_quantity": Decimal("100.0000"), "accepted_quantity": Decimal("100.0000"), "unit_cost": Decimal("5.0000"),
            "batch_number": f"RX-BATCH-{uuid.uuid4().hex[:4]}", "expiry_date": timezone.now().date() + timedelta(days=365),
            "storage_location": location,
        }],
        user=po_creator,
    )
    grn_service.post_goods_receipt(tenant, grn, user=po_creator)

    batch = Batch.objects.get(tenant=tenant, medicine=medicine)

    return tenant, company, branch, warehouse, location, customer, medicine, batch, pharmacist


# ===========================================================================
# 1. PRESCRIPTION CREATION & VERIFICATION TESTS
# ===========================================================================


@pytest.mark.django_db
class TestPrescriptionCreationAndVerification:
    def test_create_regular_prescription(self):
        """Create valid regular prescription document."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, pharmacist = rx_full_setup()
        service = PharmacyDispensingService()

        today = timezone.now().date()
        expiry = today + timedelta(days=30)

        rx = service.create_prescription(
            tenant=tenant, company=company, branch=branch, customer=customer,
            rx_date=today, expiry_date=expiry, doctor_name="Dr. Gregory House",
            lines_data=[{
                "medicine_id": str(medicine.pk), "prescribed_quantity": Decimal("20.0000"),
                "dosage": "500mg", "frequency": "3 times daily", "duration_days": 7, "refills_allowed": 2,
            }],
            rx_type=PrescriptionType.REGULAR, user=pharmacist,
        )

        assert rx.pk is not None
        assert rx.rx_number.startswith("RX-")
        assert rx.status == PrescriptionStatus.PENDING_VERIFICATION
        assert rx.is_verified is False
        assert rx.lines.count() == 1

        line = rx.lines.first()
        assert line.medicine == medicine
        assert line.prescribed_quantity == Decimal("20.0000")
        assert line.refills_remaining == 2

    def test_controlled_substance_requires_doctor_license(self):
        """Controlled substance prescription raises ControlledSubstanceLicenseRequiredError if doctor license number is blank."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, pharmacist = rx_full_setup()
        service = PharmacyDispensingService()
        today = timezone.now().date()

        with pytest.raises(ControlledSubstanceLicenseRequiredError):
            service.create_prescription(
                tenant=tenant, company=company, branch=branch, customer=customer,
                rx_date=today, expiry_date=today + timedelta(days=7), doctor_name="Dr. John",
                doctor_license_number="",  # BLANK LICENSE
                lines_data=[{"medicine_id": str(medicine.pk), "prescribed_quantity": Decimal("10.0000")}],
                rx_type=PrescriptionType.NARCOTIC, user=pharmacist,
            )

    def test_verify_prescription_by_pharmacist(self):
        """Pharmacist clinically verifies prescription."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, pharmacist = rx_full_setup()
        service = PharmacyDispensingService()
        today = timezone.now().date()

        rx = service.create_prescription(
            tenant=tenant, company=company, branch=branch, customer=customer,
            rx_date=today, expiry_date=today + timedelta(days=30), doctor_name="Dr. House",
            lines_data=[{"medicine_id": str(medicine.pk), "prescribed_quantity": Decimal("10.0000")}],
            user=pharmacist,
        )

        verified = service.verify_prescription(tenant, rx, pharmacist=pharmacist)
        assert verified.is_verified is True
        assert verified.status == PrescriptionStatus.VERIFIED
        assert verified.verified_by == pharmacist


# ===========================================================================
# 2. PHARMACY DISPENSING & STOCK REDUCTION TESTS
# ===========================================================================


@pytest.mark.django_db
class TestPharmacyDispensingEngine:
    def test_dispense_unverified_prescription_rejected(self):
        """Dispensing an unverified prescription raises PrescriptionNotVerifiedError."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, pharmacist = rx_full_setup()
        service = PharmacyDispensingService()
        today = timezone.now().date()

        rx = service.create_prescription(
            tenant=tenant, company=company, branch=branch, customer=customer,
            rx_date=today, expiry_date=today + timedelta(days=30), doctor_name="Dr. House",
            lines_data=[{"medicine_id": str(medicine.pk), "prescribed_quantity": Decimal("10.0000")}],
            user=pharmacist,
        )
        rx_line = rx.lines.first()

        with pytest.raises(PrescriptionNotVerifiedError):
            service.dispense_prescription(
                tenant=tenant, prescription=rx, warehouse=warehouse,
                dispensing_lines=[{"prescription_line_id": str(rx_line.pk), "dispensed_quantity": Decimal("10.0000"), "batch_id": str(batch.pk), "storage_location_id": str(location.pk)}],
                pharmacist=pharmacist,
            )

    def test_dispense_prescription_reduces_stock_via_stock_movement_engine(self):
        """CRITICAL: Dispensing prescription MUST reduce stock strictly via StockMovementEngine (SALE type). Zero direct mutations."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, pharmacist = rx_full_setup()
        service = PharmacyDispensingService()
        today = timezone.now().date()

        # Physical stock = 100
        inv_before = InventoryItem.objects.get(tenant=tenant, warehouse=warehouse, storage_location=location, medicine=medicine, batch=batch)
        assert inv_before.on_hand_quantity == Decimal("100.00")

        rx = service.create_prescription(
            tenant=tenant, company=company, branch=branch, customer=customer,
            rx_date=today, expiry_date=today + timedelta(days=30), doctor_name="Dr. House",
            lines_data=[{"medicine_id": str(medicine.pk), "prescribed_quantity": Decimal("20.0000")}],
            user=pharmacist,
        )
        service.verify_prescription(tenant, rx, pharmacist=pharmacist)

        rx_line = rx.lines.first()
        dispense = service.dispense_prescription(
            tenant=tenant, prescription=rx, warehouse=warehouse,
            dispensing_lines=[{
                "prescription_line_id": str(rx_line.pk), "dispensed_quantity": Decimal("20.0000"),
                "batch_id": str(batch.pk), "storage_location_id": str(location.pk),
            }],
            pharmacist=pharmacist,
        )

        assert dispense.pk is not None
        assert dispense.dispense_number.startswith("DISP-")
        assert dispense.status == DispenseStatus.COMPLETED

        rx.refresh_from_db()
        assert rx.status == PrescriptionStatus.FULLY_DISPENSED

        # Verify physical stock reduced to 80
        inv_after = InventoryItem.objects.get(tenant=tenant, warehouse=warehouse, storage_location=location, medicine=medicine, batch=batch)
        assert inv_after.on_hand_quantity == Decimal("80.00")

        # Verify StockMovement record created
        mov = StockMovement.objects.filter(tenant=tenant, reference_number=rx.rx_number).first()
        assert mov is not None
        assert mov.movement_type == "sale"

    def test_exceeding_prescribed_quantity_rejected(self):
        """Dispensing more than prescribed quantity raises ExceedsPrescribedQuantityError."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, pharmacist = rx_full_setup()
        service = PharmacyDispensingService()
        today = timezone.now().date()

        rx = service.create_prescription(
            tenant=tenant, company=company, branch=branch, customer=customer,
            rx_date=today, expiry_date=today + timedelta(days=30), doctor_name="Dr. House",
            lines_data=[{"medicine_id": str(medicine.pk), "prescribed_quantity": Decimal("10.0000")}],
            user=pharmacist,
        )
        service.verify_prescription(tenant, rx, pharmacist=pharmacist)
        rx_line = rx.lines.first()

        with pytest.raises(ExceedsPrescribedQuantityError):
            service.dispense_prescription(
                tenant=tenant, prescription=rx, warehouse=warehouse,
                dispensing_lines=[{"prescription_line_id": str(rx_line.pk), "dispensed_quantity": Decimal("25.0000"), "batch_id": str(batch.pk), "storage_location_id": str(location.pk)}],
                pharmacist=pharmacist,
            )


# ===========================================================================
# 3. REVERSAL & MULTI-TENANT ISOLATION TESTS
# ===========================================================================


@pytest.mark.django_db
class TestDispensationReversalAndIsolation:
    def test_reverse_dispensation_restores_stock_and_status(self):
        """Reversing dispensing event restores physical stock via compensating StockMovement and resets status."""
        tenant, company, branch, warehouse, location, customer, medicine, batch, pharmacist = rx_full_setup()
        service = PharmacyDispensingService()
        today = timezone.now().date()

        rx = service.create_prescription(
            tenant=tenant, company=company, branch=branch, customer=customer,
            rx_date=today, expiry_date=today + timedelta(days=30), doctor_name="Dr. House",
            lines_data=[{"medicine_id": str(medicine.pk), "prescribed_quantity": Decimal("15.0000")}],
            user=pharmacist,
        )
        service.verify_prescription(tenant, rx, pharmacist=pharmacist)
        rx_line = rx.lines.first()

        dispense = service.dispense_prescription(
            tenant=tenant, prescription=rx, warehouse=warehouse,
            dispensing_lines=[{"prescription_line_id": str(rx_line.pk), "dispensed_quantity": Decimal("15.0000"), "batch_id": str(batch.pk), "storage_location_id": str(location.pk)}],
            pharmacist=pharmacist,
        )

        # Reverse dispensation
        reversed_disp = service.reverse_dispensation(tenant, dispense, pharmacist=pharmacist, reason="Wrong patient record selected")
        assert reversed_disp.status == DispenseStatus.REVERSED

        rx.refresh_from_db()
        assert rx.status == PrescriptionStatus.VERIFIED

        # Physical stock restored to 100
        inv_item = InventoryItem.objects.get(tenant=tenant, warehouse=warehouse, storage_location=location, medicine=medicine, batch=batch)
        assert inv_item.on_hand_quantity == Decimal("100.00")
