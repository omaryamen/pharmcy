# Changelog — PharmaCloud ERP Backend

All notable changes to the PharmaCloud ERP Backend project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.34.0] - 2026-08-15

### Added - Enterprise Security, Compliance & Production Hardening (`IMP-039`)
- **HTTP Security Headers**: Implemented `SecurityHeadersMiddleware` setting strict CSP, Permissions-Policy, X-Content-Type-Options: nosniff, Referrer-Policy, and COOP.
- **Multi-Tenant Boundary Defense**: Automated test validation proving complete database isolation across all 39 business domains, zero tenant leakage, and strict IDOR prevention for customer orders, medical prescriptions, and invoices.
- **Financial & Inventory Authoritative Logic**: Protection against client-side tampering; all prices, stock balances, FEFO batches, and general ledger journal postings remain 100% server-authoritative with row-level locking (`select_for_update`) and idempotency keys.
- **Documentation**: Added `SECURITY.md` and `PRODUCTION_READINESS.md`.
- **Test Suite**: Created `tests/test_security_hardening.py` (576 platform tests passing, 100% pass rate).

---

## [1.33.0] - 2026-08-15

### Added - Enterprise Frontend & Unified Pharmacy ERP Web Application (`pharmcy/frontend` / `IMP-038`)
- **Next.js 15 & React 19 Enterprise Architecture**: Commercial-grade enterprise web application built with TypeScript, Tailwind CSS, and clinical design system tokens.
- **Unified Application Shell**: Collapsible sidebar navigation, tenant/company/branch switcher, global search command palette, real-time notification alerts, light/dark theme persistence, and bidirectional Arabic RTL / English LTR support.
- **Workspaces & Portals**:
  - `Executive & Pharmacy Dashboard` (`/dashboard`): Real-time sales telemetry, clinical alerts, and live POS operations.
  - `High-Speed POS Terminal` (`/pos`): Barcode scanner integration, fast catalog search, FEFO batch selection, split payments (Cash, Card), and instant invoice receipts.
  - `Clinical Prescriptions & Dispensing` (`/prescriptions`): Verification queue, narcotics/controlled drug warnings, and pharmacist approval sign-off.
  - `Inventory & Stock Ledger` (`/inventory`): Double-entry stock lookup, FEFO batch positions, stock counting sessions, and goods receipts (GRN).
  - `Sales, Purchasing & Invoices` (`/sales`, `/purchasing`): Customer credit invoices, supplier purchase orders, and 3-way matching.
  - `General Ledger & Financial Accounting` (`/accounting`): Automated double-entry journal logs, trial balances, and balance sheets.
  - `E-Commerce Management` (`/ecommerce`): Published digital catalog, online orders, and delivery courier tracking.
  - `Reporting & BI` (`/reports`): Interactive category breakdowns, revenue trends, and audit exports.
  - `Super Admin, SaaS Billing & Settings` (`/admin`, `/billing`, `/settings`): Platform operations, plan entitlements, tenant configuration, and RBAC policies.
- **Verification**: Next.js production build (`npm run build`) passing across all 17 static & dynamic routes; 572 backend platform tests passing (100% pass rate).

---

## [1.32.0] - 2026-08-15

### Added - Enterprise Customer & Pharmacy Mobile Application API Platform (`apps.mobile_api` / `IMP-037`)
- **Device Management & Push Tokens**: `Device` entity supporting Android, iOS, PWA, and desktop clients with hardware UUIDs, app version, OS version, push tokens, and revocation upon logout (`DeviceRegistrationService`).
- **Mobile Version Enforcement & Remote Config**: `MobileAppVersion` managing minimum supported versions, recommended versions, force upgrade prompts, maintenance mode messages, and integrating with `FeatureFlagSelector` (`MobileAppConfigService`).
- **Offline-First Synchronization Engine**: `MobileSyncQueue` capturing offline mutation queues, idempotent duplicate handling, and version conflict detection (`SyncConflictError`) preventing silent overwrites of stale records (`MobileSyncService`).
- **Role-Specific Mobile Dashboards & Queues**:
  - `CustomerDashboardSelector`: Active order counters, recent order timeline, pending prescription status, unread notifications, and featured storefront products.
  - `PharmacyOwnerMobileSelector`: Live POS/online sales aggregates, total inventory balances, active low-stock alerts, and near-expiry alerts.
  - `PharmacistMobileSelector`: Uploaded e-commerce prescription queue and in-store clinical verification queue.
- **REST APIs**: Endpoints under `/api/v1/mobile/devices/register/`, `/api/v1/mobile/devices/revoke/`, `/api/v1/mobile/config/`, `/api/v1/mobile/customer/dashboard/`, `/api/v1/mobile/owner/dashboard/`, `/api/v1/mobile/pharmacist/queue/`, `/api/v1/mobile/sync/push/`.
- **Test Suite**: Created `tests/test_mobile_api.py` (572 total platform tests passing, 100% pass rate).

---

## [1.31.0] - 2026-08-15

### Added - Enterprise Pharma E-Commerce, B2B Marketplace & Digital Ordering Platform (`apps.commerce` / `IMP-036`)
- **Multi-Tenant Storefront & Digital Catalog**: `TenantStore` configuring tenant-branded digital stores and `StoreProduct` publishing medicines with B2C retail and B2B wholesale pricing.
- **Shopping Cart & Merge Engine**: `Cart` and `CartItem` supporting guest sessions and seamless guest-to-customer cart merging upon login.
- **Authoritative Checkout & Pricing**: `CheckoutService` calculating server-side pricing, validating `StoreCoupon` discount codes, and enforcing B2B customer credit limits against Accounts Receivable (`apps.accounts_receivable`).
- **Prescription Workflow & Controlled Drugs**: `OrderPrescription` upload and pharmacist verification workflow (`PrescriptionReviewService`), blocking checkout and fulfillment for unapproved Rx orders.
- **Double-Entry FEFO Order Fulfillment**: `OrderFulfillmentService` selecting earliest expiring batches and deducting inventory atomically via `StockMovementEngine` (`MovementType.SALE`).
- **Payments, Refunds & Tracking**: `CommercePayment`, `CommerceRefund`, and `OrderDelivery` with tracking numbers, and domain event publishing (`order.created`, `order.dispatched`, `prescription.approved`).
- **REST APIs**: Endpoints under `/api/v1/store/stores/`, `/api/v1/store/products/`, `/api/v1/store/cart/`, `/api/v1/store/checkout/`, `/api/v1/store/orders/`, `/api/v1/store/prescriptions/`, `/api/v1/store/payments/`.
- **Test Suite**: Created `tests/test_commerce.py` (566 total platform tests passing, 100% pass rate).

