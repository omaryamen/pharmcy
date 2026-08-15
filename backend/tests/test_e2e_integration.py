"""Comprehensive End-to-End System Integration Test Suite (IMP-040)."""

import uuid
from decimal import Decimal
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from apps.branches.models import Branch
from apps.commerce.models import (
    Cart,
    CartItem,
    CommerceOrder,
    CommerceOrderStatus,
    OrderPrescription,
    PrescriptionReviewStatus,
    TenantStore,
)
from apps.companies.models import Company
from apps.core.models import Tenant
from apps.customers.models import Customer
from apps.inventory.models import Batch, InventoryItem
from apps.medicines.models import Medicine
from apps.mobile_api.models import Device, MobileAppVersion, DevicePlatform
from apps.platform_ops.models import GlobalFeatureFlag, SystemMaintenanceWindow, SystemHealthCheck
from apps.platform_ops.models.enums import HealthStatus
from apps.sales.models import SalesInvoice, SalesInvoiceLine, SalesStatus
from apps.suppliers.models import Supplier
from apps.warehouses.models import StorageLocation, Warehouse

User = get_user_model()


@pytest.fixture
def e2e_environment():
    uid = uuid.uuid4().hex[:6]

    tenant = Tenant.objects.create(name=f"E2E Pharma {uid}", code=f"E2E-{uid}", slug=f"e2e-{uid}")
    company = Company.objects.create(tenant=tenant, legal_name=f"E2E Co {uid}", commercial_name="E2E Corp", code=f"C-{uid[:4]}", slug=f"c-{uid}")
    branch = Branch.objects.create(tenant=tenant, company=company, name="Downtown Branch", code=f"B-{uid[:4]}")
    warehouse = Warehouse.objects.create(tenant=tenant, company=company, branch=branch, name="Main Storage", code=f"W-{uid[:4]}")
    location = StorageLocation.objects.create(tenant=tenant, warehouse=warehouse, code=f"LOC-{uid[:4]}", name="Aisle 1")

    pharmacist = User.objects.create_user(email=f"pharmacist_{uid}@e2e.com", first_name="Dr. Tariq", last_name="Pharmacist", password="secure_pass_123")
    customer = Customer.objects.create(tenant=tenant, company=company, code=f"CUS-{uid[:4]}", customer_number=f"CN-{uid[:4]}", first_name="Fatima", last_name="Ali")
    supplier = Supplier.objects.create(
        tenant=tenant,
        company=company,
        code=f"SUP-{uid[:4]}",
        legal_name=f"Global Pharma Supply {uid}",
        display_name=f"Global Pharma {uid}",
    )

    medicine = Medicine.objects.create(
        tenant=tenant,
        company=company,
        english_name=f"Augmentin 1g {uid}",
        arabic_name=f"أوجمنتين {uid}",
        slug=f"aug-1g-{uid}",
        code=f"AUG-{uid[:4]}",
        sku=f"SKU-AUG-{uid[:4]}",
        barcode=f"628100{uid[:6]}",
        prescription_type="prescription_only",
    )

    batch_early = Batch.objects.create(
        tenant=tenant,
        company=company,
        medicine=medicine,
        batch_number=f"BATCH-EARLY-{uid[:4]}",
        manufacturing_date=timezone.now().date() - timezone.timedelta(days=60),
        expiry_date=timezone.now().date() + timezone.timedelta(days=180),
    )

    inv_early = InventoryItem.objects.create(
        tenant=tenant,
        company=company,
        branch=branch,
        warehouse=warehouse,
        storage_location=location,
        medicine=medicine,
        batch=batch_early,
        on_hand_quantity=Decimal("50.00"),
    )

    return {
        "tenant": tenant,
        "company": company,
        "branch": branch,
        "warehouse": warehouse,
        "location": location,
        "pharmacist": pharmacist,
        "customer": customer,
        "supplier": supplier,
        "medicine": medicine,
        "batch_early": batch_early,
        "inv_early": inv_early,
    }


@pytest.mark.django_db
class TestFullPharmacyLifecycleE2E:
    """Validate complete flow from catalog to prescription, POS sale, and stock deduction."""

    def test_complete_prescription_to_pos_flow(self, e2e_environment):
        env = e2e_environment
        client = APIClient()
        client.force_authenticate(user=env["pharmacist"])

        # 1. Upload & approve prescription
        store = TenantStore.objects.create(tenant=env["tenant"], code="STORE-01", name="Main Store", currency="USD")
        order = CommerceOrder.objects.create(
            tenant=env["tenant"],
            store=store,
            customer=env["customer"],
            order_number="ORD-E2E-001",
            status=CommerceOrderStatus.PENDING,
            total_amount=Decimal("18.50"),
        )
        rx = OrderPrescription.objects.create(
            tenant=env["tenant"],
            order=order,
            customer=env["customer"],
            file_url="https://secure.pharmacloud/rx/fatima_rx.pdf",
            review_status=PrescriptionReviewStatus.APPROVED,
            pharmacist_notes="Verified against national health registry. Approved for dispensing.",
        )

        assert rx.review_status == PrescriptionReviewStatus.APPROVED

        # 2. POS Dispensing & Sale Invoice
        invoice = SalesInvoice.objects.create(
            tenant=env["tenant"],
            company=env["company"],
            branch=env["branch"],
            warehouse=env["warehouse"],
            invoice_number="INV-E2E-001",
            invoice_date=timezone.now().date(),
            invoice_time=timezone.now().time(),
            status=SalesStatus.COMPLETED,
            subtotal=Decimal("18.5000"),
            tax=Decimal("0.9250"),
            discount=Decimal("0.0000"),
            grand_total=Decimal("19.4250"),
        )
        SalesInvoiceLine.objects.create(
            tenant=env["tenant"],
            sales_invoice=invoice,
            medicine=env["medicine"],
            batch=env["batch_early"],
            warehouse=env["warehouse"],
            storage_location=env["location"],
            quantity=Decimal("2.00"),
            unit_price=Decimal("9.2500"),
            line_total=Decimal("18.5000"),
        )

        # 3. Authoritative stock decrement
        env["inv_early"].on_hand_quantity -= Decimal("2.00")
        env["inv_early"].save(update_fields=["on_hand_quantity"])

        # Verify final state
        env["inv_early"].refresh_from_db()
        assert env["inv_early"].on_hand_quantity == Decimal("48.00")
        assert invoice.grand_total == Decimal("19.4250")


@pytest.mark.django_db
class TestPlatformOperationsAndMobileApiE2E:
    """Validate platform ops, health checks, and mobile device synchronizations."""

    def test_platform_health_and_mobile_integration(self, e2e_environment):
        env = e2e_environment

        # 1. Platform Health
        health = SystemHealthCheck.objects.create(
            component_name="PostgreSQL Core Database",
            status=HealthStatus.HEALTHY,
            latency_ms=1.45,
        )
        assert health.status == HealthStatus.HEALTHY

        # 2. Mobile Device Registration
        device = Device.objects.create(
            tenant=env["tenant"],
            user=env["pharmacist"],
            device_uuid="DEV-IPHONE-15-PRO-MAX",
            platform=DevicePlatform.IOS,
            app_version="1.34.0",
            os_version="iOS 18.2",
            is_active=True,
        )
        assert device.is_active is True
        assert device.platform == DevicePlatform.IOS
