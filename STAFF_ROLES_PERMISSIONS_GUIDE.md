# PharmaCloud ERP — Enterprise Staff, Roles & Permissions Guide (دليل أدوار وصلاحيات طاقم الصيدلية)

## 1. Role Hierarchy & Data Scopes

PharmaCloud enforces strict multi-level role-based access control (RBAC) and data scope isolation:

```
┌─────────────────────────────────────────────────────────────┐
│                      Tenant Scope                           │
│       (Pharmacy Owner / Tenant Admin: All branches)         │
└──────────────────────────────┬──────────────────────────────┘
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
       [ Company Scope ]               [ Branch Scope ]
        Company Admin                   Branch Manager
                                        Licensed Pharmacist
                                        POS Cashier
                                        Inventory Keeper
```

---

## 2. Predefined Staff Roles

| Role Code | Role Name (AR / EN) | Primary Scope | Responsibilities & Capabilities | Prohibited Areas |
|---|---|---|---|---|
| `admin` | مدير الصيدلية والمالك (Pharmacy Admin) | Tenant-wide | Full operational control, staff provisioning, legal profile, rules. | Cannot access over-tenant SaaS platform operations. |
| `company_admin` | مدير الشركة (Company Admin) | Company-wide | Company branches, company staff, consolidated sales & inventory. | Isolated to owned company. |
| `branch_manager` | مدير الفرع (Branch Manager) | Assigned Branch | POS supervision, cash sessions, branch stock, staff attendance. | Cannot modify other branches. |
| `pharmacist` | صيدلي مرخص (Pharmacist) | Assigned Branch | Prescriptions queue, clinical dispensing, narcotics tracking, POS. | No access to GL, AP, AR accounting or system settings. |
| `cashier` | أمين الصندوق (Cashier) | Assigned Register | POS checkout, cash drawer floats, customer sales receipts, returns. | No access to prescriptions, GL, or inventory adjustments. |
| `inventory_manager`| أمين المستودع (Inventory) | Warehouse/Branch | Stock receipts (GRN), FEFO batch tracking, transfers, adjustments. | No access to accounting or prescription signing. |
| `accountant` | محاسب مالي (Accountant) | Company/Tenant | General Ledger, AP, AR, bank reconciliation, financial reports. | No clinical or dispensing capabilities. |
| `purchasing_officer`| مسؤول المشتريات (Purchasing)| Tenant/Company | Supplier purchase orders, quotations, price negotiations. | No GL journal posting. |
| `sales_supervisor`| مشرف المبيعات (Sales Supervisor)| Branch/Company | Sales oversight, POS discount approvals, customer accounts. | No financial journal adjustments. |
| `customer_service`| خدمة العملاء (Customer Service)| Tenant-wide | Patient inquiries, order tracking, profile management. | No dispensing or inventory write-offs. |

---

## 3. Dynamic Sidebar Navigation Filtering
The frontend sidebar automatically filters available modules based on the active role while backend authorization authoritatively prevents unauthorized REST API requests (IDOR / privilege escalation protection).
