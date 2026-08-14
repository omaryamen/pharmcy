"""Comprehensive Test Suite for Enterprise Advanced Reporting & Business Intelligence (IMP-032 / apps.reports)."""

import uuid
from decimal import Decimal
from datetime import date, time, timedelta
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.core.models import Tenant
from apps.companies.models import Company
from apps.branches.models import Branch
from apps.warehouses.models import Warehouse
from apps.customers.models import Customer
from apps.sales.models import SalesInvoice, SalesStatus
from apps.reports.models import ReportDefinition, ReportExportLog, ExportFormat, ReportCategory
from apps.reports.selectors import (
    ReportFilterDTO,
    SalesReportSelector,
    InventoryReportSelector,
    PurchasingReportSelector,
    FinancialReportSelector,
    ExecutiveDashboardSelector,
)
from apps.reports.services import (
    KpiEngineService,
    ReportExportService,
    ReportReconciliationService,
)

User = get_user_model()


def rpt_setup():
    """Helper setup creating tenant, company, branch, warehouse, cashier user, and customer."""
    uid = uuid.uuid4().hex[:6]
    tenant = Tenant.objects.create(name=f"RPT Tenant {uid}", code=f"TNT-{uid}", slug=f"rpt-slug-{uid}")
    company = Company.objects.create(tenant=tenant, legal_name="Pharma Cloud Corp", commercial_name="Pharma Cloud Corp", code=f"COMP-{uid[:4]}", slug=f"comp-{uid[:4]}")
    branch = Branch.objects.create(tenant=tenant, company=company, name="Main Pharmacy Branch", code=f"BR-{uid[:4]}")
    warehouse = Warehouse.objects.create(tenant=tenant, company=company, branch=branch, name="Main Warehouse", code=f"WH-{uid[:4]}")
    cashier = User.objects.create_user(email=f"cashier_{uid}@test.com", first_name="John", last_name="Doe", password="pass")
    customer = Customer.objects.create(tenant=tenant, company=company, code=f"CUS-{uid[:4]}", customer_number=f"CN-{uid[:4]}", first_name="Valued", last_name="Customer")
    return tenant, company, branch, warehouse, cashier, customer


@pytest.mark.django_db
class TestSalesReportSelector:
    """Test suite for SalesReportSelector sales analytics."""

    def test_sales_summary_aggregation(self):
        tenant, company, branch, warehouse, cashier_user, customer = rpt_setup()
        today = timezone.now().date()
        now_time = time(10, 30)
        SalesInvoice.objects.create(
            tenant=tenant,
            company=company,
            branch=branch,
            warehouse=warehouse,
            cashier=cashier_user,
            customer=customer,
            invoice_number=f"INV-RPT-{uuid.uuid4().hex[:4]}",
            invoice_date=today,
            invoice_time=now_time,
            status=SalesStatus.COMPLETED,
            subtotal=Decimal("100.0000"),
            discount=Decimal("10.0000"),
            tax=Decimal("5.0000"),
            grand_total=Decimal("95.0000"),
            paid_amount=Decimal("95.0000"),
        )
        SalesInvoice.objects.create(
            tenant=tenant,
            company=company,
            branch=branch,
            warehouse=warehouse,
            cashier=cashier_user,
            customer=customer,
            invoice_number=f"INV-RPT-{uuid.uuid4().hex[:4]}",
            invoice_date=today,
            invoice_time=now_time,
            status=SalesStatus.COMPLETED,
            subtotal=Decimal("200.0000"),
            discount=Decimal("0.0000"),
            tax=Decimal("10.0000"),
            grand_total=Decimal("210.0000"),
            paid_amount=Decimal("210.0000"),
        )

        selector = SalesReportSelector()
        filters = ReportFilterDTO(tenant=tenant, company_id=str(company.pk), period_type="today")
        summary = selector.get_sales_summary(filters)

        assert summary["invoice_count"] == 2
        assert summary["gross_sales"] == Decimal("300.0000")
        assert summary["total_discounts"] == Decimal("10.0000")
        assert summary["net_sales"] == Decimal("305.0000")
        assert summary["average_transaction_value"] == Decimal("152.5000")

    def test_sales_by_branch_and_cashier(self):
        tenant, company, branch, warehouse, cashier_user, customer = rpt_setup()
        today = timezone.now().date()
        SalesInvoice.objects.create(
            tenant=tenant,
            company=company,
            branch=branch,
            warehouse=warehouse,
            cashier=cashier_user,
            customer=customer,
            invoice_number=f"INV-RPT-{uuid.uuid4().hex[:4]}",
            invoice_date=today,
            invoice_time=time(12, 0),
            status=SalesStatus.COMPLETED,
            subtotal=Decimal("500.0000"),
            grand_total=Decimal("500.0000"),
            paid_amount=Decimal("500.0000"),
        )

        selector = SalesReportSelector()
        filters = ReportFilterDTO(tenant=tenant, period_type="today")

        by_branch = selector.get_sales_by_branch(filters)
        assert len(by_branch) >= 1
        assert by_branch[0]["branch_id"] == str(branch.pk)
        assert by_branch[0]["net_sales"] == Decimal("500.0000")

        by_cashier = selector.get_sales_by_cashier(filters)
        assert len(by_cashier) >= 1
        assert by_cashier[0]["cashier_id"] == str(cashier_user.pk)
        assert by_cashier[0]["net_sales"] == Decimal("500.0000")


