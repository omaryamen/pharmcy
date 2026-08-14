"""ExecutiveDashboardSelector aggregating high-level C-Suite management KPIs and chart data payloads."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from apps.reports.selectors.dto import ReportFilterDTO
from apps.reports.selectors.financial_reports import FinancialReportSelector
from apps.reports.selectors.inventory_reports import InventoryReportSelector
from apps.reports.selectors.sales_reports import SalesReportSelector


class ExecutiveDashboardSelector:
    """Master C-Suite Executive Management Dashboard Selector combining Sales, Financials, Treasury, and Inventory KPIs."""

    def __init__(
        self,
        sales_selector: SalesReportSelector | None = None,
        financial_selector: FinancialReportSelector | None = None,
        inventory_selector: InventoryReportSelector | None = None,
    ) -> None:
        self.sales_selector = sales_selector or SalesReportSelector()
        self.financial_selector = financial_selector or FinancialReportSelector()
        self.inventory_selector = inventory_selector or InventoryReportSelector()

    def get_executive_summary(self, filters: ReportFilterDTO) -> dict[str, Any]:
        """Compile comprehensive executive dashboard KPI metrics."""
        sales_summary = self.sales_selector.get_sales_summary(filters)
        p_and_l = self.financial_selector.get_profit_and_loss(filters)
        treasury = self.financial_selector.get_cash_treasury_summary(filters)
        inventory = self.inventory_selector.get_stock_valuation_summary(filters)
        expiry = self.inventory_selector.get_expiry_risk_summary(filters)
        ar_aging = self.financial_selector.get_ar_aging(filters)
        expenses = self.financial_selector.get_expense_summary(filters)

        return {
            "sales_performance": sales_summary,
            "financial_profitability": {
                "total_revenue": p_and_l["total_revenue"],
                "total_cogs": p_and_l["total_cogs"],
                "gross_profit": p_and_l["gross_profit"],
                "total_expenses": p_and_l["total_expenses"],
                "net_profit": p_and_l["net_profit"],
            },
            "treasury_liquidity": treasury,
            "inventory_health": {
                "total_valuation": inventory["total_inventory_valuation"],
                "total_quantity": inventory["total_quantity_on_hand"],
                "expired_batches_count": expiry["expired_batches_count"],
                "expired_stock_value": expiry["expired_stock_value"],
            },
            "receivables": {
                "total_ar_outstanding": ar_aging["total_ar_outstanding"],
            },
            "operating_costs": {
                "total_posted_expenses": expenses["total_posted_expenses"],
            },
        }

    def get_chart_analytics(self, filters: ReportFilterDTO) -> dict[str, Any]:
        """Compile structured JSON chart payloads for frontend rendering (Line trend, Bar by Branch, Cashier breakdown)."""
        sales_trend = self.sales_selector.get_sales_trend(filters)
        branch_sales = self.sales_selector.get_sales_by_branch(filters)
        cashier_sales = self.sales_selector.get_sales_by_cashier(filters)

        return {
            "sales_trend_chart": {
                "type": "line",
                "labels": [t["date"] for t in sales_trend],
                "datasets": [
                    {"name": "Net Sales", "data": [t["net_sales"] for t in sales_trend]},
                ],
            },
            "branch_performance_chart": {
                "type": "bar",
                "labels": [b["branch_name"] for b in branch_sales],
                "datasets": [
                    {"name": "Net Sales", "data": [b["net_sales"] for b in branch_sales]},
                ],
            },
            "cashier_performance_chart": {
                "type": "bar",
                "labels": [c["cashier_name"] for c in cashier_sales[:10]],
                "datasets": [
                    {"name": "Net Sales", "data": [c["net_sales"] for c in cashier_sales[:10]]},
                ],
            },
        }
