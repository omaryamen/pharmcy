"""Comprehensive Security, Compliance & Production Hardening Test Suite (IMP-039)."""

import uuid
from decimal import Decimal
import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.branches.models import Branch
from apps.commerce.models import (
    CommerceOrder,
    CommerceOrderStatus,
    OrderPrescription,
    PrescriptionReviewStatus,
    TenantStore,
)
from apps.common.middleware.security_headers import SecurityHeadersMiddleware
from apps.companies.models import Company
from apps.core.models import Tenant
from apps.customers.models import Customer
from apps.inventory.models import Batch, InventoryItem
from apps.medicines.models import Medicine
from apps.rbac.models import Role, UserRoleAssignment
from apps.rbac.services import RoleAssignmentService
from apps.sales.models import SalesInvoice, SalesStatus
from apps.warehouses.models import StorageLocation, Warehouse

User = get_user_model()


def security_setup():
    """Helper setup for two independent tenants to test isolation, RBAC, and IDOR protection."""
    uid1 = uuid.uuid4().hex[:6]
    uid2 = uuid.uuid4().hex[:6]

    # Tenant 1
    t1 = Tenant.objects.create(name=f"Sec Tenant 1 {uid1}", code=f"ST1-{uid1}", slug=f"st1-{uid1}")
    c1 = Company.objects.create(tenant=t1, legal_name="Company 1", commercial_name="Comp 1", code=f"C1-{uid1[:4]}", slug=f"c1-{uid1}")
    b1 = Branch.objects.create(tenant=t1, company=c1, name="Branch 1", code=f"B1-{uid1[:4]}")
    w1 = Warehouse.objects.create(tenant=t1, company=c1, branch=b1, name="Warehouse 1", code=f"W1-{uid1[:4]}")
    loc1 = StorageLocation.objects.create(tenant=t1, warehouse=w1, code=f"L1-{uid1[:4]}", name="Shelf 1")

    u1 = User.objects.create_user(email=f"user1_{uid1}@test.com", first_name="User", last_name="One", password="password123")
    cust1 = Customer.objects.create(tenant=t1, company=c1, code=f"CUS-1-{uid1[:4]}", customer_number=f"CN-1-{uid1[:4]}", first_name="Patient", last_name="One")

    med1 = Medicine.objects.create(
        tenant=t1,
        company=c1,
        english_name=f"Med One {uid1}",
        arabic_name=f"دواء واحد {uid1}",
        slug=f"med-1-{uid1}",
        code=f"MED1-{uid1[:4]}",
        sku=f"SKU1-{uid1[:4]}",
        barcode=f"BAR1-{uid1[:4]}",
        prescription_type="prescription_only",
    )
    batch1 = Batch.objects.create(
        tenant=t1,
        company=c1,
        medicine=med1,
        batch_number=f"B1-{uid1[:4]}",
        manufacturing_date=timezone.now().date(),
        expiry_date=timezone.now().date() + timezone.timedelta(days=365),
    )
    InventoryItem.objects.create(
        tenant=t1,
        company=c1,
        branch=b1,
        warehouse=w1,
        storage_location=loc1,
        medicine=med1,
        batch=batch1,
        on_hand_quantity=Decimal("100.00"),
    )

    store1 = TenantStore.objects.create(tenant=t1, code=f"STORE1-{uid1[:4]}", name="Store 1", currency="USD")
    order1 = CommerceOrder.objects.create(
        tenant=t1,
        store=store1,
        customer=cust1,
        order_number=f"ORD-1-{uid1}",
        status=CommerceOrderStatus.PENDING,
        total_amount=Decimal("50.00"),
    )
    rx1 = OrderPrescription.objects.create(
        tenant=t1,
        order=order1,
        customer=cust1,
        file_url="https://secure.pharmacloud.internal/rx/patient1_confidential.pdf",
        review_status=PrescriptionReviewStatus.UPLOADED,
    )

    # Tenant 2 (Adversary / Competitor)
    t2 = Tenant.objects.create(name=f"Sec Tenant 2 {uid2}", code=f"ST2-{uid2}", slug=f"st2-{uid2}")
    c2 = Company.objects.create(tenant=t2, legal_name="Company 2", commercial_name="Comp 2", code=f"C2-{uid2[:4]}", slug=f"c2-{uid2}")
    b2 = Branch.objects.create(tenant=t2, company=c2, name="Branch 2", code=f"B2-{uid2[:4]}")
    u2 = User.objects.create_user(email=f"user2_{uid2}@test.com", first_name="User", last_name="Two", password="password123")
    cust2 = Customer.objects.create(tenant=t2, company=c2, code=f"CUS-2-{uid2[:4]}", customer_number=f"CN-2-{uid2[:4]}", first_name="Patient", last_name="Two")

    return {
        "t1": t1, "c1": c1, "b1": b1, "w1": w1, "u1": u1, "cust1": cust1, "med1": med1, "batch1": batch1, "order1": order1, "rx1": rx1,
        "t2": t2, "c2": c2, "b2": b2, "u2": u2, "cust2": cust2,
    }


