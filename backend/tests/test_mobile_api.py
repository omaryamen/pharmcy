"""Comprehensive Test Suite for Enterprise Customer & Pharmacy Mobile Application API Platform (IMP-037 / apps.mobile_api)."""

import uuid
from decimal import Decimal
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.alerts.models import AlertSeverity, AlertStatus, AlertType, InventoryAlert
from apps.branches.models import Branch
from apps.commerce.models import (
    CommerceOrder,
    CommerceOrderStatus,
    OrderPrescription,
    PrescriptionReviewStatus,
    StoreProduct,
    TenantStore,
)
from apps.companies.models import Company
from apps.core.models import Tenant
from apps.customers.models import Customer
from apps.inventory.models import Batch, InventoryItem
from apps.medicines.models import Medicine
from apps.mobile_api.exceptions import SyncConflictError
from apps.mobile_api.models import (
    Device,
    DevicePlatform,
    MobileAppVersion,
    MobileSyncQueue,
    SyncOperation,
    SyncStatus,
)
from apps.mobile_api.selectors import (
    CustomerDashboardSelector,
    PharmacyOwnerMobileSelector,
    PharmacistMobileSelector,
)
from apps.mobile_api.services import (
    DeviceRegistrationService,
    MobileAppConfigService,
    MobileSyncService,
)
from apps.platform_ops.models import GlobalFeatureFlag
from apps.sales.models import SalesInvoice, SalesStatus
from apps.warehouses.models import StorageLocation, Warehouse

User = get_user_model()


def mobile_setup():
    """Helper setup creating tenant, company, branch, warehouse, medicine, customer, store, user."""
    uid = uuid.uuid4().hex[:6]
    tenant = Tenant.objects.create(name=f"Mobile Tenant {uid}", code=f"TNT-{uid}", slug=f"mobile-slug-{uid}")
    company = Company.objects.create(tenant=tenant, legal_name=f"Mobile Corp {uid}", commercial_name="Mobile Corp", code=f"CMP-{uid[:4]}", slug=f"cmp-{uid}")
    branch = Branch.objects.create(tenant=tenant, company=company, name="Central Branch", code=f"BR-{uid[:4]}")
    warehouse = Warehouse.objects.create(tenant=tenant, company=company, branch=branch, name="Main Storage", code=f"WH-{uid[:4]}")
    loc = StorageLocation.objects.create(tenant=tenant, warehouse=warehouse, code=f"LOC-{uid[:4]}", name="Shelf 1")

    user = User.objects.create_user(email=f"mob_user_{uid}@test.com", first_name="Mobile", last_name="User", password="pass")
    pharmacist = User.objects.create_user(email=f"mob_pharm_{uid}@test.com", first_name="Pharm", last_name="Lead", password="pass")

    med = Medicine.objects.create(
        tenant=tenant,
        company=company,
        english_name=f"Ibuprofen 400mg {uid}",
        arabic_name=f"إيبوبروفين {uid}",
        slug=f"ibuprofen-{uid}",
        generic_name="Ibuprofen",
        code=f"MED-IBU-{uid[:4]}",
        sku=f"SKU-IBU-{uid[:4]}",
        barcode=f"BAR-IBU-{uid[:4]}",
        prescription_type="otc",
    )
    batch = Batch.objects.create(
        tenant=tenant,
        company=company,
        medicine=med,
        batch_number=f"BATCH-IBU-{uid[:4]}",
        manufacturing_date=timezone.now().date(),
        expiry_date=timezone.now().date() + timezone.timedelta(days=365),
    )
    InventoryItem.objects.create(
        tenant=tenant,
        company=company,
        branch=branch,
        medicine=med,
        batch=batch,
        warehouse=warehouse,
        storage_location=loc,
        on_hand_quantity=Decimal("150.00"),
    )

    store = TenantStore.objects.create(
        tenant=tenant,
        code=f"MOB-STORE-{uid[:4]}",
        name="Mobile Pharmacy Store",
        currency="USD",
    )
    prod = StoreProduct.objects.create(
        tenant=tenant,
        store=store,
        medicine=med,
        display_name="Ibuprofen 400mg (Pain Relief)",
        retail_price=Decimal("12.00"),
        b2b_price=Decimal("9.00"),
        is_published=True,
        is_featured=True,
    )

    customer = Customer.objects.create(
        tenant=tenant,
        company=company,
        code=f"CUS-MOB-{uid[:4]}",
        customer_number=f"CN-MOB-{uid[:4]}",
        first_name="Alice",
        last_name="Mobile",
        customer_type="individual",
    )

    return tenant, company, branch, warehouse, user, pharmacist, store, prod, customer