---

## [1.30.0] - 2026-08-15

### Added - Enterprise SaaS Super Admin & Platform Operations Center (`apps.platform_ops` / `IMP-035`)
- **System Health & Diagnostic Engine**: `SystemHealthCheck` and `SystemHealthSelector` executing live diagnostic probes on primary database, caching layers, and worker queue depths.
- **Global Maintenance Mode**: `SystemMaintenanceWindow` and `MaintenanceModeService` supporting scheduled maintenance windows with emergency bypass keys.
- **Audited Tenant Impersonation**: `TenantImpersonationLog` and `TenantImpersonationService` managing secure super-admin customer support sessions with session tokens and action counts.
- **Super Admin Tenant Lifecycle & Global Audit**: `TenantLifecycleAdminService` providing bulk tenant suspension (cascading to subscriptions), reactivation, and `PlatformAuditLog` tracking.
- **Progressive Feature Flags**: `GlobalFeatureFlag` and `FeatureFlagSelector` enabling progressive rollout percentages (0-100), whitelist/blacklist filtering, and tier targeting.
- **Platform Alerting & REST APIs**: `PlatformAlert` resolving infrastructure and security alerts. REST endpoints under `/api/v1/platform/overview/`, `/api/v1/platform/health/`, `/api/v1/platform/tenants/`, `/api/v1/platform/maintenance/`, `/api/v1/platform/feature-flags/`, `/api/v1/platform/alerts/`.
- **Test Suite**: Created `tests/test_platform_ops.py` (557 total platform tests passing, 100% pass rate).

---

## [1.29.0] - 2026-08-15

### Added - Enterprise SaaS Subscription, Billing & Licensing Platform (`apps.saas` / `IMP-034`)
- **Plan & Entitlement Engine**: `Plan`, `PlanVersion`, `PlanFeature`, `PlanPrice`, and `AddOn` models for tiered SaaS monetization (`Starter`, `Professional`, `Enterprise`) with limit enforcement (`max_users`, `max_branches`, `max_warehouses`).
- **Subscription Lifecycle & Licensing**: `SaaSSubscription` (`SUB-YYYY-XXXXXX`) and `SaaSLicense` (`LIC-YYYY-XXXXXX`) managing trial periods (14 days), active states, and automatic license key generation with cryptographic identity.
- **Proration & Upgrade Invoicing**: `ProrationCalculatorService` computing mid-cycle plan upgrades, calculating unused subscription credit, and issuing prorated `SaaSInvoice` (`SINV-YYYY-XXXXXX`) and `SaaSInvoiceLine` breakdown items.
- **Payments, Refunds & GL Integration**: `SaaSPaymentService` processing invoice settlements (`SPAY-YYYY-XXXXXX`), refunds (`SRFD-YYYY-XXXXXX`), and posting double-entry GL journals (`Debit Bank 1200, Credit Subscription Revenue 4000`) via `JournalPostingService`.
- **SaaS BI & Revenue Analytics**: `SaaSAnalyticsSelector` computing MRR, ARR, Churn, ARPU, active plan distribution, and historical billing revenue.
- **REST APIs**: Endpoints under `/api/v1/saas/plans/`, `/api/v1/saas/subscriptions/`, `/api/v1/saas/subscriptions/current/`, `/api/v1/saas/subscriptions/upgrade/`, and `/api/v1/saas/analytics/`.
- **Test Suite**: Created `tests/test_saas.py` (551 total platform tests passing, 100% pass rate).

---

## [1.28.0] - 2026-08-14

### Added - Enterprise Notifications & Automation Engine (`apps.notifications` / `IMP-033`)
- **Event-Driven Architecture & Transactional Outbox**: `DomainEvent` (`EVT-YYYY-XXXXXX`) and `OutboxEvent` for reliable transaction-safe event delivery with tenant-scoped idempotency key validation.
- **Multi-Channel Notification Engine**: `Notification` (`NOT-YYYY-XXXXXX`) supporting `IN_APP`, `EMAIL`, `SMS`, `PUSH`, `WEBHOOK`, and `WHATSAPP` channels across priorities (`LOW`, `NORMAL`, `HIGH`, `URGENT`, `CRITICAL`) and statuses (`PENDING`, `SENT`, `DELIVERED`, `READ`, `FAILED`, `DISMISSED`).
- **Template & Rule Engine**: Safe variable placeholder substitution (`TemplateEngineService`) for localized subjects/bodies (`ar`, `en`). Declarative condition rules (`RuleEngineService`) evaluating payload thresholds (`stock_lt`, `amount_gt`), resolving role/branch recipients, and enforcing alert deduplication cooldown.
- **Delivery Adapters & Security**: Multi-provider adapters (`NotificationDeliveryService`) executing In-App status updates, HMAC SHA256 Webhook signing (`X-PharmaCloud-Signature`), SSRF security URL protection (rejecting localhost/internal IP loopbacks), and Dead Letter Queue (`DeadLetterEvent`) logging.
- **REST APIs & Notification Center**: Published endpoints under `/api/v1/notifications/`, `/api/v1/notifications/unread/`, `/api/v1/notifications/{id}/read/`, `/api/v1/notifications/read-all/`, `/api/v1/notification-preferences/`.
- **Test Suite**: Created `tests/test_notifications.py` (544 total platform tests passing, 100% pass rate).

