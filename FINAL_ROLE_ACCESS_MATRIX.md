# PharmaCloud ERP — Final Role Access & Scope Matrix (مصفوفة صلاحيات ونطاق الأدوار النهائية)

| Role Code | Primary Shell | Allowed Routes | Permitted Core Modules | Scope Boundary | Strictly Forbidden Areas |
|---|---|---|---|---|---|
| **superadmin** | `/admin` | `/admin/*` | SaaS Plans, Tenants, System Health, Maintenance | Over-Tenant Global | Individual Pharmacy Patient Records |
| **admin** | `/app` | `/app`, `/settings`, `/billing`, `/dashboard` | User Management, RBAC Matrix, Fiscal Settings | Tenant / Multi-Branch | Platform SuperAdmin Controls |
| **company_admin** | `/app` | `/app`, `/settings`, `/reports` | Company-wide Governance, Auditing | Multi-Branch Company | Platform SuperAdmin Controls |
| **branch_manager**| `/branch`| `/branch`, `/pos`, `/inventory`, `/reports` | Branch Sales, Shifts, Restock Requisitions | Assigned Branch Only | Other Branch Books, Tenant Settings |
| **pharmacist** | `/pharmacy`| `/pharmacy`, `/prescriptions`, `/inventory` | Clinical Queue, Narcotics, Dispensing | Authorized Branch | Accounting, GL, Platform Admin |
| **cashier** | `/pos` | `/pos`, `/sales` | Fast POS Terminal, Cash Float, Sales Receipts | Assigned POS Register | Clinical Dispense, Inventory Adjustments, GL |
| **inventory_manager**| `/inventory`| `/inventory`, `/purchasing` | Stock Batches, Transfers, GRN, Counts | Assigned Warehouse(s) | Prescriptions Dispensing, GL Journals |
| **accountant** | `/accounting`| `/accounting`, `/reports`, `/billing` | General Ledger, AR, AP, Bank Reconciliation | Company Financials | Clinical Prescriptions, POS Register Control |
| **purchasing_officer**| `/purchasing`| `/purchasing`, `/inventory` | Purchase Orders, 3-Way Match, Suppliers | Supply Chain Scope | Clinical Dispensing, GL Journal Posting |
| **sales_supervisor** | `/sales` | `/sales`, `/pos`, `/reports` | Tax Invoices, Discount Caps, Return Approvals | Sales / Branches | System Settings, Drug Formulations |
| **customer_service** | `/ecommerce`| `/ecommerce`, `/sales` | Digital Orders, Courier Tracking, Patient Rx | E-Commerce Scope | Clinical Sign-off, Financial Ledgers |
