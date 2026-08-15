"""Comprehensive Test Suite for Enterprise Pharma E-Commerce & B2B Marketplace (IMP-036 / apps.commerce)."""

import uuid
from decimal import Decimal
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.branches.models import Branch
from apps.commerce.exceptions import (
    CreditLimitExceededError,
    InvalidCouponError,
    PrescriptionRequiredError,
    StockUnavailableError,
)
from apps.commerce.models import (
    Cart,
    CommerceOrder,
    CommerceOrderStatus,
    CommercePaymentStatus,
    CouponDiscountType,
    DeliveryMethod,
    OrderPrescription,
    PrescriptionReviewStatus,
    StoreCoupon,
    StoreProduct,
    StoreStatus,
    TenantStore,
)
from apps.commerce.selectors import CartSelector, CommerceOrderSelector, StoreCatalogSelector
from apps.commerce.services import (
    CartService,
    CheckoutService,
    CommercePaymentService,
    OrderFulfillmentService,
    PrescriptionReviewService,
)
from apps.companies.models import Company
from apps.core.models import Tenant
from apps.customers.models import Customer
from apps.inventory.models import Batch, InventoryItem
from apps.medicines.models import Medicine
from apps.warehouses.models import StorageLocation, Warehouse

User = get_user_model()


def commerce_setup():
    """Helper setup creating tenant, company, branch, warehouse, storage location, medicine, batches, inventory, store, and customer."""
    uid = uuid.uuid4().hex[:6]
    tenant = Tenant.objects.create(name=f"Commerce Tenant {uid}", code=f"TNT-{uid}", slug=f"commerce-slug-{uid}")
    company = Company.objects.create(tenant=tenant, legal_name=f"Commerce Corp {uid}", commercial_name="Commerce Corp", code=f"CMP-{uid[:4]}", slug=f"cmp-{uid}")
    branch = Branch.objects.create(tenant=tenant, company=company, name="Downtown Branch", code=f"BR-{uid[:4]}")
    warehouse = Warehouse.objects.create(tenant=tenant, company=company, branch=branch, name="Main Storage", code=f"WH-{uid[:4]}")
    loc = StorageLocation.objects.create(tenant=tenant, warehouse=warehouse, code=f"LOC-{uid[:4]}", name="Shelf 1")

    # Pharmacist User
    pharmacist = User.objects.create_user(email=f"pharmacist_{uid}@test.com", first_name="Pharm", last_name="User", password="pass")

    # Medicine 1: Standard OTC
    med_otc = Medicine.objects.create(
        tenant=tenant,
        company=company,
        english_name=f"Paracetamol 500mg {uid}",
        arabic_name=f"باراسيتامول {uid}",
        slug=f"paracetamol-{uid}",
        generic_name="Paracetamol",
        code=f"MED-OTC-{uid[:4]}",
        sku=f"SKU-OTC-{uid[:4]}",
        barcode=f"BAR-OTC-{uid[:4]}",
        prescription_type="otc",
    )
    batch_otc = Batch.objects.create(
        tenant=tenant,
        company=company,
        medicine=med_otc,
        batch_number=f"BATCH-OTC-{uid[:4]}",
        manufacturing_date=timezone.now().date(),
        expiry_date=timezone.now().date() + timezone.timedelta(days=365),
    )
    InventoryItem.objects.create(
        tenant=tenant,
        company=company,
        branch=branch,
        medicine=med_otc,
        batch=batch_otc,
        warehouse=warehouse,
        storage_location=loc,
        on_hand_quantity=Decimal("100.00"),
    )

    # Medicine 2: Prescription-Only
    med_rx = Medicine.objects.create(
        tenant=tenant,
        company=company,
        english_name=f"Amoxicillin 500mg {uid}",
        arabic_name=f"أموكسيسيلين {uid}",
        slug=f"amoxicillin-{uid}",
        generic_name="Amoxicillin",
        code=f"MED-RX-{uid[:4]}",
        sku=f"SKU-RX-{uid[:4]}",
        barcode=f"BAR-RX-{uid[:4]}",
        prescription_type="prescription_only",
    )
    batch_rx = Batch.objects.create(
        tenant=tenant,
        company=company,
        medicine=med_rx,
        batch_number=f"BATCH-RX-{uid[:4]}",
        manufacturing_date=timezone.now().date(),
        expiry_date=timezone.now().date() + timezone.timedelta(days=365),
    )
    InventoryItem.objects.create(
        tenant=tenant,
        company=company,
        branch=branch,
        medicine=med_rx,
        batch=batch_rx,
        warehouse=warehouse,
        storage_location=loc,
        on_hand_quantity=Decimal("50.00"),
    )

    # Tenant Store
    store = TenantStore.objects.create(
        tenant=tenant,
        code=f"STORE-{uid[:4]}",
        name="PharmaCloud Digital Store",
        currency="USD",
        delivery_fee=Decimal("5.00"),
        free_delivery_threshold=Decimal("50.00"),
    )

    # Store Products
    prod_otc = StoreProduct.objects.create(
        tenant=tenant,
        store=store,
        medicine=med_otc,
        display_name="Paracetamol 500mg (20 Tabs)",
        retail_price=Decimal("10.00"),
        b2b_price=Decimal("8.00"),
        is_published=True,
        is_prescription_required=False,
    )
    prod_rx = StoreProduct.objects.create(
        tenant=tenant,
        store=store,
        medicine=med_rx,
        display_name="Amoxicillin 500mg (Antibiotic)",
        retail_price=Decimal("20.00"),
        b2b_price=Decimal("15.00"),
        is_published=True,
        is_prescription_required=True,
    )

    # Customers (B2C and B2B)
    cust_b2c = Customer.objects.create(
        tenant=tenant,
        company=company,
        code=f"CUS-B2C-{uid[:4]}",
        customer_number=f"CN-B2C-{uid[:4]}",
        first_name="Jane",
        last_name="Retail",
        customer_type="individual",
    )
    cust_b2b = Customer.objects.create(
        tenant=tenant,
        company=company,
        code=f"CUS-B2B-{uid[:4]}",
        customer_number=f"CN-B2B-{uid[:4]}",
        first_name="Dr. Smith",
        last_name="Clinic",
        customer_type="clinic",
        credit_limit=Decimal("1000.00"),
        current_balance=Decimal("0.00"),
    )

    return tenant, company, branch, warehouse, pharmacist, store, prod_otc, prod_rx, cust_b2c, cust_b2b