---

## [1.27.0] - 2026-08-14

### Added - Enterprise Advanced Reporting & Business Intelligence (`apps.reports` / `IMP-032`)
- **Reporting Architecture & Filter DTO Engine**: `ReportFilterDTO` standardizing tenant, company, branch, warehouse, customer, supplier, date range (Today, Yesterday, This Week, Last Week, This Month, Last Month, This Year, Last Year, Custom), and currency resolution.
- **Operational & Analytical Report Selectors**:
  - `SalesReportSelector`: Daily/monthly sales summaries, gross sales, net sales, invoice counts, average transaction value, sales by branch, cashier, and daily trend analysis.
  - `InventoryReportSelector`: Stock valuation summary, low stock alert queries, near expiry / expired stock risk analysis.
  - `PurchasingReportSelector`: Purchase order summary and supplier AP aging reports.
  - `FinancialReportSelector`: Authoritative Trial Balance, Profit & Loss, Balance Sheet, AR Aging, AP Aging, Cash & Treasury liquidity, and Expense summaries.
  - `ExecutiveDashboardSelector`: C-suite executive dashboard metrics and chart payload structures (line trend, bar charts).
- **KPI Engine & Multi-Format Export Engine**: `KpiEngineService` calculating period-over-period metric growth, difference deltas, and zero-division handling. `ReportExportService` exporting report records to CSV/JSON with audit logging (`ReportExportLog`).
- **Cross-Subledger Reconciliation Audit**: `ReportReconciliationService` auditing financial consistency across AR ↔ GL, AP ↔ GL, Cash/Bank ↔ GL, and Expense subledgers.
- **REST APIs**: Endpoints under `/api/v1/reports/sales/`, `/api/v1/reports/inventory/`, `/api/v1/reports/financial/`, `/api/v1/reports/dashboard/`, `/api/v1/reports/export/`, and `/api/v1/reports/reconciliation/`.
- **Test Suite**: Created `tests/test_reports.py` (536 total platform tests passing, 100% pass rate).

---

## [1.26.0] - 2026-08-14

### Added - Enterprise Expense & Operating Cost Management (`apps.expenses` / `IMP-031`)
- **Expense Categories & Pre-Approval Requests**: `ExpenseCategory` supporting parent-child hierarchy and default GL expense account linkage, and `ExpenseRequest` (`EXR-YYYY-XXXXXX`) for pre-approval workflows (`DRAFT` → `SUBMITTED` → `APPROVED` / `REJECTED`).
- **Expense Record & Line Breakdown Engine**: `Expense` header (`EXP-YYYY-XXXXXX`) and `ExpenseLine` items detailing operational expenditures across departments and cost centers.
- **Posting & Multi-Channel Financial Settlement Engine**: `ExpensePostingService` executing double-entry GL journal posting via `JournalPostingService` (`Debit Expense 6000, Credit Cash 1100` / `Credit Bank 1200` / `Credit AP 2100` / `Credit Employee Payable 2000`) and integrating with Cash, Bank, Accounts Payable subledger (`SupplierInvoice`), and Employee Reimbursement (`EmployeeExpense`).
- **Recurring Expense Schedule Automation**: `RecurringExpenseService` automating recurring expense schedules (`DAILY`, `WEEKLY`, `MONTHLY`, `QUARTERLY`, `YEARLY`) with duplicate protection per period.
- **Immutable Reversals & Budget Foundation**: `ExpenseReversalService` executing immutable reversals (`EXV-YYYY-XXXXXX`) via compensating GL entries. `ExpenseBudget` allocating and tracking budget vs actual expenditure.
- **REST APIs & Expense Analytics**: Published endpoints under `/api/v1/expense-categories/`, `/api/v1/expense-requests/`, `/api/v1/expenses/`, `/api/v1/employee-expenses/`, `/api/v1/expense-budgets/`, and `/api/v1/expense-analytics/`.
- **Test Suite**: Created `tests/test_expenses.py` (530 total platform tests passing, 100% pass rate).

---

## [1.25.0] - 2026-08-12

### Added - Enterprise Cash, Bank & Financial Reconciliation (`apps.cash_and_bank` / `IMP-030`)
- **Treasury Accounts & Cash Management**: Implemented `CashAccount` and `BankAccount` models supporting GL chart of account linkage and ledger balance tracking.
- **Cashier Session Closing & Variance Engine**: Created `CashSessionReconciliationService` managing POS shift session closing, actual vs expected cash count reconciliation, and automated `CashVariance` (`CVR-YYYY-XXXXXX`) logging for shortages (-100) or overages (+100).
- **Treasury Operations Engine**: Created `TreasuryOperationsService` executing Cash Deposits (`DEP-YYYY-XXXXXX`, Cash -> Bank) and Cash Withdrawals (`WTH-YYYY-XXXXXX`, Bank -> Cash) with double-entry GL journal posting via `JournalPostingService` (`Debit Bank 1200, Credit Cash 1100` / `Debit Cash 1100, Credit Bank 1200`).
- **Bank Statement Import & Duplicate Protection**: Created `BankStatementImportService` importing statement lines with sha256 `import_hash` fingerprinting to prevent duplicate statement transaction imports.
- **Financial Reconciliation & Exception Matching**: Created `FinancialReconciliationService` managing `BankReconciliation` (`REC-YYYY-XXXXXX`) sessions, linking statement transactions to book entries (`ReconciliationMatch`), and logging unreconciled items (`ReconciliationException`).
- **REST APIs & Treasury Summary**: Published endpoints under `/api/v1/cash/accounts/`, `/api/v1/cash/deposits/`, `/api/v1/cash/withdrawals/`, `/api/v1/cash/transfers/`, `/api/v1/banks/accounts/`, `/api/v1/banks/transactions/`, `/api/v1/banks/reconciliations/`, and `/api/v1/financial-reconciliation/`.
- **Test Suite**: Created `tests/test_cash_and_bank.py` (524 total platform tests passing, 100% pass rate).

