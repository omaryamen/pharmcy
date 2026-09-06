# PharmaCloud ERP — Role-Permission Matrix (مصفوفة الصلاحيات والأدوار)

The following matrix documents the authoritative granular permissions allocated across operational pharmacy roles.

| Module / Action Code | Description | Admin | Branch Manager | Pharmacist | Cashier | Inventory | Accountant |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `pos.manage` | POS Terminal & Dispensing |  |  |  |  |  |  |
| `prescriptions.approve` | Prescription Review & Signature |  |  |  |  |  |  |
| `prescriptions.controlled` | Controlled Narcotics Dispensing |  |  |  |  |  |  |
| `inventory.stock.manage` | Stock Adjustments & Counts |  |  |  |  |  |  |
| `purchasing.po.create` | Supplier Purchase Orders |  |  |  |  |  |  |
| `ap.invoice.pay` | Accounts Payable & Payments |  |  |  |  |  |  |
| `ar.invoice.collect` | Accounts Receivable & Claims |  |  |  |  |  |  |
| `gl.journal.post` | General Ledger Journal Posting |  |  |  |  |  |  |
| `cash.session.manage` | Cash Drawer Shift Floats |  |  |  |  |  |  |
| `rbac.user.manage` | Staff Provisioning & Roles |  |  |  |  |  |  |
| `settings.company.manage` | Legal & Fiscal Settings |  |  |  |  |  |  |

**Legend:**
-  = Allowed
-  = Explicitly Denied / Inaccessible
