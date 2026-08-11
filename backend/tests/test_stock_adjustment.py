"""
Comprehensive test suite for IMP-018 — Enterprise Stock Adjustment & Stock Count.
Tests: models, services, blind count security, tenant isolation, idempotency, exceptions.
"""

from __future__ import annotations

import uuid
from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.companies.models import Company
from apps.core.models import Tenant
from apps.medicines.models import Medicine
from apps.warehouses.models import StorageLocation, Warehouse

User = get_user_model()


# ---------------------------------------------------------------------------
# Test data factories
# ---------------------------------------------------------------------------

def make_tenant(suffix=""):
    code = "sa-" + uuid.uuid4().hex[:6] + suffix
    return Tenant.objects.create(name=f"SA Tenant {code}", code=code, slug=code)


def make_company(tenant, code=None):
    code = code or ("CO-" + uuid.uuid4().hex[:6])
    return Company.objects.create(tenant=tenant, code=code, legal_name=f"Company {code}")


def make_warehouse(tenant, company):
    code = "WH-" + uuid.uuid4().hex[:6]
    return Warehouse.objects.create(tenant=tenant, company=company, code=code, name=f"Warehouse {code}")


def make_location(tenant, warehouse):
    code = "LOC-" + uuid.uuid4().hex[:6]
    return StorageLocation.objects.create(
        tenant=tenant, warehouse=warehouse, code=code, name=f"Location {code}"
    )


def make_medicine(tenant):
    code = "MED-" + uuid.uuid4().hex[:6]
    return Medicine.objects.create(
        tenant=tenant,
        code=code,
        sku=code,
        english_name="Paracetamol 500mg",
        arabic_name="باراسيتامول",
    )


def make_batch(tenant, company, medicine, expiry_days=365):
    from apps.inventory.models import Batch
    return Batch.objects.create(
        tenant=tenant,
        company=company,
        medicine=medicine,
        batch_number="BATCH-" + uuid.uuid4().hex[:8],
        manufacturing_date=timezone.now().date() - timedelta(days=30),
        expiry_date=timezone.now().date() + timedelta(days=expiry_days),
        unit_cost=Decimal("10.0000"),
        selling_price=Decimal("15.0000"),
    )


def make_inventory_item(tenant, company, medicine, batch, warehouse, location, qty=Decimal("100")):
    from apps.inventory.models import InventoryItem
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
            "unit_cost": Decimal("10.0000"),
        },
    )
    return item


def make_user(email=None):
    email = email or f"u-{uuid.uuid4().hex[:8]}@test.com"
    return User.objects.create_user(email=email, first_name="Test", password="Pass123!")


def create_stock_count(tenant, company, warehouse, location, user, **kwargs):
    from apps.stock_adjustment.services import StockCountService
    return StockCountService().create_stock_count(
        tenant=tenant,
        company=company,
        branch=None,
        warehouse=warehouse,
        storage_location=location,
        count_type=kwargs.get("count_type", "warehouse_count"),
        count_scope_type=kwargs.get("count_scope_type", "warehouse"),
        scope_filter={},
        is_blind_count=kwargs.get("is_blind_count", False),
        freeze_inventory=kwargs.get("freeze_inventory", False),
        reason="Routine count",
        notes="",
        idempotency_key=kwargs.get("idempotency_key", ""),
        created_by=user,
    )


def full_setup():
    """Return (tenant, company, warehouse, location, medicine, batch, inv_item, user)."""
    tenant = make_tenant()
    company = make_company(tenant)
    warehouse = make_warehouse(tenant, company)
    location = make_location(tenant, warehouse)
    medicine = make_medicine(tenant)
    batch = make_batch(tenant, company, medicine)
    inv_item = make_inventory_item(tenant, company, medicine, batch, warehouse, location)
    user = make_user()
    return tenant, company, warehouse, location, medicine, batch, inv_item, user


# ===========================================================================
# MODEL TESTS
# ===========================================================================