---

## [1.24.0] - 2026-08-11

### Added - Enterprise General Ledger & Double-Entry Accounting (`apps.general_ledger` / `IMP-029`)
- **Chart of Accounts Engine**: Created `ChartOfAccount` model supporting 6 account types (`ASSET`, `LIABILITY`, `EQUITY`, `REVENUE`, `EXPENSE`, `COST_OF_GOODS_SOLD`), control account protection, and automated default system account seeding.
- **Double-Entry Journal Posting Engine**: Created `JournalPostingService` enforcing strict `Total Debits == Total Credits` double-entry rules and `AccountingPeriod` lock verification.
- **Immutable Journal Reversal Engine**: Created `JournalReversalService` executing compensating reversal journals (`Original Debit -> Reversal Credit`).
- **Operational GL Integrations**: Created `GLIntegrationPostingService` posting balanced double-entry journals for POS sales, customer payments, supplier bills, supplier payments, and COGS inventory movements.
- **Financial Statements & Reconciliation**: Created `GLSelector` and `GLReconciliationService` computing Trial Balance, Profit & Loss, Balance Sheet, and subledger audit reconciliation.
- **REST APIs**: Published endpoints under `/api/v1/accounting/accounts/`, `/api/v1/accounting/journals/`, `/api/v1/accounting/periods/`, and `/api/v1/accounting/reports/`.
- **Test Suite**: Created `tests/test_general_ledger.py` (515 total platform tests passing, 100% pass rate).

---

## [1.23.0] - 2026-08-11

### Added - Enterprise Customer Accounts Receivable (AR) (`apps.accounts_receivable` / `IMP-028`)
- **AR Subledger Engine**: Implemented `CustomerReceivable` model (`AR-YYYY-XXXXXX`) tracking customer financial obligations created by credit sales, POS invoices, or manual entries.
- **Credit Sales & Credit Limit Checks**: Created `CustomerReceivableService` integrating POS credit sales without duplicating sales invoices, enforcing credit limits and updating customer debt balances (`customer.current_balance`).
- **Customer Payments & Allocations**: Implemented `CustomerPayment` (`CPY-YYYY-XXXXXX`) and `CustomerPaymentAllocation` supporting multi-receivable payment allocation, partial payments, full payments, and overpayment policy enforcement.
- **Adjustments & Bad Debt Write-Offs**: Created `ReceivableAdjustment` (`ADJ-YYYY-XXXXXX`) and `ReceivableWriteOff` (`WOF-YYYY-XXXXXX`) for debit/credit adjustments and bad debt write-offs with separation of duties enforcement.
- **Disputes & Payment Reversals**: Created `ReceivableDispute` (`DSP-YYYY-XXXXXX`) for invoice disputes and payment reversals restoring receivable balances and customer debt.
- **AR Aging & Statements**: Created `ReceivableSelector` calculating AR aging buckets (Current, 1-30, 31-60, 61-90, 90+ days) and generating customer ledger statements with running balances.
- **AR Reconciliation Service**: Created `ARReconciliationService` auditing subledger integrity.
- **REST APIs**: Published endpoints under `/api/v1/accounts-receivable/`, `/api/v1/customer-payments/`, `/api/v1/customer-statements/`, and `/api/v1/ar-analytics/`.
- **Test Suite**: Created `tests/test_accounts_receivable.py` (507 total tests passing, 100% pass rate).

---

## [1.22.0] - 2026-08-11

### Added - Enterprise Prescription Management & Pharmacy Dispensing (`apps.prescriptions` / `IMP-027`)
- **Prescription Document Engine**: Implemented `Prescription` and `PrescriptionLine` models (`RX-YYYY-XXXXXX`) managing clinical prescription lifecycle (`DRAFT` → `PENDING_VERIFICATION` → `VERIFIED` → `PARTIALLY_DISPENSED` → `FULLY_DISPENSED`).
- **Clinical Verification & Controlled Substances**: Implemented `verify_prescription` enforcing doctor license checks for Narcotics and Class A/B Controlled drugs.
- **Pharmacy Dispensing & FEFO Batch Allocation**: Created `PharmacyDispensingService.dispense_prescription` generating `PrescriptionDispense` (`DISP-YYYY-XXXXXX`) with FEFO batch selection.
- **Authoritative Stock Deduction**: Stock reduction during dispensing is executed strictly via `StockMovementEngine` (`SALE` movement type) inside `@transaction.atomic` blocks with `select_for_update()` row locking. Zero direct inventory mutations.
- **Dispensing Reversals & Refills**: Implemented `reverse_dispensation` restoring stock strictly via compensating `SALE_RETURN` stock movements and updating line refill balances.
- **REST APIs & Clinical Statistics**: Published endpoints under `/api/v1/prescriptions/` and `/api/v1/dispensations/` (`/verify/`, `/dispense/`, `/reverse/`, `/statistics/`).
- **Test Suite**: Created `tests/test_prescriptions.py` (498 total tests passing, 100% pass rate).

---

## [1.21.0] - 2026-08-11

### Added - Enterprise Customer Sales Returns & Refund Management (`apps.sales_returns` / `IMP-026`)
- **Customer Returns Engine**: Implemented `CustomerReturn` and `CustomerReturnLine` models (`CRT-YYYY-XXXXXX`) managing customer sales returns against `SalesInvoice` (`DRAFT` → `REQUESTED` → `APPROVED` → `INSPECTION` → `ACCEPTED` / `PARTIALLY_ACCEPTED` / `REJECTED`).
- **Return Eligibility & Quantity Validation**: Created `validate_returnable_quantity` enforcing line-by-line returnable limits (`requested_quantity <= original_sold - previously_returned`).
- **Quality Inspection & Stock Restoration**: Implemented `inspect_and_accept_return` logging accepted/rejected quantities and restoring stock strictly via `StockMovementEngine` (`SALE_RETURN` for sealed stock, `QUARANTINE` for damaged stock) with zero direct quantity mutations.
- **Refund Disbursements & Store Credit**: Created `CustomerRefund` (`REF-YYYY-XXXXXX`) supporting cash, card, bank transfer, and store credit refunds (adjusting customer account balance).
- **Return Reversals & Separation of Duties**: Implemented `reverse_customer_return` creating compensating `SALE` movements via `StockMovementEngine` and reversing customer store credit. Enforced creator != approver separation of duties.
- **REST APIs & Return Analytics**: Published endpoints under `/api/v1/customer-returns/` and `/api/v1/customer-refunds/` (`/approve/`, `/inspect/`, `/process-refund/`, `/reverse/`, `/statistics/`).
- **Test Suite**: Created `tests/test_sales_returns.py` (491 total tests passing, 100% pass rate).

