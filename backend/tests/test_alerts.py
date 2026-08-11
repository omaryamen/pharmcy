"""Comprehensive test suite for IMP-020 — Enterprise Expiry, Recall & Inventory Alert Management.
Tests: models, AlertScannerService, BatchRecallService, automatic stock quarantining via StockMovementEngine,
alert acknowledgment, resolution, selectors, statistics, and tenant isolation.
"""

from __future__ import annotations

import uuid
from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.alerts.exceptions import AlertAlreadyResolvedError, InvalidAlertStateError, RecallAlreadyInitiatedError
from apps.alerts.models import (
    AlertConfiguration,
    AlertSeverity,
    AlertStatus,
    AlertType,
    BatchRecall,
    InventoryAlert,
    RecallClass,
    RecallStatus,
    RecallType,
)
from apps.alerts.selectors import BatchRecallSelector, InventoryAlertSelector
from apps.alerts.services import AlertScannerService, BatchRecallService
from apps.companies.models import Company
from apps.core.models import Tenant
from apps.inventory.models import Batch, InventoryItem
from apps.medicines.models import Medicine
from apps.stock_movement.models import StockMovement
from apps.warehouses.models import StorageLocation, Warehouse

User = get_user_model()


# ---------------------------------------------------------------------------
# Test data factories
# ---------------------------------------------------------------------------

def make_tenant(suffix=""):
    code = "alt-" + uuid.uuid4().hex[:6] + suffix
    return Tenant.objects.create(name=f"Alert Tenant {code}", code=code, slug=code)


def make_company(tenant, code=None):
    code = code or ("CO-" + uuid.uuid4().hex[:6])
    return Company.objects.create(tenant=tenant, code=code, legal_name=f"Company {code}")


def make_warehouse(tenant, company, name="Warehouse"):
    code = "WH-" + uuid.uuid4().hex[:6]
    return Warehouse.objects.create(tenant=tenant, company=company, code=code, name=f"{name} {code}")


def make_location(tenant, warehouse, name="Location"):
    code = "LOC-" + uuid.uuid4().hex[:6]
    return StorageLocation.objects.create(tenant=tenant, warehouse=warehouse, code=code, name=f"{name} {code}")


def make_medicine(tenant, name="Amoxicillin 500mg"):
    code = "MED-" + uuid.uuid4().hex[:6]
    return Medicine.objects.create(
        tenant=tenant,
        code=code,
        sku=code,
        english_name=name,
        arabic_name="دواء",
    )


def make_batch(tenant, company, medicine, expiry_days=365, status="active"):
    return Batch.objects.create(
        tenant=tenant,
        company=company,
        medicine=medicine,
        batch_number="BATCH-" + uuid.uuid4().hex[:8],
        manufacturing_date=timezone.now().date() - timedelta(days=30),
        expiry_date=timezone.now().date() + timedelta(days=expiry_days),
        unit_cost=Decimal("10.0000"),
        selling_price=Decimal("15.0000"),
        status=status,
    )


def make_inventory_item(tenant, company, medicine, batch, warehouse, location, qty=Decimal("100"), reorder_point=Decimal("20")):
    item, _ = InventoryItem.objects.get_or_create(
        tenant=tenant,
        medicine=medicine,
        batch=batch,
        warehouse=warehouse,
        storage_location=location,
        defaults={
            "company": company,
            "on_hand_quantity": qty,
            "reserved_quantity": Decimal("0"),
            "damaged_quantity": Decimal("0"),
            "quarantine_quantity": Decimal("0"),
            "reorder_point": reorder_point,
            "unit_cost": Decimal("10.0000"),
        },
    )
    return item


def make_user(email=None):
    email = email or f"u-{uuid.uuid4().hex[:8]}@test.com"
    return User.objects.create_user(email=email, first_name="TestUser", password="Pass123!")


def full_alert_setup(qty=Decimal("100"), expiry_days=365, reorder_point=Decimal("20")):
    """Return (tenant, company, warehouse, location, medicine, batch, inv_item, user)."""
    tenant = make_tenant()
    company = make_company(tenant)
    warehouse = make_warehouse(tenant, company)
    location = make_location(tenant, warehouse)
    medicine = make_medicine(tenant)
    batch = make_batch(tenant, company, medicine, expiry_days=expiry_days)
    inv_item = make_inventory_item(tenant, company, medicine, batch, warehouse, location, qty=qty, reorder_point=reorder_point)
    user = make_user()
    return tenant, company, warehouse, location, medicine, batch, inv_item, user


# ===========================================================================
# MODEL TESTS
# ===========================================================================


