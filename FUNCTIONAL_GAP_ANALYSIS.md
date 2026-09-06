# PharmaCloud ERP — Functional Gap Analysis

## 1. Assessment of Implemented vs Operational Workflows

| Area | Implemented Backend API | Frontend Implementation | Gap Status | Recommendation |
|---|---|---|---|---|
| **POS Barcode Dispensing** | Full REST endpoints with FEFO batch deduction | Interactive Cashier UI with real-time cart | Operational | Add shortcut keys (F2 for cash, F4 for card). |
| **Prescription Verification** | Clinical state engine with pharmacist approval | Queue review & Controlled medication badges | Operational | Add electronic signature stamp display. |
| **Stock Adjustments & Counts** | `apps/stock_adjustment/` and `apps/stock_movement/` | Inventory table with filter & status badges | Minor UI Gap | Create dedicated stock physical count sheet dialog. |
| **Supplier Directory** | `apps/suppliers/` full CRUD endpoints | Purchasing table displays supplier names | Minor UI Gap | Add dedicated master supplier contact profile modal. |
| **Customer Credit Accounts** | `apps/customers/` and `apps/accounts_receivable/` | Sales table lists customer credit invoices | Minor UI Gap | Add dedicated customer account ledger statement view. |
| **Financial Journals** | `apps/general_ledger/` double-entry engine | Recent auto-posted journals list | Operational | Add manual custom journal entry creation modal. |
| **Platform Ops & Health** | `apps/platform_ops/` SystemHealthCheck | Super admin metrics card & audit logs | Operational | Add direct trigger button for manual backup execution. |