---

## [1.20.0] - 2026-08-11

### Added - Enterprise POS & Sales Management (`apps.sales` / `IMP-025`)
- **POS Retail Counter & Cart Engine**: Implemented `SalesInvoice` and `SalesInvoiceLine` models (`INV-YYYY-XXXXXX`) supporting retail checkout and cart management (`DRAFT` -> `HELD` -> `COMPLETED` -> `VOIDED`).
- **FEFO Batch Allocation**: Created `FEFOBatchSelector` automatically allocating the earliest expiring valid medicine batch while filtering out expired, recalled, or quarantined batches.
- **Authoritative Stock Reduction**: Completing a sale reduces physical inventory strictly through `StockMovementEngine` (`SALE` movement type) with zero direct quantity mutations and pessimistic DB row locking.
- **Payments, Change & Customer Credit**: Created `SalesPayment` (`PAY-YYYY-XXXXXX`) supporting cash, card, mobile wallet, split payments, cash change calculation, and customer credit sales with credit limit validation.
- **Void Workflow & Stock Restoration**: Implemented `void_completed_sale` creating compensating `SALE_RETURN` movements via `StockMovementEngine` and restoring customer credit balance.
- **Cash Registers & Shift Sessions**: Created `CashRegister` (`REG-YYYY-XXXXXX`) and `RegisterSession` (`SES-YYYY-XXXXXX`) for managing cashier shift sessions and till cash reconciliation (calculating expected cash vs actual count variance).
- **REST APIs & Barcode Search**: Endpoints published under `/api/v1/sales/`, `/api/v1/pos/`, `/api/v1/cash-registers/`, `/api/v1/register-sessions/` (`/complete/`, `/void/`, `/lookup/barcode/`, `/analytics/`).
- **Test Suite**: Created `tests/test_sales.py` (480 total tests passing, 100% pass rate).

---

## [1.19.0] - 2026-08-11

### Added - Enterprise Supplier Invoices & Accounts Payable Foundation (`apps.accounts_payable` / `IMP-024`)
- **Vendor Bill & Invoice Engine**: Created `SupplierInvoice` and `SupplierInvoiceLine` models (`INV-YYYY-XXXXXX`) for managing vendor bills (`DRAFT` -> `VERIFIED` -> `APPROVED` -> `POSTED` -> `PARTIALLY_PAID` -> `PAID`).
- **Three-Way Matching Engine**: Implemented `ThreeWayMatchService` comparing PO, Goods Receipt, and Invoice lines to detect `MATCHED`, `QUANTITY_VARIANCE`, `PRICE_VARIANCE`, `RECEIPT_MISSING`, and `SUPPLIER_MISMATCH`.
- **AP Subledger & Duplicate Detection**: Created `AccountsPayableEntry` (`AP-YYYY-XXXXXX`) for tracking outstanding vendor balances. Enforces duplicate bill detection by `(tenant, supplier, supplier_invoice_number)`.
- **Supplier Payments & Credit Note Integration**: Created `SupplierPayment` (`PAY-YYYY-XXXXXX`) and `CreditApplication` applying `SupplierCreditNote` (from IMP-023) against open payables. Supports partial payments, full payments, overpayment prevention, and payment reversals.
- **AP Aging & Supplier Balance Analytics**: Provided `calculate_ap_aging` breakdown (Current, 1-30, 31-60, 61-90, 90+ days) and net supplier balance summary.
- **REST APIs & Test Suite**: Published endpoints under `/api/v1/supplier-invoices/`, `/api/v1/supplier-payments/`, `/api/v1/accounts-payable/` and created `tests/test_accounts_payable.py` (469 total tests passing, 100% pass rate).

---

## [1.18.0] - 2026-08-11

### Added - Enterprise Purchase Returns & Supplier Returns (`apps.purchase_returns` / `IMP-023`)
- **Supplier Returns Engine**: Created `PurchaseReturn` and `PurchaseReturnLine` models (`PRT-YYYY-XXXXXX`) returning stock against Goods Receipts and Purchase Orders (`DRAFT` -> `REQUESTED` -> `APPROVED` -> `DISPATCHED` -> `ACCEPTED` / `DISCREPANCY`).
- **Stock Movement Integration**: Implemented `dispatch_purchase_return` executing physical stock removals strictly through `StockMovementEngine` (`PURCHASE_RETURN`) with zero direct quantity mutations and stock balance validations.
- **Supplier Acceptance & Discrepancy Tracking**: Created `ReturnDiscrepancy` (`DISC-YYYY-XXXXXX`) for quantity shortages/rejections and `SupplierCreditNote` (`CRN-YYYY-XXXXXX`) foundation for accepted values.
- **Reversal Engine & Separation of Duties**: Supports compensating return reversal movements restoring inventory balance. Enforces creator != approver separation of duties.
- **REST APIs & Test Suite**: Published endpoints under `/api/v1/purchase-returns/` and created `tests/test_purchase_returns.py` (457 total tests passing, 100% pass rate).

---

## [1.17.0] - 2026-08-11