@pytest.mark.django_db
class TestAlertModels:
    def test_create_inventory_alert_model(self):
        tenant, company, warehouse, location, medicine, batch, _, _ = full_alert_setup()
        alert = InventoryAlert.objects.create(
            tenant=tenant,
            company=company,
            warehouse=warehouse,
            storage_location=location,
            medicine=medicine,
            batch=batch,
            alert_number="ALT-2026-000001",
            alert_type=AlertType.LOW_STOCK,
            severity=AlertSeverity.HIGH,
            status=AlertStatus.ACTIVE,
            title="Low Stock Warning",
            message="Stock level is below threshold.",
            current_value=Decimal("5.0000"),
            threshold_value=Decimal("20.0000"),
            triggered_at=timezone.now(),
        )

        assert alert.pk is not None
        assert alert.alert_number == "ALT-2026-000001"
        assert alert.severity == AlertSeverity.HIGH
        assert alert.status == AlertStatus.ACTIVE

    def test_create_batch_recall_model(self):
        tenant, company, _, _, medicine, batch, _, user = full_alert_setup()
        recall = BatchRecall.objects.create(
            tenant=tenant,
            company=company,
            medicine=medicine,
            batch=batch,
            recall_number="RCL-2026-000001",
            recall_type=RecallType.REGULATORY_FDA,
            recall_class=RecallClass.CLASS_1_CRITICAL,
            status=RecallStatus.DRAFT,
            reason="Impurity detected in stability testing.",
            action_required="Quarantine and return immediately.",
            initiated_by=user,
        )

        assert recall.pk is not None
        assert recall.recall_number == "RCL-2026-000001"
        assert recall.recall_class == RecallClass.CLASS_1_CRITICAL
        assert recall.status == RecallStatus.DRAFT


# ===========================================================================
# ALERT SCANNER SERVICE TESTS
# ===========================================================================


@pytest.mark.django_db
class TestAlertScannerService:
    def test_scan_generates_out_of_stock_alert(self):
        tenant, company, warehouse, location, medicine, batch, inv_item, user = full_alert_setup(qty=Decimal("0"))
        scanner = AlertScannerService()

        res = scanner.scan_inventory_alerts(tenant=tenant)
        assert res["alerts_created"] >= 1

        alert = InventoryAlert.objects.filter(tenant=tenant, medicine=medicine, alert_type=AlertType.OUT_OF_STOCK).first()
        assert alert is not None
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.status == AlertStatus.ACTIVE

    def test_scan_generates_low_stock_alert(self):
        tenant, company, warehouse, location, medicine, batch, inv_item, user = full_alert_setup(qty=Decimal("15"), reorder_point=Decimal("20"))
        scanner = AlertScannerService()

        res = scanner.scan_inventory_alerts(tenant=tenant)
        assert res["alerts_created"] >= 1

        alert = InventoryAlert.objects.filter(tenant=tenant, medicine=medicine, alert_type=AlertType.LOW_STOCK).first()
        assert alert is not None
        assert alert.current_value == Decimal("15.0000")
        assert alert.threshold_value == Decimal("20.0000")

    def test_scan_generates_near_expiry_alert(self):
        tenant, company, warehouse, location, medicine, batch, inv_item, user = full_alert_setup(qty=Decimal("50"), expiry_days=45)
        scanner = AlertScannerService()

        res = scanner.scan_inventory_alerts(tenant=tenant, near_expiry_days=90)
        assert res["alerts_created"] >= 1

        alert = InventoryAlert.objects.filter(tenant=tenant, batch=batch, alert_type=AlertType.EXPIRY_WARNING).first()
        assert alert is not None
        assert alert.status == AlertStatus.ACTIVE

    def test_scan_generates_expired_batch_alert(self):
        tenant, company, warehouse, location, medicine, batch, inv_item, user = full_alert_setup(qty=Decimal("50"), expiry_days=-5)
        scanner = AlertScannerService()

        res = scanner.scan_inventory_alerts(tenant=tenant)
        assert res["alerts_created"] >= 1

        alert = InventoryAlert.objects.filter(tenant=tenant, batch=batch, alert_type=AlertType.EXPIRED).first()
        assert alert is not None
        assert alert.severity == AlertSeverity.CRITICAL

    def test_scan_is_idempotent_and_updates_existing_alert(self):
        tenant, company, warehouse, location, medicine, batch, inv_item, user = full_alert_setup(qty=Decimal("15"), reorder_point=Decimal("20"))
        scanner = AlertScannerService()

        scanner.scan_inventory_alerts(tenant=tenant)
        count_after_first = InventoryAlert.objects.filter(tenant=tenant).count()

        # Update item quantity to 10 and scan again
        inv_item.on_hand_quantity = Decimal("10.00")
        inv_item.save(update_fields=["on_hand_quantity"])

        scanner.scan_inventory_alerts(tenant=tenant)
        count_after_second = InventoryAlert.objects.filter(tenant=tenant).count()

        assert count_after_first == count_after_second
        alert = InventoryAlert.objects.filter(tenant=tenant, medicine=medicine, alert_type=AlertType.LOW_STOCK).first()
        assert alert.current_value == Decimal("10.0000")

    def test_acknowledge_and_resolve_alert_lifecycle(self):
        tenant, company, warehouse, location, medicine, batch, inv_item, user = full_alert_setup(qty=Decimal("0"))
        scanner = AlertScannerService()
        scanner.scan_inventory_alerts(tenant=tenant)

        alert = InventoryAlert.objects.filter(tenant=tenant, medicine=medicine).first()
        assert alert.status == AlertStatus.ACTIVE

        # Acknowledge
        ack_alert = scanner.acknowledge_alert(tenant, alert, user=user)
        assert ack_alert.status == AlertStatus.ACKNOWLEDGED
        assert ack_alert.acknowledged_by == user

        # Resolve
        res_alert = scanner.resolve_alert(tenant, ack_alert, resolution_notes="PO #9921 placed to replenish stock.", user=user)
        assert res_alert.status == AlertStatus.RESOLVED
        assert res_alert.resolution_notes == "PO #9921 placed to replenish stock."


