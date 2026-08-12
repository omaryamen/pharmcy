"""Domain choices & enums for Enterprise General Ledger & Double-Entry Accounting."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class AccountType(models.TextChoices):
    ASSET = "asset", _("Asset")
    LIABILITY = "liability", _("Liability")
    EQUITY = "equity", _("Equity")
    REVENUE = "revenue", _("Revenue / Income")
    EXPENSE = "expense", _("Expense")
    COST_OF_GOODS_SOLD = "cost_of_goods_sold", _("Cost of Goods Sold (COGS)")
    OTHER_INCOME = "other_income", _("Other Income")
    OTHER_EXPENSE = "other_expense", _("Other Expense")


class AccountSubtype(models.TextChoices):
    CASH = "cash", _("Cash & Cash Equivalents")
    BANK = "bank", _("Bank Account")
    ACCOUNTS_RECEIVABLE = "accounts_receivable", _("Accounts Receivable (AR)")
    INVENTORY = "inventory", _("Merchandise Inventory")
    FIXED_ASSET = "fixed_asset", _("Fixed Asset / Equipment")
    ACCOUNTS_PAYABLE = "accounts_payable", _("Accounts Payable (AP)")
    TAX_PAYABLE = "tax_payable", _("Tax / VAT Payable")
    CUSTOMER_CREDIT = "customer_credit", _("Customer Credit Liability")
    SUPPLIER_CREDIT = "supplier_credit", _("Supplier Credit Asset")
    SALES_REVENUE = "sales_revenue", _("Sales Revenue")
    SALES_RETURNS = "sales_returns", _("Sales Returns & Allowances")
    PURCHASE = "purchase", _("Purchases")
    COGS = "cogs", _("Cost of Goods Sold")
    OPERATING_EXPENSE = "operating_expense", _("Operating Expense")
    OTHER_INCOME = "other_income", _("Other Income")
    OTHER_EXPENSE = "other_expense", _("Other Expense")
    CAPITAL = "capital", _("Owner Capital")
    RETAINED_EARNINGS = "retained_earnings", _("Retained Earnings")


class PeriodStatus(models.TextChoices):
    OPEN = "open", _("Open Accounting Period")
    CLOSED = "closed", _("Closed Period")
    LOCKED = "locked", _("Locked Period (Audited)")


class JournalStatus(models.TextChoices):
    DRAFT = "draft", _("Draft Journal")
    PENDING_APPROVAL = "pending_approval", _("Pending Manager Approval")
    POSTED = "posted", _("Posted Journal (Immutable)")
    REVERSED = "reversed", _("Reversed Journal")
    VOIDED = "voided", _("Voided")


class MappingPurpose(models.TextChoices):
    DEFAULT_CASH = "default_cash", _("Default Cash Account")
    DEFAULT_BANK = "default_bank", _("Default Bank Account")
    DEFAULT_AR = "default_ar", _("Default Accounts Receivable Account")
    DEFAULT_AP = "default_ap", _("Default Accounts Payable Account")
    DEFAULT_SALES_REVENUE = "default_sales_revenue", _("Default Sales Revenue Account")
    DEFAULT_SALES_RETURN = "default_sales_return", _("Default Sales Returns Account")
    DEFAULT_INVENTORY = "default_inventory", _("Default Inventory Account")
    DEFAULT_COGS = "default_cogs", _("Default COGS Account")
    DEFAULT_OUTPUT_TAX = "default_output_tax", _("Default Output Tax Account")
    DEFAULT_INPUT_TAX = "default_input_tax", _("Default Input Tax Account")
    DEFAULT_CUSTOMER_CREDIT = "default_customer_credit", _("Default Customer Credit Account")
    DEFAULT_SUPPLIER_CREDIT = "default_supplier_credit", _("Default Supplier Credit Account")