### Added - Enterprise Goods Receipt & Receiving Management (`apps.goods_receipt` / `IMP-022`)
- **Physical Goods Receiving Engine**: Created `GoodsReceipt` and `GoodsReceiptLine` models (`GRN-YYYY-XXXXXX`) supporting draft receiving, quality status checks, cold chain temperature excursion tracking, and PO matching.
- **Batch Management Integration**: Automatic `Batch` creation/reuse with expiry date validation and recalled/blocked batch rejection.
- **Authoritative Stock Movement Posting Engine**: Implemented `post_goods_receipt` executing physical stock entries strictly through `StockMovementEngine` (`RECEIPT` / `QUARANTINE` / `DAMAGE`) with zero direct quantity mutations.
- **PO Quantity Reconciliation & Reversals**: Reconciles PO line quantities, updates PO statuses (`PARTIALLY_RECEIVED`, `FULLY_RECEIVED`), and supports compensating `reverse_goods_receipt` workflows.
- **REST APIs & Test Suite**: Published endpoints under `/api/v1/goods-receipts/` and created `tests/test_goods_receipt.py` (450 total tests passing, 100% pass rate).

---

## [1.16.0] - 2026-08-11

### Added - Enterprise Purchasing & Purchase Order Management (`apps.procurement` / `IMP-021`)
- **Purchase Requisition Engine**: Created `PurchaseRequisition` and `PurchaseRequisitionLine` models (`PR-YYYY-XXXXXX`) managing internal purchase requests (`DRAFT` -> `SUBMITTED` -> `APPROVED` / `REJECTED`).
- **Purchase Order Engine**: Created `PurchaseOrder` and `PurchaseOrderLine` models (`PO-YYYY-XXXXXX`) for supplier commitments (`DRAFT` -> `PENDING_APPROVAL` -> `APPROVED` -> `SENT_TO_SUPPLIER` -> `ACKNOWLEDGED` -> `PARTIALLY_RECEIVED` -> `FULLY_RECEIVED` -> `CLOSED`). Zero direct inventory mutation.
- **Requisition to PO Conversion Engine**: Implemented `convert_requisition_to_purchase_order` service converting approved requisitions into POs grouped by supplier with row-locking idempotency protection.
- **Controlled Amendments & Separation of Duties**: Created `PurchaseOrderAmendment` audit model for approved order modifications and enforced creator != approver separation of duties.
- **REST APIs & Test Suite**: Published endpoints under `/api/v1/purchase-requisitions/`, `/api/v1/purchase-orders/`, `/api/v1/supplier-prices/`, and created `tests/test_procurement.py`.

---

## [1.15.0] - 2026-08-11

### Added - Enterprise Expiry, Recall & Inventory Alert Management (`apps.alerts` / `IMP-020`)
- **Alert Scanner Engine**: Implemented `AlertScannerService` scanning active inventory balances and pharmaceutical batch expiry dates, generating/updating real-time `InventoryAlert` records for low stock, out of stock, near expiry (30/60/90 days), and expired stock.
- **Batch Recall & Auto-Quarantine Engine**: Implemented `BatchRecallService` managing formal pharmaceutical recall orders (`RCL-YYYY-XXXXXX`), setting batch status to `RECALLED`, and executing automated stock quarantining across all storage locations via `StockMovementEngine` (`QUARANTINE` movement type).
- **Acknowledgment & Resolution Lifecycle**: Complete lifecycle tracking (`ACTIVE` → `ACKNOWLEDGED` → `RESOLVED` / `DISMISSED`) with user accountability and resolution notes.
- **REST APIs & Document Generation**: Implemented ViewSets, serializers, and URL routing under `/api/v1/alerts/` and `/api/v1/recalls/` with sequential number generation (`ALT-YYYY-XXXXXX`, `RCL-YYYY-XXXXXX`).
- **Automated Test Suite**: Created `tests/test_alerts.py` covering models, `AlertScannerService`, `BatchRecallService`, automatic stock quarantining via `StockMovementEngine`, alert acknowledgment, resolution, selectors, statistics, and tenant isolation (428 total tests passing, 100% pass rate).

---

## [1.14.0] - 2026-08-09

### Added - Enterprise Inter-Branch & Warehouse Stock Transfer (`apps.stock_transfer` / `IMP-019`)
- **Stock Transfer Workflow Engine**: Implemented `StockTransferService` managing the complete transfer lifecycle: `DRAFT` → `REQUESTED` → `APPROVED` → `PICKING` → `READY_FOR_DISPATCH` → `DISPATCHED` / `IN_TRANSIT` → `RECEIVED` / `PARTIALLY_RECEIVED` / `DISCREPANCY` → `CLOSED`.
- **FEFO-Aware Stock Picking**: Implemented automatic FEFO batch selection for transfer lines without specified batches, filtering out expired, recalled, or quarantined lots.
- **Atomic Double-Entry Dispatch & Receiving**: Integrated with `StockMovementEngine` to generate authoritative double-entry movements (`TRANSFER_OUT` and `TRANSFER_IN`) with zero direct inventory balance mutations.
- **Discrepancy & Damage Tracking Engine**: Automated discrepancy record creation (`StockTransferDiscrepancy`) for quantity shortages, overages, damaged goods during transit (`DAMAGE` movements), wrong batch, and wrong medicine delivery.
- **Separation of Duties & Reversal System**: Enforced separation of duties between transfer requester and approver. Implemented clean compensating double-entry reversals (`reverse_transfer`) preventing double reversals.
- **REST APIs & Document Generation**: Implemented ViewSets, serializers, and URL routing under `/api/v1/stock-transfers/` and `/api/v1/transfer-discrepancies/` with sequential number generation (`TRF-YYYY-XXXXXX`, `DISC-YYYY-XXXXXX`).
- **Automated Test Suite**: Created `tests/test_stock_transfer.py` covering models, service workflow lifecycle, FEFO picking, dispatching, receiving, partial receiving, discrepancies, damage, wrong batch/medicine, cancellation, reversal, idempotency, tenant isolation, and selectors (416 total tests passing, 100% pass rate).

---

## [1.13.0] - 2026-08-09

