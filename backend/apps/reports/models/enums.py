"""Domain choices & enums for Enterprise Reporting & Business Intelligence."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ReportCategory(models.TextChoices):
    SALES = "sales", _("Sales & POS Analytics")
    INVENTORY = "inventory", _("Inventory & Valuation")
    PURCHASING = "purchasing", _("Purchasing & Procurement")
    SUPPLIER = "supplier", _("Supplier & Accounts Payable")
    CUSTOMER = "customer", _("Customer & Accounts Receivable")
    FINANCIAL = "financial", _("General Ledger & Financial Statements")
    CASH_BANK = "cash_bank", _("Cash, Treasury & Bank Reconciliation")
    EXPENSE = "expense", _("Expenses & Operating Costs")
    PRESCRIPTION = "prescription", _("Prescription & Clinical Dispensing")
    BRANCH = "branch", _("Branch Performance")
    EMPLOYEE = "employee", _("Employee & Cashier Productivity")
    EXECUTIVE = "executive", _("Executive Management Dashboard")
    RECONCILIATION = "reconciliation", _("Cross-Subledger Reconciliation Audit")


class ExportFormat(models.TextChoices):
    JSON = "json", _("JSON Data Payload")
    CSV = "csv", _("Comma-Separated Values (CSV)")
    EXCEL = "excel", _("Microsoft Excel Spreadsheet (.xlsx)")
    PDF = "pdf", _("Portable Document Format (PDF)")


class PeriodType(models.TextChoices):
    TODAY = "today", _("Today")
    YESTERDAY = "yesterday", _("Yesterday")
    THIS_WEEK = "this_week", _("This Week")
    LAST_WEEK = "last_week", _("Last Week")
    THIS_MONTH = "this_month", _("This Month")
    LAST_MONTH = "last_month", _("Last Month")
    THIS_QUARTER = "this_quarter", _("This Quarter")
    LAST_QUARTER = "last_quarter", _("Last Quarter")
    THIS_YEAR = "this_year", _("This Year")
    LAST_YEAR = "last_year", _("Last Year")
    CUSTOM = "custom", _("Custom Date Range")
