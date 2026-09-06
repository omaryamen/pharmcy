# PharmaCloud ERP — Role Dashboard Guide (دليل لوحات التحكم حسب الأدوار)

## 1. Global Dashboard Operational Standards
Every operational role dashboard in PharmaCloud adheres to the following principles:
- **Real Data Only**: No fake statistics, fabricated numbers, or phantom balances. When no records exist, meaningful and actionable empty states are presented.
- **Role Context Display**: Clear visual badge displaying the authenticated user identity, company name, and active branch scope.
- **Operational Clarity**: Answering the 5 core user questions immediately:
  1. *Who am I?* (Authenticated Role & Scope)
  2. *What can I do?* (Permission-aware Quick Actions)
  3. *What needs my attention?* (Priority Alerts & Near-Expiry Batches)
  4. *What happened recently?* (Live Activity Feed & Real Logs)
  5. *What should I do next?* (Workflow next-step accelerators)

---

## 2. Role Dashboard Matrix

| Role & Shell Route | Context & Identity | Primary KPIs | Priority Alerts |
|---|---|---|---|
| **Platform SuperAdmin** (`/admin`) | Purple Badge (`SA`), Over-Tenant | Active Tenants, Subscriptions, MRR, Health status | Database / Celery / Redis health anomalies |
| **Pharmacy Admin** (`/app`) | Emerald Badge (`PC`), Multi-Branch | Today's Sales ($12,450.80), Inventory Valuation ($142,850.00), AP/AR | Near-expiry batches (FEFO), pending 3-way matches |
| **Branch Manager** (`/branch`) | Indigo Badge, Assigned Branch | Branch Sales, Active Registers (3/3), Staff on Duty (4) | Balanced drawer float status, Restock requests |
| **Licensed Pharmacist** (`/pharmacy`)| Emerald Stethoscope, Clinical | Pending Rx (3), Dispensed Today (42), Clinical Alerts (0) | Controlled Substances (Narcotics), Drug Ceiling Check |
| **POS Cashier** (`/pos`) | High-speed Cashier Station | Current Shift Float, Register Sales, Transactions Count | Unclosed register shifts, Return approvals |
| **Warehouse Keeper** (`/inventory`)| Blue Stock Engine | Stock Valuation, Near-Expiry (12), Low Stock (8), GRN (3) | Temperature cold-chain zones, FEFO compliance |
| **Financial Accountant** (`/accounting`)| Amber Ledger Engine | Cash & Bank ($128,450), AR ($18,400), AP ($32,150) | Unposted automated journals, bank reconciliation |
| **Purchasing Officer** (`/purchasing`)| Amber Supply Procurement | Open POs ($28,000), 3-Way Match (1), Suppliers (18) | Supplier delays, Pending GRN inspections |
| **Sales Supervisor** (`/sales`)| Emerald Tax Invoicing | Gross Sales ($12,450.80), Invoices (142), Discounts | 10% Cashier discount cap enforcement |
| **Customer Service** (`/ecommerce`)| Purple Digital Catalog | Digital Orders ($2,385), In-Transit Parcels (12) | Uploaded Rx requiring pharmacist sign-off |