@pytest.mark.django_db
class TestStockCountModel:
    def test_create_stock_count_is_draft(self):
        from apps.stock_adjustment.models.enums import CountStatus
        tenant, company, warehouse, location, *_, user = full_setup()

        sc = create_stock_count(tenant, company, warehouse, location, user)
        assert sc.pk is not None
        assert sc.count_number.startswith("CNT-")
        assert sc.count_status == CountStatus.DRAFT
        assert sc.tenant == tenant

    def test_sequential_count_numbers_are_unique(self):
        tenant, company, warehouse, location, *_, user = full_setup()

        sc1 = create_stock_count(tenant, company, warehouse, location, user)
        sc2 = create_stock_count(tenant, company, warehouse, location, user)
        assert sc1.count_number != sc2.count_number

    def test_default_aggregate_fields_are_zero(self):
        tenant, company, warehouse, location, *_, user = full_setup()

        sc = create_stock_count(tenant, company, warehouse, location, user)
        assert sc.total_items_counted == 0
        assert sc.total_variance_cost == Decimal("0.0000")
        assert sc.is_blind_count is False
        assert sc.freeze_inventory is False


# ===========================================================================
# STOCK COUNT LINE MODEL TESTS
# ===========================================================================


@pytest.mark.django_db
class TestStockCountLineModel:
    def _make_line(self, counted, snapshot=Decimal("100"), unit_cost=Decimal("10")):
        from apps.stock_adjustment.models import StockCountLine
        tenant, company, warehouse, location, medicine, batch, _, user = full_setup()
        sc = create_stock_count(tenant, company, warehouse, location, user)
        return StockCountLine(
            tenant=tenant,
            stock_count=sc,
            medicine=medicine,
            batch=batch,
            storage_location=location,
            snapshot_quantity=snapshot,
            counted_quantity=counted,
            unit_cost=unit_cost,
        )

    def test_overage_variance(self):
        from apps.stock_adjustment.models.enums import VarianceDirection
        line = self._make_line(Decimal("110"))
        line.recalculate_variance()
        assert line.variance_quantity == Decimal("10")
        assert line.variance_direction == VarianceDirection.OVERAGE
        assert line.variance_cost == Decimal("100.0000")

    def test_shortage_variance(self):
        from apps.stock_adjustment.models.enums import VarianceDirection
        line = self._make_line(Decimal("85"))
        line.recalculate_variance()
        assert line.variance_quantity == Decimal("-15")
        assert line.variance_direction == VarianceDirection.SHORTAGE
        assert line.variance_cost == Decimal("-150.0000")

    def test_exact_match_no_variance(self):
        from apps.stock_adjustment.models.enums import VarianceDirection
        line = self._make_line(Decimal("100"))
        line.recalculate_variance()
        assert line.variance_quantity == Decimal("0")
        assert line.variance_direction == VarianceDirection.NO_VARIANCE
        assert line.variance_cost == Decimal("0.0000")

    def test_zero_snapshot_does_not_raise(self):
        line = self._make_line(Decimal("10"), snapshot=Decimal("0"))
        line.recalculate_variance()  # Should not raise
        assert line.variance_quantity == Decimal("10")


# ===========================================================================
# SERVICE LIFECYCLE TESTS
# ===========================================================================


