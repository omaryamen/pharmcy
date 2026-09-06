# PharmaCloud ERP — Role-Based Access Control (RBAC) & Security Audit

## 1. Multi-Tenant Boundary Isolation
- **Tenant Scope Enforcement**: Verified across all 35+ backend apps; queries automatically filter by `tenant_id`.
- **Branch Data Scoping**: Cashier and POS operations are restricted to the user's active branch assignment.

## 2. Role-Level Capabilities & Safeguards
- **Pharmacist Role**: Authorized for clinical review, prescription approval, controlled drug dispensing, and inventory queries. Cannot modify general ledger accounts or manage platform subscription billing.
- **Cashier Role**: Restricted to POS dispensing and retail returns within their branch register. Cannot approve controlled narcotics prescriptions or reverse supplier invoices.
- **Accountant Role**: Authorized for journal entries, trial balance, AR/AP statements, and financial reports. Cannot dispense prescription medicines directly.
- **Superadmin Role**: Full platform observability, health checks, and tenant impersonation with immutable audit log recording.

## 3. Recommendations
1. Implement granular UI action disables with tooltip explanations (e.g. "Action requires Pharmacist license") when viewing restricted buttons as a lower-privilege role.