### Added - Enterprise Stock Adjustment & Stock Count (`apps.stock_adjustment` / `IMP-018`)
- **Authoritative Stock Movement Engine**: Implemented `StockMovementEngine` executing double-entry inventory quantity modifications atomically inside `@transaction.atomic` blocks with `select_for_update()` pessimistic DB row locking.
- **Movement Types & Statuses**: Complete support for `OPENING_BALANCE`, `RECEIPT`, `ISSUE`, `SALE`, `SALE_RETURN`, `PURCHASE_RETURN`, `TRANSFER_OUT`, `TRANSFER_IN`, `ADJUSTMENT_IN`, `ADJUSTMENT_OUT`, `DAMAGE`, `EXPIRY`, `QUARANTINE`, `QUARANTINE_RELEASE`, `RESERVATION`, `RESERVATION_RELEASE`, `CORRECTION`, `RECALL`, `OTHER`.
- **Reversal Engine**: Implemented `reverse_movement(...)` creating compensating reversal movements, reversing line quantities, and preventing duplicate reversals.
- **FEFO Batch Allocation & Idempotency**: Automatic FEFO batch selection for outgoing issues/sales when unspecified, and tenant-scoped `idempotency_key` duplicate protection.
- **Sequence Generator**: Collision-safe document sequence code generator (`STK-2026-XXXXXX`, `TRF-2026-XXXXXX`, `REC-2026-XXXXXX`, `ISS-2026-XXXXXX`).
- **REST APIs**: Published endpoints under `/api/v1/stock-movements/` for CRUD, status processing (`/process/`, `/cancel/`, `/reverse/`), operational shortcuts (`/receive/`, `/issue/`, `/transfer/`), traceability reporting (`/traceability/`), and movement stats (`/stats/`).
- **Automated Test Suite**: Added `test_stock_movement_models.py`, `test_stock_movement_engine.py`, `test_stock_movement_concurrency.py`, `test_stock_movement_selectors.py`, `test_stock_movement_api.py`, and `test_stock_movement_isolation.py` (368 total tests passing, 100% pass rate).

---

## [1.11.0] - 2026-08-09

### Added - Enterprise Inventory & Batch Management (`apps.inventory` / `IMP-016`)
- **Pharmaceutical Batch Engine**: Implemented `Batch` entity (`FullAuditModel`, `TenantAwareModel`) supporting batch number, lot number, manufacturing date, expiry date, registration number, country of origin, unit cost, selling price, storage requirements, and compliance status (`active`, `quarantine`, `expired`, `recalled`, `blocked`, `depleted`, `archived`).
- **Stock Position Balance Engine**: Implemented `InventoryItem` representing stock position of a medicine batch at a storage location within a warehouse. Enforces Decimal precision, non-negative quantity check constraints, available quantity calculation (`on_hand - reserved - damaged - quarantine`), unit cost, average cost (weighted average calculation), and last cost tracking.
- **Concurrency & Thread Safety**: Concurrency-safe service methods implementing `transaction.atomic` and pessimistic DB row locks (`select_for_update`) during quantity adjustments, reservations, and reservation releases to prevent race conditions or negative stock.
- **FEFO & Recall Readiness**: `BatchSelector.get_available_batches_fefo()` for First Expired First Out selection, and `InventoryItemSelector.find_inventory_for_recall()` for cross-warehouse recall lookup.
- **Auditable Transactions**: Implemented `InventoryTransaction` recording all quantity-changing stock movements with quantity before/after, user accountability, and reference tracking.
- **REST APIs**: Published endpoints under `/api/v1/inventory/`, `/api/v1/batches/`, and `/api/v1/inventory-transactions/` for CRUD, status management (`/block/`, `/unblock/`, `/recall/`), stock adjustments (`/adjust/`), stock reservations (`/reserve/`), inventory summary (`/summary/`), FEFO lookup (`/fefo/`), and recall lookup (`/recall-lookup/`).
- **Automated Test Suite**: Added `test_inventory_models.py`, `test_inventory_services.py`, `test_inventory_concurrency.py`, `test_inventory_selectors.py`, `test_inventory_api.py`, and `test_inventory_isolation.py` (358 total tests passing, 100% pass rate).

---

## [1.10.0] - 2026-08-08

### Added - Enterprise Warehouse & Storage Location Management (`apps.warehouses` / `IMP-015`)
- **Warehouse Entity & Domain**: Implemented `Warehouse` entity (`FullAuditModel`, `TenantAwareModel`) supporting code, name, names in Arabic/English, warehouse types (`main`, `pharmacy`, `branch`, `distribution_center`, `cold_storage`, `controlled_drug`, `quarantine`, `returns`, `damaged`, `transit`, `virtual`, `other`), status lifecycle (`draft`, `active`, `inactive`, `suspended`, `temporarily_closed`, `archived`), tenant, company, optional branch, manager assignment validation, contact info, geolocation, working hours, and default storage role flags.
- **Hierarchical Storage Location Engine**: Implemented `StorageLocation` entity supporting recursive depth (Warehouse → Zone → Aisle → Rack → Shelf → Bin / Cabinet / Freezer / Room), status lifecycle (`active`, `inactive`, `maintenance`, `blocked`, `full`), capacity & current utilization foundation, environmental control parameters (temperature range, humidity range), and storage conditions.
- **Hierarchy Integrity & Validation**: Full breadcrumb pathing (`get_full_path()`), prevention of circular parentage, and strict cross-warehouse parent assignment enforcement.
- **REST APIs**: Published endpoints under `/api/v1/warehouses/` and `/api/v1/storage-locations/` for CRUD, filtering, search, status transitions (`/activate/`, `/deactivate/`, `/suspend/`, `/close-temporarily/`, `/restore/`), manager assignment (`/assign-manager/`), fast lookup (`/search/`), statistics (`/stats/`), location tree representation (`/tree/`), and location move operations (`/move/`).
- **Automated Test Suite**: Added `test_warehouses_models.py`, `test_warehouses_hierarchy.py`, `test_warehouses_services.py`, `test_warehouses_api.py`, and `test_warehouses_isolation.py` (346 total tests passing, 100% pass rate).