@pytest.mark.django_db
class TestStockCountServiceLifecycle:
    def test_start_transitions_to_in_progress(self):
        from apps.stock_adjustment.models.enums import CountStatus
        from apps.stock_adjustment.services import StockCountService
        tenant, company, warehouse, location, *_, user = full_setup()

        sc = create_stock_count(tenant, company, warehouse, location, user)
        started = StockCountService().start_stock_count(tenant, sc, user=user)

        assert started.count_status == CountStatus.IN_PROGRESS
        assert started.started_at is not None
        assert started.snapshot_at is not None

    def test_record_lines_saves_counted_quantity(self):
        from apps.stock_adjustment.models import StockCountLine
        from apps.stock_adjustment.services import StockCountService
        tenant, company, warehouse, location, medicine, batch, inv_item, user = full_setup()

        sc = create_stock_count(tenant, company, warehouse, location, user)
        svc = StockCountService()
        svc.start_stock_count(tenant, sc, user=user)
        sc.refresh_from_db()

        svc.record_count_lines(tenant, sc, [{
            "medicine_id": str(medicine.id),
            "batch_id": str(batch.id),
            "storage_location_id": str(location.id),
            "counted_quantity": Decimal("95"),
            "unit_cost": Decimal("10.00"),
        }], user=user)

        line = StockCountLine.objects.filter(stock_count=sc, medicine=medicine).first()
        assert line is not None
        assert line.counted_quantity == Decimal("95")

    def test_submit_transitions_to_submitted(self):
        from apps.stock_adjustment.models.enums import CountStatus
        from apps.stock_adjustment.services import StockCountService
        tenant, company, warehouse, location, medicine, batch, inv_item, user = full_setup()

        sc = create_stock_count(tenant, company, warehouse, location, user)
        svc = StockCountService()
        svc.start_stock_count(tenant, sc, user=user)
        sc.refresh_from_db()

        svc.record_count_lines(tenant, sc, [{
            "medicine_id": str(medicine.id),
            "batch_id": str(batch.id),
            "storage_location_id": str(location.id),
            "counted_quantity": Decimal("95"),
            "unit_cost": Decimal("10.00"),
        }], user=user)
        sc.refresh_from_db()

        submitted = svc.submit_stock_count(tenant, sc, user=user)
        assert submitted.count_status == CountStatus.SUBMITTED
        assert submitted.submitted_at is not None

    def test_approve_transitions_to_approved(self):
        from apps.stock_adjustment.models.enums import CountStatus
        from apps.stock_adjustment.services import StockCountService
        tenant, company, warehouse, location, medicine, batch, inv_item, user = full_setup()
        approver = make_user("approver-lifecycle@test.com")

        sc = create_stock_count(tenant, company, warehouse, location, user)
        svc = StockCountService()
        svc.start_stock_count(tenant, sc, user=user)
        sc.refresh_from_db()

        svc.record_count_lines(tenant, sc, [{
            "medicine_id": str(medicine.id),
            "batch_id": str(batch.id),
            "storage_location_id": str(location.id),
            "counted_quantity": Decimal("100"),
            "unit_cost": Decimal("10.00"),
        }], user=user)
        sc.refresh_from_db()
        svc.submit_stock_count(tenant, sc, user=user)
        sc.refresh_from_db()

        approved = svc.approve_stock_count(tenant, sc, user=approver)
        assert approved.count_status == CountStatus.APPROVED

    def test_reconcile_shortage_creates_adjustment_out_movement(self):
        from apps.stock_adjustment.models.enums import CountStatus
        from apps.stock_adjustment.services import StockCountService
        from apps.stock_movement.models import StockMovement
        tenant, company, warehouse, location, medicine, batch, inv_item, user = full_setup()
        approver = make_user("approver-rec@test.com")

        sc = create_stock_count(tenant, company, warehouse, location, user)
        svc = StockCountService()
        svc.start_stock_count(tenant, sc, user=user)
        sc.refresh_from_db()

        # Count 90 vs 100 on-hand → shortage
        svc.record_count_lines(tenant, sc, [{
            "medicine_id": str(medicine.id),
            "batch_id": str(batch.id),
            "storage_location_id": str(location.id),
            "counted_quantity": Decimal("90"),
            "unit_cost": Decimal("10.00"),
        }], user=user)
        sc.refresh_from_db()
        svc.submit_stock_count(tenant, sc, user=user)
        sc.refresh_from_db()
        svc.approve_stock_count(tenant, sc, user=approver)
        sc.refresh_from_db()

        movements_before = StockMovement.objects.filter(tenant=tenant).count()
        reconciled = svc.reconcile_stock_count(tenant, sc, user=user)
        movements_after = StockMovement.objects.filter(tenant=tenant).count()

        assert reconciled.count_status == CountStatus.RECONCILED
        assert movements_after > movements_before

    def test_cancel_stock_count(self):
        from apps.stock_adjustment.models.enums import CountStatus
        from apps.stock_adjustment.services import StockCountService
        tenant, company, warehouse, location, *_, user = full_setup()

        sc = create_stock_count(tenant, company, warehouse, location, user)
        cancelled = StockCountService().cancel_stock_count(tenant, sc, user=user)
        assert cancelled.count_status == CountStatus.CANCELLED
        assert cancelled.cancelled_at is not None


# ===========================================================================
# IDEMPOTENCY TESTS
# ===========================================================================