@pytest.mark.django_db
class TestKpiEngineService:
    """Test suite for KpiEngineService metric calculations."""

    def test_kpi_growth_and_variance(self):
        kpi_service = KpiEngineService()
        res = kpi_service.calculate_kpi_metric("Revenue", current_value=1200, previous_value=1000)

        assert res["kpi_name"] == "Revenue"
        assert res["difference"] == Decimal("200")
        assert res["percentage_change"] == Decimal("20.00")
        assert res["trend"] == "up"

    def test_kpi_zero_previous_value_handling(self):
        kpi_service = KpiEngineService()
        res = kpi_service.calculate_kpi_metric("New Sales", current_value=500, previous_value=0)

        assert res["difference"] == Decimal("500")
        assert res["percentage_change"] == Decimal("100.00")
        assert res["trend"] == "up"


@pytest.mark.django_db
class TestReportExportService:
    """Test suite for ReportExportService."""

    def test_export_report_to_csv(self):
        tenant, company, branch, warehouse, cashier_user, customer = rpt_setup()
        export_service = ReportExportService()
        data = [
            {"date": "2026-08-14", "net_sales": Decimal("100.0000"), "invoice_count": 1},
            {"date": "2026-08-15", "net_sales": Decimal("250.0000"), "invoice_count": 2},
        ]

        csv_str, filename = export_service.export_report_to_csv(
            tenant=tenant,
            company=company,
            report_code="RPT-SAL-TEST",
            category="sales",
            data_rows=data,
            user=cashier_user,
        )

        assert "date,net_sales,invoice_count" in csv_str
        assert "2026-08-14" in csv_str
        assert filename.startswith("RPT-SAL-TEST_")

        # Verify audit log
        log = ReportExportLog.objects.filter(tenant=tenant, report_code="RPT-SAL-TEST").first()
        assert log is not None
        assert log.record_count == 2
        assert log.export_format == ExportFormat.CSV


@pytest.mark.django_db
class TestTenantIsolationInReporting:
    """Test suite ensuring strict tenant isolation across reporting selectors."""

    def test_reporting_tenant_isolation(self):
        tenant, company, branch, warehouse, cashier_user, customer = rpt_setup()
        uid2 = uuid.uuid4().hex[:6]
        another_tenant = Tenant.objects.create(name=f"RPT Tenant 2 {uid2}", code=f"TNT-{uid2}", slug=f"rpt-slug-2-{uid2}")
        today = timezone.now().date()

        # Tenant 1 sale
        SalesInvoice.objects.create(
            tenant=tenant,
            company=company,
            branch=branch,
            warehouse=warehouse,
            cashier=cashier_user,
            customer=customer,
            invoice_number=f"INV-TEN-1-{uuid.uuid4().hex[:4]}",
            invoice_date=today,
            invoice_time=time(14, 0),
            status=SalesStatus.COMPLETED,
            subtotal=Decimal("1000.0000"),
            grand_total=Decimal("1000.0000"),
            paid_amount=Decimal("1000.0000"),
        )

        selector = SalesReportSelector()
        t1_summary = selector.get_sales_summary(ReportFilterDTO(tenant=tenant, period_type="today"))
        t2_summary = selector.get_sales_summary(ReportFilterDTO(tenant=another_tenant, period_type="today"))

        assert t1_summary["net_sales"] == Decimal("1000.0000")
        assert t2_summary["net_sales"] == Decimal("0.0000")
        assert t2_summary["invoice_count"] == 0