# ===========================================================================
# BATCH RECALL SERVICE TESTS
# ===========================================================================


@pytest.mark.django_db
class TestBatchRecallService:
    def test_complete_batch_recall_workflow_with_auto_quarantine(self):
        """Test BatchRecall initiation, batch status update, and automated stock quarantine via StockMovementEngine."""
        tenant, company, warehouse, location, medicine, batch, inv_item, user = full_alert_setup(qty=Decimal("80"))
        recall_svc = BatchRecallService()

        # 1. Create Recall Draft
        recall = recall_svc.create_recall(
            tenant=tenant,
            company=company,
            medicine=medicine,
            batch=batch,
            reason="Quality defect in active pharmaceutical ingredient.",
            recall_type=RecallType.REGULATORY_FDA,
            recall_class=RecallClass.CLASS_1_CRITICAL,
            user=user,
        )
        assert recall.status == RecallStatus.DRAFT

        # 2. Initiate Recall with Auto-Quarantine
        movements_before = StockMovement.objects.filter(tenant=tenant).count()
        initiated = recall_svc.initiate_recall(tenant=tenant, recall=recall, auto_quarantine=True, user=user)
        movements_after = StockMovement.objects.filter(tenant=tenant).count()

        assert initiated.status == RecallStatus.QUARANTINED
        assert initiated.quarantined_quantity == Decimal("80.0000")
        assert movements_after > movements_before

        # Check Batch status updated to recalled
        batch.refresh_from_db()
        assert batch.status == "recalled"

        # Check InventoryItem quarantine quantity updated
        inv_item.refresh_from_db()
        assert inv_item.quarantine_quantity == Decimal("80.0000")
        assert inv_item.available_quantity == Decimal("0.0000")

        # 3. Complete Recall
        completed = recall_svc.complete_recall(
            tenant=tenant,
            recall=initiated,
            disposed_quantity=Decimal("80.0000"),
            user=user,
        )
        assert completed.status == RecallStatus.COMPLETED
        assert completed.disposed_quantity == Decimal("80.0000")

    def test_cannot_reinitiate_already_initiated_recall(self):
        tenant, company, warehouse, location, medicine, batch, inv_item, user = full_alert_setup(qty=Decimal("50"))
        recall_svc = BatchRecallService()

        recall = recall_svc.create_recall(tenant, company, medicine, batch, reason="Defect", user=user)
        recall_svc.initiate_recall(tenant, recall, auto_quarantine=False, user=user)
        recall.refresh_from_db()

        with pytest.raises(RecallAlreadyInitiatedError):
            recall_svc.initiate_recall(tenant, recall, auto_quarantine=False, user=user)


# ===========================================================================
# SELECTOR & TENANT ISOLATION TESTS
# ===========================================================================


@pytest.mark.django_db
class TestAlertSelectorsAndTenantIsolation:
    def test_alert_statistics_aggregation(self):
        tenant, company, warehouse, location, medicine, batch, inv_item, user = full_alert_setup(qty=Decimal("0"))
        scanner = AlertScannerService()
        scanner.scan_inventory_alerts(tenant=tenant)

        selector = InventoryAlertSelector()
        stats = selector.get_alert_statistics(tenant=tenant)

        assert stats["total_active_alerts"] >= 1
        assert stats["critical_alerts"] >= 1

    def test_tenant_isolation_hides_other_tenant_alerts(self):
        tenant_a, company_a, wh_a, loc_a, med_a, batch_a, _, user_a = full_alert_setup(qty=Decimal("0"))
        tenant_b = make_tenant("b")

        scanner = AlertScannerService()
        scanner.scan_inventory_alerts(tenant=tenant_a)

        selector = InventoryAlertSelector()
        alerts_a = selector.list_alerts(tenant=tenant_a)
        alerts_b = selector.list_alerts(tenant=tenant_b)

        assert alerts_a.count() >= 1
        assert alerts_b.count() == 0