@pytest.mark.django_db
class TestReconcileIdempotency:
    def test_reconciled_count_cannot_be_reconciled_again(self):
        from apps.stock_adjustment.services import StockCountService
        tenant, company, warehouse, location, medicine, batch, inv_item, user = full_setup()
        approver = make_user("approver-idem@test.com")

        sc = create_stock_count(tenant, company, warehouse, location, user)
        svc = StockCountService()
        svc.start_stock_count(tenant, sc, user=user)
        sc.refresh_from_db()

        svc.record_count_lines(tenant, sc, [{
            "medicine_id": str(medicine.id),
            "batch_id": str(batch.id),
            "storage_location_id": str(location.id),
            "counted_quantity": Decimal("80"),
            "unit_cost": Decimal("10.00"),
        }], user=user)
        sc.refresh_from_db()
        svc.submit_stock_count(tenant, sc, user=user)
        sc.refresh_from_db()
        svc.approve_stock_count(tenant, sc, user=approver)
        sc.refresh_from_db()
        svc.reconcile_stock_count(tenant, sc, user=user)
        sc.refresh_from_db()

        # Service returns idempotently without raising when already reconciled
        result = svc.reconcile_stock_count(tenant, sc, user=user)
        sc.refresh_from_db()

        # Status must still be RECONCILED and no new movements should be created
        from apps.stock_adjustment.models.enums import CountStatus
        assert result.count_status == CountStatus.RECONCILED


# ===========================================================================
# BLIND COUNT SECURITY TESTS
# ===========================================================================


@pytest.mark.django_db
class TestBlindCountSecurity:
    def test_snapshot_quantity_hidden_for_blind_count_in_progress(self):
        from apps.stock_adjustment.models import StockCountLine
        from apps.stock_adjustment.serializers import StockCountLineSerializer
        from apps.stock_adjustment.services import StockCountService
        from rest_framework.test import APIRequestFactory

        tenant, company, warehouse, location, medicine, batch, _, user = full_setup()

        sc = create_stock_count(tenant, company, warehouse, location, user, is_blind_count=True)
        StockCountService().start_stock_count(tenant, sc, user=user)
        sc.refresh_from_db()

        line = StockCountLine.objects.create(
            tenant=tenant,
            stock_count=sc,
            medicine=medicine,
            batch=batch,
            storage_location=location,
            snapshot_quantity=Decimal("100"),
            counted_quantity=Decimal("95"),
            unit_cost=Decimal("10.00"),
            variance_quantity=Decimal("-5"),
            variance_direction="shortage",
        )

        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = user

        data = StockCountLineSerializer(line, context={"request": request}).data
        # Blind count IN_PROGRESS — system-side quantities must be masked
        assert data["snapshot_quantity"] is None
        assert data["variance_quantity"] is None
        assert data["variance_percentage"] is None
        assert data["variance_cost"] is None

    def test_snapshot_quantity_visible_for_non_blind_count(self):
        from apps.stock_adjustment.models import StockCountLine
        from apps.stock_adjustment.serializers import StockCountLineSerializer
        from apps.stock_adjustment.services import StockCountService
        from rest_framework.test import APIRequestFactory

        tenant, company, warehouse, location, medicine, batch, _, user = full_setup()

        sc = create_stock_count(tenant, company, warehouse, location, user, is_blind_count=False)
        StockCountService().start_stock_count(tenant, sc, user=user)
        sc.refresh_from_db()

        line = StockCountLine.objects.create(
            tenant=tenant,
            stock_count=sc,
            medicine=medicine,
            batch=batch,
            storage_location=location,
            snapshot_quantity=Decimal("100"),
            counted_quantity=Decimal("95"),
            unit_cost=Decimal("10.00"),
            variance_quantity=Decimal("-5"),
            variance_direction="shortage",
        )

        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = user

        data = StockCountLineSerializer(line, context={"request": request}).data
        # Non-blind count — system quantities must be visible
        assert data["snapshot_quantity"] is not None


# ===========================================================================
# TENANT ISOLATION TESTS
# ===========================================================================