---

## [1.9.0] - 2026-08-08

### Added - Enterprise Customer Management (`apps.customers` / `IMP-014` / `P008`)
- **Customer Identity & Domain Model**: Implemented `Customer` entity (`FullAuditModel`, `TenantAwareModel`) supporting code, customer number, customer type (`individual`, `organization`, `corporate`, `insurance`, `walk_in`, `anonymous`), status (`active`, `inactive`, `blocked`, `suspended`, `archived`), names (Arabic, English, preferred), personal information (gender, DOB, national ID, passport, nationality, occupation, photo), contacts, preferences, financial profile (credit limit, opening/current balance, credit status, terms, discount eligibility), classification, loyalty foundation, and insurance coverage foundation.
- **Multi-Address Support**: Implemented `CustomerAddress` entity supporting home, work, billing, delivery and custom address types with primary/default switching and geolocation (latitude/longitude/Google Maps URL).
- **Customer Medical Profile Foundation**: Implemented `CustomerMedicalProfile` supporting blood type, allergies, chronic conditions, emergency contact, physician/pharmacy preferences, and insurance notes with restricted access permissions (`customers.medical_profile.read`, `customers.medical_profile.update`).
- **Duplicate Detection Engine**: Non-destructive `CustomerDuplicateDetector` scoring phone, email, national ID, passport, insurance member number, and name similarity.
- **REST APIs**: Published endpoints under `/api/v1/customers/` for CRUD, filtering, search, status transitions (`/activate/`, `/deactivate/`, `/block/`, `/unblock/`, `/suspend/`, `/restore/`), fast lookup (`/search/`), duplicate detection (`/duplicates/`), statistics (`/stats/`), addresses (`/addresses/`), and medical profiles (`/medical-profile/`).
- **Automated Test Suite**: Added `test_customers_models.py`, `test_customers_services.py`, `test_customers_api.py`, `test_customers_isolation.py`, and `test_customers_duplicate.py` (336 total tests passing, 100% pass rate).

---

## [1.8.0] - 2026-08-07

### Added - Enterprise Supplier Management (`apps.suppliers` / `IMP-013`)
- **Supplier Profile & Domain**: Implemented `Supplier` model (`UUIDBase`, `FullAuditModel`, `TenantAwareModel`) supporting code, legal name, display name, supplier type (`manufacturer`, `distributor`, `wholesaler`, `importer`, `agent`, `service_provider`), supplier category, registration number, tax number, VAT number, and status (`active`, `inactive`, `suspended`, `blacklisted`, `archived`).
- **Contact, Geolocation & Financial Data**: Primary/secondary contacts, multi-channel phone/WhatsApp/mobile/email, physical address & geolocation (lat/long, Google Maps link), financial parameters (currency, payment terms, credit limit, balances, bank account, IBAN, SWIFT, tax category).
- **Licensing & Compliance Rating**: Commercial registration, drug license, license expiry dates, insurance info, preferred supplier flag, blacklisted flag, 5-star rating, and risk level (`low`, `medium`, `high`, `critical`).
- **REST APIs**: Published endpoints under `/api/v1/suppliers/` for CRUD, filtering, search, activate (`/activate/`), suspend (`/suspend/`), blacklist (`/blacklist/`), restore (`/restore/`), bulk import (`/import/`), export (`/export/`), and statistics (`/stats/`).
- **Automated Test Suite**: Added `test_suppliers_models.py`, `test_suppliers_services.py`, `test_suppliers_api.py`, and `test_suppliers_isolation.py` (331 total tests passing, 100% pass rate).

---

## [1.7.0] - 2026-08-07

### Integrated - Enterprise Pharmaceutical Reference Data Engine & Medicine Integration (`apps.references` & `apps.medicines` / `IMP-012`)
- Added optional ForeignKey relationships on `Medicine` (`category_ref`, `manufacturer_ref`, `dosage_form_ref`, `unit_of_measure_ref`, `tax_category_ref`) with string fallback attributes.
- Generated database migration `0003_medicine_category_ref_medicine_dosage_form_ref_and_more.py`.

---

## [1.6.0] - 2026-08-07

### Enhanced - Enterprise Medicine Master Catalog (`apps.medicines` / `IMP-011`)
- Enhanced `Medicine` model with commercial name, search keywords, drug classification, approval date, registration expiry, safety flags, and pricing controls.
- Upgraded `MedicineSelector` and REST APIs with enterprise multi-field search engine.

---

## [1.5.0] - 2026-08-07

### Added - Enterprise Pharmaceutical Reference Data (`apps.references` / `IMP-012`)
- Added master reference data models (`MedicineCategory` tree, `Manufacturer`, `DosageForm`, `StrengthUnit`, `UnitOfMeasure`, `PackageType`, `RouteOfAdministration`, `AtcClassification` WHO 5-level hierarchy, `StorageCondition`, `TaxCategory`).

---

## [1.4.0] - 2026-08-07

### Added - Enterprise Medicine Master Data (`apps.medicines` / `IMP-011`)
- Added master pharmaceutical catalog (`Medicine`) with classifications, clinical safety flags, barcode/SKU lookups, and bulk import/export.

---

## [1.3.0] - 2026-08-07

### Added - Enterprise User Management (`apps.users` / `IMP-010`)
- Added HR & employment profile extension (`EmployeeProfile`) linking users to Company, primary Branch, and secondary branches.

---

## [1.2.0] - 2026-08-07

### Added - Branch Management (`apps.branches` / `IMP-009`)
- Added physical pharmacy & warehouse branch locations (`Branch` & `BranchSettings`).

---

## [1.1.0] - 2026-08-07

### Added - Company Management (`apps.companies` / `IMP-008`)
- Added legal business entity root (`Company` & `CompanySettings`).

---

## [1.0.0] - 2026-08-07

### Added - Platform Foundation & Core Services
- Baseline Auth, Dynamic RBAC, and Tenant Management (`apps.tenants` / `IMP-007`).
