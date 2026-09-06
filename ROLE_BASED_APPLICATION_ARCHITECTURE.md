# PharmaCloud ERP — Role-Based Application Architecture & Protected Frontend Shells (الهيكل المعماري لفصل واجهات المستخدم حسب الأدوار)

## 1. Unified Backend, Multiple Protected Frontend Shells
PharmaCloud maintains a single unified Django REST backend, unified PostgreSQL database, and authoritative multi-tenant RBAC engine, while offering dedicated protected frontend application shells tailored to operational roles.

```
                               ┌───────────────────────────┐
                               │   Unified Auth & Login    │
                               │        (/login)           │
                               └─────────────┬─────────────┘
                                             │
      ┌──────────────┬───────────────┬───────┴───────┬──────────────┬──────────────┐
      ▼              ▼               ▼               ▼              ▼              ▼
[ /admin ]       [ /app ]      [ /pharmacy ]      [ /pos ]     [ /inventory ]  [ /accounting ]
Platform       Pharmacy Admin    Licensed       High-Speed     Warehouse &     Financial
SuperAdmin      & Management    Pharmacist       Cashier         Stock          Accountant
```

---

## 2. Dedicated Application Shell Directory

| Protected Shell Path | Target User Role | Visual Identity | Primary Operational Navigation |
|---|---|---|---|
| **`/admin`** | Platform SuperAdmin | Purple Badge (`SA`) | Overview KPIs, Tenants, Subscriptions, Plans, Flags, Health, Maintenance, Audit. |
| **`/app`** | Pharmacy Admin / Company Admin | Emerald Badge (`PC`) | Management Portal, Staff RBAC Matrix, Branches, Invoicing, Settings. |
| **`/pharmacy`** | Licensed Pharmacist | Emerald Stethoscope Badge | Clinical Review, Prescription Queue, Dispensing, Medicine Catalog, FEFO Inventory. |
| **`/pos`** | POS Cashier | Emerald Register Badge | POS Fast Scanning, Cart, Cash Drawer Floats, Sales Receipts, Customer Returns. |
| **`/inventory`**| Warehouse Manager | Blue Stock Badge | Double-Entry Stock, Batches, Shelf Expiry, Transfers, GRN Receiving, Counts. |
| **`/accounting`**| Financial Accountant | Amber Ledger Badge | General Ledger, Automated Journals, AP, AR, Cash & Bank Reconciliation. |
| **`/branch`** | Branch Manager | Indigo Branch Badge | Branch Sales, Cash Registers Oversight, On-Duty Staff Supervision. |

---

## 3. Automatic Login Routing Matrix
Following successful authentication on `/login`, users are automatically redirected to their authoritative workspace shell:
- `superadmin` ➔ `/admin`
- `pharmacy_admin` / `company_admin` ➔ `/app`
- `pharmacist` ➔ `/pharmacy`
- `cashier` ➔ `/pos`
- `inventory_manager` ➔ `/inventory`
- `accountant` ➔ `/accounting`
- `branch_manager` ➔ `/branch`