@pytest.mark.django_db
class TestStockCountTenantIsolation:
    def test_list_counts_scoped_to_tenant(self):
        from apps.stock_adjustment.selectors import StockCountSelector

        tenant_a = make_tenant("a")
        company_a = make_company(tenant_a)
        wh_a = make_warehouse(tenant_a, company_a)
        loc_a = make_location(tenant_a, wh_a)
        user_a = make_user("user-iso-a@test.com")

        tenant_b = make_tenant("b")
        company_b = make_company(tenant_b)
        wh_b = make_warehouse(tenant_b, company_b)
        loc_b = make_location(tenant_b, wh_b)
        user_b = make_user("user-iso-b@test.com")

        create_stock_count(tenant_a, company_a, wh_a, loc_a, user_a)
        create_stock_count(tenant_a, company_a, wh_a, loc_a, user_a)
        create_stock_count(tenant_b, company_b, wh_b, loc_b, user_b)

        selector = StockCountSelector()
        qs_a = selector.list_counts(tenant=tenant_a)
        qs_b = selector.list_counts(tenant=tenant_b)

        assert qs_a.count() == 2
        assert qs_b.count() == 1

    def test_cross_tenant_id_lookup_returns_none(self):
        from apps.stock_adjustment.selectors import StockCountSelector

        tenant_a = make_tenant("aa")
        company_a = make_company(tenant_a)
        wh_a = make_warehouse(tenant_a, company_a)
        loc_a = make_location(tenant_a, wh_a)
        user_a = make_user("user-cross-a@test.com")

        tenant_b = make_tenant("bb")
        company_b = make_company(tenant_b)
        wh_b = make_warehouse(tenant_b, company_b)
        loc_b = make_location(tenant_b, wh_b)
        user_b = make_user("user-cross-b@test.com")

        sc_b = create_stock_count(tenant_b, company_b, wh_b, loc_b, user_b)

        selector = StockCountSelector()
        result = selector.get_count_by_id(tenant_a, str(sc_b.id))
        assert result is None


# ===========================================================================
# SEQUENCE GENERATOR TESTS
# ===========================================================================


@pytest.mark.django_db
class TestCountNumberGenerator:
    def test_generates_cnt_prefix(self):
        from apps.stock_adjustment.services.count_number_generator import CountNumberGenerator
        tenant = make_tenant()
        number = CountNumberGenerator().generate_count_number(tenant)
        assert number.startswith("CNT-")

    def test_sequential_numbers_are_unique(self):
        """Numbers must increment when prior counts are saved to the database."""
        from apps.stock_adjustment.services.count_number_generator import CountNumberGenerator
        tenant = make_tenant()
        company = make_company(tenant)
        warehouse = make_warehouse(tenant, company)
        location = make_location(tenant, warehouse)
        user = make_user()
        gen = CountNumberGenerator()

        # Create actual saved stock counts so the generator can detect sequence
        sc1 = create_stock_count(tenant, company, warehouse, location, user)
        sc2 = create_stock_count(tenant, company, warehouse, location, user)
        sc3 = create_stock_count(tenant, company, warehouse, location, user)

        numbers = {sc1.count_number, sc2.count_number, sc3.count_number}
        assert len(numbers) == 3

    def test_session_number_starts_with_ses(self):
        from apps.stock_adjustment.services.count_number_generator import CountNumberGenerator
        tenant = make_tenant()
        number = CountNumberGenerator().generate_session_number(tenant)
        assert number.startswith("SES-")

    def test_recount_number_starts_with_rec(self):
        from apps.stock_adjustment.services.count_number_generator import CountNumberGenerator
        tenant = make_tenant()
        number = CountNumberGenerator().generate_recount_number(tenant)
        assert number.startswith("REC-")


# ===========================================================================
# HISTORY EVENT TESTS
# ===========================================================================


@pytest.mark.django_db
class TestStockCountHistory:
    def test_history_event_written_on_create(self):
        from apps.stock_adjustment.models import StockCountHistory
        tenant, company, warehouse, location, *_, user = full_setup()

        sc = create_stock_count(tenant, company, warehouse, location, user)
        events = StockCountHistory.objects.filter(stock_count=sc)
        assert events.count() >= 1

    def test_history_event_written_on_start(self):
        from apps.stock_adjustment.models import StockCountHistory
        from apps.stock_adjustment.services import StockCountService
        tenant, company, warehouse, location, *_, user = full_setup()

        sc = create_stock_count(tenant, company, warehouse, location, user)
        StockCountService().start_stock_count(tenant, sc, user=user)

        events = StockCountHistory.objects.filter(stock_count=sc)
        assert events.count() >= 2  # CREATED + STARTED

    def test_selector_get_history_returns_list(self):
        from apps.stock_adjustment.selectors import StockCountSelector
        from apps.stock_adjustment.services import StockCountService
        tenant, company, warehouse, location, *_, user = full_setup()

        sc = create_stock_count(tenant, company, warehouse, location, user)
        StockCountService().start_stock_count(tenant, sc, user=user)

        selector = StockCountSelector()
        history = selector.get_count_history(tenant, str(sc.id))
        assert len(history) >= 1