@pytest.mark.django_db
class TestDeviceRegistrationAndRevocation:
    """Test suite for device registration, push token updating, and revocation."""

    def test_register_and_revoke_device(self):
        tenant, company, branch, warehouse, user, pharmacist, store, prod, customer = mobile_setup()
        device_service = DeviceRegistrationService()

        # Register device
        device = device_service.register_device(
            user=user,
            tenant=tenant,
            device_identifier="android_uuid_9988",
            platform=DevicePlatform.ANDROID,
            push_token="fcm_token_sample_123",
            app_version="1.2.0",
            os_version="Android 14",
        )

        assert device.is_active is True
        assert device.push_token == "fcm_token_sample_123"
        assert device.platform == DevicePlatform.ANDROID

        # Update push token on same device
        device_updated = device_service.register_device(
            user=user,
            tenant=tenant,
            device_identifier="android_uuid_9988",
            platform=DevicePlatform.ANDROID,
            push_token="fcm_token_rotated_456",
            app_version="1.2.1",
        )
        assert device.pk == device_updated.pk
        assert device_updated.push_token == "fcm_token_rotated_456"

        # Revoke device
        revoked = device_service.revoke_device(user, "android_uuid_9988")
        assert revoked is True
        device_updated.refresh_from_db()
        assert device_updated.is_active is False


@pytest.mark.django_db
class TestMobileAppConfiguration:
    """Test suite for app version policy, force updates, and remote feature flags."""

    def test_app_config_and_feature_flags(self):
        tenant, company, branch, warehouse, user, pharmacist, store, prod, customer = mobile_setup()
        config_service = MobileAppConfigService()

        MobileAppVersion.objects.create(
            platform=DevicePlatform.IOS,
            min_version="2.0.0",
            recommended_version="2.1.0",
            is_force_update=True,
            maintenance_mode=False,
        )

        GlobalFeatureFlag.objects.create(
            feature_key="ai_prescription_scanner",
            name="AI Scanner",
            is_globally_enabled=True,
        )

        config = config_service.get_mobile_config(platform=DevicePlatform.IOS, tenant=tenant)

        assert config["min_version"] == "2.0.0"
        assert config["is_force_update"] is True
        assert config["feature_flags"]["ai_prescription_scanner"] is True
        assert config["feature_flags"]["offline_pos_sync"] is False