@pytest.mark.django_db
class TestTenantStoreAndCatalog:
    """Test suite for storefront setup, product publishing, catalog search, and tenant isolation."""

    def test_catalog_search_and_stock(self):
        tenant, company, branch, warehouse, pharmacist, store, prod_otc, prod_rx, cust_b2c, cust_b2b = commerce_setup()
        selector = StoreCatalogSelector()

        # Search OTC medicine
        results = selector.list_published_products(store, search_query="Paracetamol")
        assert len(results) == 1
        assert results[0]["display_name"] == "Paracetamol 500mg (20 Tabs)"
        assert results[0]["available_stock"] == 100.0
        assert results[0]["retail_price"] == 10.0

    def test_tenant_isolation(self):
        # Tenant 1
        t1, c1, b1, w1, p1, s1, prod1, _, _, _ = commerce_setup()
        # Tenant 2
        t2, c2, b2, w2, p2, s2, prod2, _, _, _ = commerce_setup()

        selector = StoreCatalogSelector()
        results_s1 = selector.list_published_products(s1)
        results_s2 = selector.list_published_products(s2)

        s1_prod_ids = [p["id"] for p in results_s1]
        s2_prod_ids = [p["id"] for p in results_s2]

        assert prod1.pk in s1_prod_ids
        assert prod1.pk not in s2_prod_ids
        assert prod2.pk in s2_prod_ids
        assert prod2.pk not in s1_prod_ids