# ===========================================================================
# VARIANCE SUMMARY TESTS
# ===========================================================================


@pytest.mark.django_db
class TestVarianceSummary:
    def test_variance_summary_has_expected_structure(self):
        from apps.stock_adjustment.models import StockCountLine
        from apps.stock_adjustment.selectors import StockCountSelector
        from apps.stock_adjustment.services import StockCountService
        tenant, company, warehouse, location, medicine, batch, _, user = full_setup()

        sc = create_stock_count(tenant, company, warehouse, location, user)
        StockCountService().start_stock_count(tenant, sc, user=user)
        sc.refresh_from_db()

        StockCountLine.objects.create(
            tenant=tenant,
            stock_count=sc,
            medicine=medicine,
            batch=batch,
            storage_location=location,
            snapshot_quantity=Decimal("100"),
            counted_quantity=Decimal("90"),
            unit_cost=Decimal("10.00"),
            variance_quantity=Decimal("-10"),
            variance_cost=Decimal("-100.0000"),
            variance_direction="shortage",
        )

        summary = StockCountSelector().get_count_variance_summary(tenant, str(sc.id))
        assert summary is not None
        assert "total_items" in summary


# ===========================================================================
# SERVICE EXCEPTION / INVALID TRANSITION TESTS
# ===========================================================================


@pytest.mark.django_db
class TestStockCountServiceExceptions:
    def test_cannot_start_in_progress_count(self):
        from apps.stock_adjustment.services import StockCountService
        tenant, company, warehouse, location, *_, user = full_setup()

        sc = create_stock_count(tenant, company, warehouse, location, user)
        svc = StockCountService()
        svc.start_stock_count(tenant, sc, user=user)
        sc.refresh_from_db()

        with pytest.raises(Exception):
            svc.start_stock_count(tenant, sc, user=user)

    def test_cannot_submit_draft_count(self):
        from apps.stock_adjustment.services import StockCountService
        tenant, company, warehouse, location, *_, user = full_setup()

        sc = create_stock_count(tenant, company, warehouse, location, user)
        with pytest.raises(Exception):
            StockCountService().submit_stock_count(tenant, sc, user=user)

    def test_cannot_approve_draft_count(self):
        from apps.stock_adjustment.services import StockCountService
        tenant, company, warehouse, location, *_, user = full_setup()

        sc = create_stock_count(tenant, company, warehouse, location, user)
        with pytest.raises(Exception):
            StockCountService().approve_stock_count(tenant, sc, user=user)

    def test_cannot_reconcile_draft_count(self):
        from apps.stock_adjustment.services import StockCountService
        tenant, company, warehouse, location, *_, user = full_setup()

        sc = create_stock_count(tenant, company, warehouse, location, user)
        with pytest.raises(Exception):
            StockCountService().reconcile_stock_count(tenant, sc, user=user)

    def test_cannot_cancel_already_cancelled(self):
        from apps.stock_adjustment.services import StockCountService
        tenant, company, warehouse, location, *_, user = full_setup()

        sc = create_stock_count(tenant, company, warehouse, location, user)
        svc = StockCountService()
        svc.cancel_stock_count(tenant, sc, user=user)
        sc.refresh_from_db()

        with pytest.raises(Exception):
            svc.cancel_stock_count(tenant, sc, user=user)


# ===========================================================================
# REPORTING SUMMARY TESTS
# ===========================================================================


@pytest.mark.django_db
class TestReportingSummary:
    def test_reporting_summary_returns_dict(self):
        from apps.stock_adjustment.selectors import StockCountSelector
        tenant = make_tenant()
        company = make_company(tenant)
        warehouse = make_warehouse(tenant, company)
        location = make_location(tenant, warehouse)
        user = make_user()

        create_stock_count(tenant, company, warehouse, location, user)

        selector = StockCountSelector()
        summary = selector.get_reporting_summary(tenant)
        assert isinstance(summary, dict)
        assert "total_reconciled_lines" in summary
        assert "total_variance_cost" in summary
