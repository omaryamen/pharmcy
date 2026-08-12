"""ChartOfAccountsService seeding default system Chart of Accounts and managing integration account mappings."""

from __future__ import annotations

import logging
from typing import Any

from django.db import transaction

from apps.companies.models import Company
from apps.general_ledger.models import (
    AccountMapping,
    AccountSubtype,
    AccountType,
    ChartOfAccount,
    MappingPurpose,
)

logger = logging.getLogger(__name__)


class ChartOfAccountsService:
    """Service layer seeding standard ERP Chart of Accounts (1000 Assets, 2000 Liabilities, 3000 Equity, 4000 Revenue, 5000 COGS, 6000 Expenses)."""

    @transaction.atomic
    def seed_default_chart_of_accounts(self, tenant: Any, company: Company) -> dict[str, ChartOfAccount]:
        """Seed default system accounts for a company."""
        default_accounts = [
            # 1000 ASSETS
            {"code": "1000", "name": "Assets", "type": AccountType.ASSET, "subtype": AccountSubtype.CASH, "is_control": True},
            {"code": "1100", "name": "Cash on Hand", "type": AccountType.ASSET, "subtype": AccountSubtype.CASH, "is_control": False},
            {"code": "1200", "name": "Bank Account", "type": AccountType.ASSET, "subtype": AccountSubtype.BANK, "is_control": False},
            {"code": "1300", "name": "Accounts Receivable", "type": AccountType.ASSET, "subtype": AccountSubtype.ACCOUNTS_RECEIVABLE, "is_control": False},
            {"code": "1400", "name": "Merchandise Inventory", "type": AccountType.ASSET, "subtype": AccountSubtype.INVENTORY, "is_control": False},
            # 2000 LIABILITIES
            {"code": "2000", "name": "Liabilities", "type": AccountType.LIABILITY, "subtype": AccountSubtype.ACCOUNTS_PAYABLE, "is_control": True},
            {"code": "2100", "name": "Accounts Payable", "type": AccountType.LIABILITY, "subtype": AccountSubtype.ACCOUNTS_PAYABLE, "is_control": False},
            {"code": "2200", "name": "Tax / VAT Payable", "type": AccountType.LIABILITY, "subtype": AccountSubtype.TAX_PAYABLE, "is_control": False},
            {"code": "2300", "name": "Customer Credit Liability", "type": AccountType.LIABILITY, "subtype": AccountSubtype.CUSTOMER_CREDIT, "is_control": False},
            # 3000 EQUITY
            {"code": "3000", "name": "Equity", "type": AccountType.EQUITY, "subtype": AccountSubtype.CAPITAL, "is_control": True},
            {"code": "3100", "name": "Owner Capital", "type": AccountType.EQUITY, "subtype": AccountSubtype.CAPITAL, "is_control": False},
            {"code": "3200", "name": "Retained Earnings", "type": AccountType.EQUITY, "subtype": AccountSubtype.RETAINED_EARNINGS, "is_control": False},
            # 4000 REVENUE
            {"code": "4000", "name": "Revenue", "type": AccountType.REVENUE, "subtype": AccountSubtype.SALES_REVENUE, "is_control": True},
            {"code": "4100", "name": "Sales Revenue", "type": AccountType.REVENUE, "subtype": AccountSubtype.SALES_REVENUE, "is_control": False},
            {"code": "4200", "name": "Sales Returns & Allowances", "type": AccountType.REVENUE, "subtype": AccountSubtype.SALES_RETURNS, "is_control": False},
            # 5000 COGS
            {"code": "5000", "name": "Cost of Goods Sold", "type": AccountType.COST_OF_GOODS_SOLD, "subtype": AccountSubtype.COGS, "is_control": False},
            # 6000 EXPENSES
            {"code": "6000", "name": "Operating Expenses", "type": AccountType.EXPENSE, "subtype": AccountSubtype.OPERATING_EXPENSE, "is_control": False},
        ]

        created_map = {}
        for item in default_accounts:
            acc, _ = ChartOfAccount.objects.get_or_create(
                tenant=tenant,
                company=company,
                account_code=item["code"],
                defaults={
                    "account_name": item["name"],
                    "english_name": item["name"],
                    "account_type": item["type"],
                    "account_subtype": item["subtype"],
                    "is_control_account": item["is_control"],
                    "is_system_account": True,
                    "status": "active",
                },
            )
            created_map[item["code"]] = acc

        # Seed default account mappings
        mappings = [
            (MappingPurpose.DEFAULT_CASH, created_map["1100"]),
            (MappingPurpose.DEFAULT_BANK, created_map["1200"]),
            (MappingPurpose.DEFAULT_AR, created_map["1300"]),
            (MappingPurpose.DEFAULT_INVENTORY, created_map["1400"]),
            (MappingPurpose.DEFAULT_AP, created_map["2100"]),
            (MappingPurpose.DEFAULT_OUTPUT_TAX, created_map["2200"]),
            (MappingPurpose.DEFAULT_CUSTOMER_CREDIT, created_map["2300"]),
            (MappingPurpose.DEFAULT_SALES_REVENUE, created_map["4100"]),
            (MappingPurpose.DEFAULT_SALES_RETURN, created_map["4200"]),
            (MappingPurpose.DEFAULT_COGS, created_map["5000"]),
        ]

        for purpose, acc_obj in mappings:
            AccountMapping.objects.update_or_create(
                tenant=tenant,
                company=company,
                purpose=purpose,
                defaults={"account": acc_obj},
            )

        logger.info(f"Seeded default Chart of Accounts and Mappings for company {company.legal_name}")
        return created_map