@pytest.mark.django_db
class TestShoppingCartAndMerging:
    """Test suite for cart modifications, totals calculation, and guest-to-customer cart merge."""

    def test_cart_operations_and_totals(self):
        tenant, company, branch, warehouse, pharmacist, store, prod_otc, prod_rx, cust_b2c, cust_b2b = commerce_setup()
        cart_service = CartService()
        cart_selector = CartSelector()

        cart = cart_service.get_or_create_cart(store, customer=cust_b2c)
        cart_service.add_to_cart(cart, prod_otc, quantity=Decimal("2"))  # 2 * $10 = $20

        summary = cart_selector.calculate_cart_summary(cart)
        assert summary["subtotal"] == 20.0
        assert summary["delivery_fee"] == 5.0  # < $50 threshold
        assert summary["total"] == 25.0
        assert summary["items_count"] == 1

        # Add more items to trigger free delivery
        cart_service.add_to_cart(cart, prod_otc, quantity=Decimal("4"))  # 6 * $10 = $60
        summary2 = cart_selector.calculate_cart_summary(cart)
        assert summary2["subtotal"] == 60.0
        assert summary2["delivery_fee"] == 0.0  # Free delivery
        assert summary2["total"] == 60.0

    def test_merge_guest_cart_into_customer_cart(self):
        tenant, company, branch, warehouse, pharmacist, store, prod_otc, prod_rx, cust_b2c, cust_b2b = commerce_setup()
        cart_service = CartService()

        guest_cart = cart_service.get_or_create_cart(store, session_key="guest_sess_123")
        cart_service.add_to_cart(guest_cart, prod_otc, quantity=Decimal("1"))

        cust_cart = cart_service.get_or_create_cart(store, customer=cust_b2c)
        cart_service.add_to_cart(cust_cart, prod_otc, quantity=Decimal("2"))

        cart_service.merge_guest_cart(guest_cart, cust_cart)

        cust_cart.refresh_from_db()
        assert cust_cart.items.count() == 1
        item = cust_cart.items.first()
        assert item.quantity == Decimal("3.00")
        assert not Cart.objects.filter(pk=guest_cart.pk, is_deleted=False).exists()


@pytest.mark.django_db
class TestPricingCouponsAndCheckout:
    """Test suite for server-side price enforcement, coupons, B2B wholesale pricing, and credit checks."""

    def test_checkout_server_side_price_and_coupon(self):
        tenant, company, branch, warehouse, pharmacist, store, prod_otc, prod_rx, cust_b2c, cust_b2b = commerce_setup()
        cart_service = CartService()
        checkout_service = CheckoutService()

        # Create 10% coupon
        StoreCoupon.objects.create(
            tenant=tenant,
            store=store,
            code="SAVE10",
            discount_type=CouponDiscountType.PERCENTAGE,
            discount_value=Decimal("10.00"),
            is_active=True,
        )

        cart = cart_service.get_or_create_cart(store, customer=cust_b2c)
        cart_service.add_to_cart(cart, prod_otc, quantity=Decimal("2"))  # $20.00 subtotal

        order = checkout_service.checkout_cart(
            cart,
            customer=cust_b2c,
            shipping_address="123 Health Ave",
            coupon_code="SAVE10",
            branch=branch,
            warehouse=warehouse,
        )

        assert order.subtotal == Decimal("20.00")
        assert order.discount_amount == Decimal("2.00")  # 10% of 20
        assert order.shipping_fee == Decimal("5.00")
        assert order.total_amount == Decimal("23.00")  # 20 - 2 + 5
        assert order.status == CommerceOrderStatus.PENDING

    def test_b2b_wholesale_pricing_and_credit_limit(self):
        tenant, company, branch, warehouse, pharmacist, store, prod_otc, prod_rx, cust_b2c, cust_b2b = commerce_setup()
        cart_service = CartService()
        checkout_service = CheckoutService()

        cart = cart_service.get_or_create_cart(store, customer=cust_b2b)
        cart_service.add_to_cart(cart, prod_otc, quantity=Decimal("10"))  # B2B price is $8.00 -> $80.00

        order = checkout_service.checkout_cart(
            cart,
            customer=cust_b2b,
            branch=branch,
            warehouse=warehouse,
        )

        assert order.subtotal == Decimal("80.00")
        assert order.total_amount == Decimal("80.00")  # Free delivery threshold met

        # Exceed credit limit test
        cust_b2b.current_balance = Decimal("980.00")
        cust_b2b.credit_limit = Decimal("1000.00")
        cust_b2b.save(update_fields=["current_balance", "credit_limit"])

        cart2 = cart_service.get_or_create_cart(store, customer=cust_b2b)
        cart_service.add_to_cart(cart2, prod_otc, quantity=Decimal("5"))  # 5 * $8 = $40 (exceeds $20 available credit)

        with pytest.raises(CreditLimitExceededError):
            checkout_service.checkout_cart(cart2, customer=cust_b2b, branch=branch, warehouse=warehouse)