@pytest.mark.django_db
class TestCustomerAndOwnerMobileDashboards:
    """Test suite for customer home screen and pharmacy owner mobile dashboards."""

    def test_customer_mobile_dashboard(self):
        tenant, company, branch, warehouse, user, pharmacist, store, prod, customer = mobile_setup()
        dashboard_selector = CustomerDashboardSelector()

        # Create active order
        order = CommerceOrder.objects.create(
            tenant=tenant,
            store=store,
            customer=customer,
            order_number="ORD-2026-TEST01",
            status=CommerceOrderStatus.PENDING,
            total_amount=Decimal("24.00"),
            currency="USD",
        )

        # Create uploaded prescription
        OrderPrescription.objects.create(
            tenant=tenant,
            order=order,
            customer=customer,
            file_url="https://storage.pharmacloud/rx/test.pdf",
            review_status=PrescriptionReviewStatus.UPLOADED,
        )

        data = dashboard_selector.get_customer_dashboard(customer)

        assert data["customer_id"] == str(customer.pk)
        assert data["active_orders_count"] == 1
        assert data["pending_prescriptions_count"] == 1
        assert len(data["featured_products"]) == 1

    def test_pharmacy_owner_mobile_dashboard(self):
        tenant, company, branch, warehouse, user, pharmacist, store, prod, customer = mobile_setup()
        owner_selector = PharmacyOwnerMobileSelector()

        # Create a completed sales invoice today
        SalesInvoice.objects.create(
            tenant=tenant,
            company=company,
            branch=branch,
            warehouse=warehouse,
            invoice_number="INV-2026-TEST01",
            invoice_date=timezone.now().date(),
            invoice_time=timezone.now().time(),
            status=SalesStatus.COMPLETED,
            grand_total=Decimal("150.00"),
        )

        # Create Low Stock Inventory Alert
        InventoryAlert.objects.create(
            tenant=tenant,
            company=company,
            medicine=prod.medicine,
            warehouse=warehouse,
            alert_number="ALT-2026-TEST01",
            alert_type=AlertType.LOW_STOCK,
            severity=AlertSeverity.HIGH,
            status=AlertStatus.ACTIVE,
            title="Low stock on Ibuprofen",
            message="Stock level at 5 units",
            triggered_at=timezone.now(),
        )

        dashboard = owner_selector.get_owner_dashboard(tenant)

        assert dashboard["tenant_id"] == str(tenant.pk)
        assert dashboard["today_sales"] == 150.0
        assert dashboard["low_stock_alerts_count"] == 1
        assert dashboard["total_stock_units"] == 150.0


@pytest.mark.django_db
class TestPharmacistMobileQueue:
    """Test suite for pharmacist prescription queue and review."""

    def test_pharmacist_queue(self):
        tenant, company, branch, warehouse, user, pharmacist, store, prod, customer = mobile_setup()
        pharmacist_selector = PharmacistMobileSelector()

        order = CommerceOrder.objects.create(
            tenant=tenant,
            store=store,
            customer=customer,
            order_number="ORD-2026-RXQUEUE",
            status=CommerceOrderStatus.PENDING,
            total_amount=Decimal("50.00"),
            currency="USD",
        )
        OrderPrescription.objects.create(
            tenant=tenant,
            order=order,
            customer=customer,
            file_url="https://storage.pharmacloud/rx/queue.jpg",
            review_status=PrescriptionReviewStatus.UPLOADED,
        )

        queue = pharmacist_selector.get_pharmacist_queue(tenant)

        assert queue["pending_ecommerce_prescriptions_count"] == 1
        assert queue["ecommerce_prescriptions"][0]["order__order_number"] == "ORD-2026-RXQUEUE"


@pytest.mark.django_db
class TestMobileOfflineSync:
    """Test suite for offline mutation queuing, idempotency, and version conflict detection."""

    def test_offline_sync_and_conflict_handling(self):
        tenant, company, branch, warehouse, user, pharmacist, store, prod, customer = mobile_setup()
        sync_service = MobileSyncService()

        # 1. Normal sync item
        sync_item = sync_service.process_sync_item(
            tenant=tenant,
            user=user,
            entity_type="count_line",
            client_mutation_id="mut_item_001",
            operation=SyncOperation.CREATE,
            payload={"product_id": str(prod.pk), "counted_qty": 50},
            client_version=1,
        )
        assert sync_item.status == SyncStatus.APPLIED

        # 2. Idempotent re-submission
        sync_item_dup = sync_service.process_sync_item(
            tenant=tenant,
            user=user,
            entity_type="count_line",
            client_mutation_id="mut_item_001",
            operation=SyncOperation.CREATE,
            payload={"product_id": str(prod.pk), "counted_qty": 50},
            client_version=1,
        )
        assert sync_item.pk == sync_item_dup.pk

        # 3. Version conflict detection (client at version 1 when server is at version 3)
        with pytest.raises(SyncConflictError, match="is behind server version"):
            sync_service.process_sync_item(
                tenant=tenant,
                user=user,
                entity_type="order_status",
                client_mutation_id="mut_item_002",
                operation=SyncOperation.UPDATE,
                payload={"order_id": "123", "server_expected_version": 3},
                client_version=1,
            )