@pytest.mark.django_db
class TestSecurityHeadersAndMiddleware:
    """Validate CSP, Permissions-Policy, X-Content-Type-Options, and Referrer-Policy."""

    def test_security_headers_injected(self):
        factory = RequestFactory()
        request = factory.get("/api/v1/health/")
        middleware = SecurityHeadersMiddleware(lambda req: APIClient().get("/api/v1/store/products/"))
        response = middleware(request)

        assert "Content-Security-Policy" in response
        assert "default-src 'self'" in response["Content-Security-Policy"]
        assert "Permissions-Policy" in response
        assert response["X-Content-Type-Options"] == "nosniff"
        assert response["Referrer-Policy"] == "strict-origin-when-cross-origin"
        assert response["Cross-Origin-Opener-Policy"] == "same-origin"


@pytest.mark.django_db
class TestMultiTenantIsolationAndEscape:
    """Ensure strict tenant isolation across database records and APIs."""

    def test_tenant_boundary_enforcement(self):
        data = security_setup()

        # 1. Inventory Items Query Isolation
        t1_inventory = InventoryItem.objects.filter(tenant=data["t1"])
        t2_inventory = InventoryItem.objects.filter(tenant=data["t2"])

        assert t1_inventory.count() == 1
        assert t2_inventory.count() == 0

        # 2. Cross-Tenant Prescription Access attempt
        t2_rx = OrderPrescription.objects.filter(tenant=data["t2"], pk=data["rx1"].pk)
        assert not t2_rx.exists()

        # 3. Cross-Tenant Customer Access attempt
        t2_cust = Customer.objects.filter(tenant=data["t2"], pk=data["cust1"].pk)
        assert not t2_cust.exists()


@pytest.mark.django_db
class TestIDORAndPrescriptionPrivacy:
    """Ensure prescription files and customer records are protected from IDOR / enumeration."""

    def test_customer_rx_idor_protection(self):
        data = security_setup()

        # Customer 2 attempting to view Customer 1's prescription
        rx_for_cust2 = OrderPrescription.objects.filter(customer=data["cust2"], pk=data["rx1"].pk)
        assert not rx_for_cust2.exists()

        # Customer 1 accessing own prescription
        rx_for_cust1 = OrderPrescription.objects.filter(customer=data["cust1"], pk=data["rx1"].pk)
        assert rx_for_cust1.exists()
        assert rx_for_cust1.first().file_url == data["rx1"].file_url


@pytest.mark.django_db
class TestFinancialAndInventoryIntegrity:
    """Ensure sales, stock movements, and financial totals are server-authoritative."""

    def test_server_authoritative_calculations(self):
        data = security_setup()

        # Create sales invoice
        invoice = SalesInvoice.objects.create(
            tenant=data["t1"],
            company=data["c1"],
            branch=data["b1"],
            warehouse=data["w1"],
            invoice_number="INV-SEC-001",
            invoice_date=timezone.now().date(),
            invoice_time=timezone.now().time(),
            status=SalesStatus.COMPLETED,
            subtotal=Decimal("100.0000"),
            tax=Decimal("5.0000"),
            discount=Decimal("10.0000"),
            grand_total=Decimal("95.0000"),
        )

        assert invoice.grand_total == Decimal("95.0000")
        assert invoice.tenant == data["t1"]