@pytest.mark.django_db
class TestPrescriptionsAndFulfillment:
    """Test suite for prescription upload, pharmacist review, and stock movement fulfillment."""

    def test_prescription_order_workflow_and_fulfillment(self):
        tenant, company, branch, warehouse, pharmacist, store, prod_otc, prod_rx, cust_b2c, cust_b2b = commerce_setup()
        cart_service = CartService()
        checkout_service = CheckoutService()
        review_service = PrescriptionReviewService()
        fulfillment_service = OrderFulfillmentService()

        cart = cart_service.get_or_create_cart(store, customer=cust_b2c)
        cart_service.add_to_cart(cart, prod_rx, quantity=Decimal("1"))

        # 1. Attempt checkout without prescription URL -> Fails
        with pytest.raises(PrescriptionRequiredError):
            checkout_service.checkout_cart(cart, customer=cust_b2c, branch=branch, warehouse=warehouse)

        # 2. Checkout with prescription URL -> Creates OrderPrescription with UPLOADED status
        order = checkout_service.checkout_cart(
            cart,
            customer=cust_b2c,
            branch=branch,
            warehouse=warehouse,
            prescription_file_url="https://secure-storage.pharmacloud/rx/12345.pdf",
        )

        rx = order.prescriptions.first()
        assert rx is not None
        assert rx.review_status == PrescriptionReviewStatus.UPLOADED

        # 3. Attempt fulfillment before approval -> Fails
        with pytest.raises(PrescriptionRequiredError):
            fulfillment_service.fulfill_and_dispatch_order(order, user=pharmacist)

        # 4. Pharmacist approves prescription
        review_service.approve_prescription(rx, pharmacist_user=pharmacist, notes="Valid Rx from Dr. House")
        rx.refresh_from_db()
        assert rx.review_status == PrescriptionReviewStatus.APPROVED

        # 5. Fulfill and dispatch order -> Deducts stock via StockMovementEngine
        delivery = fulfillment_service.fulfill_and_dispatch_order(order, courier_name="DHL Pharma", user=pharmacist)
        order.refresh_from_db()

        assert order.status == CommerceOrderStatus.OUT_FOR_DELIVERY
        assert delivery.courier_name == "DHL Pharma"
        assert delivery.tracking_number.startswith("TRK-")


@pytest.mark.django_db
class TestPaymentsRefundsAndIdempotency:
    """Test suite for payment settlement, partial refunds, and idempotent checkout."""

    def test_payment_and_refund(self):
        tenant, company, branch, warehouse, pharmacist, store, prod_otc, prod_rx, cust_b2c, cust_b2b = commerce_setup()
        cart_service = CartService()
        checkout_service = CheckoutService()
        payment_service = CommercePaymentService()

        cart = cart_service.get_or_create_cart(store, customer=cust_b2c)
        cart_service.add_to_cart(cart, prod_otc, quantity=Decimal("2"))
        order = checkout_service.checkout_cart(cart, customer=cust_b2c, branch=branch, warehouse=warehouse)

        # Pay
        payment = payment_service.process_payment(order, amount=order.total_amount, payment_method="card")
        order.refresh_from_db()
        assert payment.status == CommercePaymentStatus.PAID
        assert order.payment_status == CommercePaymentStatus.PAID

        # Partial Refund
        refund = payment_service.refund_payment(payment, refund_amount=Decimal("10.00"), reason="Returned 1 item")
        payment.refresh_from_db()
        order.refresh_from_db()
        assert payment.status == CommercePaymentStatus.PARTIALLY_REFUNDED
        assert refund.amount == Decimal("10.00")

    def test_idempotent_checkout(self):
        tenant, company, branch, warehouse, pharmacist, store, prod_otc, prod_rx, cust_b2c, cust_b2b = commerce_setup()
        cart_service = CartService()
        checkout_service = CheckoutService()

        cart = cart_service.get_or_create_cart(store, customer=cust_b2c)
        cart_service.add_to_cart(cart, prod_otc, quantity=Decimal("1"))

        idemp_key = "idemp_checkout_xyz_999"
        order1 = checkout_service.checkout_cart(
            cart,
            customer=cust_b2c,
            branch=branch,
            warehouse=warehouse,
            idempotency_key=idemp_key,
        )

        # Retry with same key
        order2 = checkout_service.checkout_cart(
            cart,
            customer=cust_b2c,
            branch=branch,
            warehouse=warehouse,
            idempotency_key=idemp_key,
        )

        assert order1.pk == order2.pk
        assert CommerceOrder.objects.filter(idempotency_key=idemp_key).count() == 1
