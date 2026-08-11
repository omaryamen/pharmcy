# PharmaCloud ERP — Project Status & Roadmap

**Last Updated:** 2026-08-11  
**System Status:** Operational / Healthy  
**Automated Test Pass Rate:** 100% (491 / 491 passed)  
**Backend Framework:** Django 5.2 (Python 3.10+)  
**Frontend Framework:** Next.js (Pending Phase)  

---

## 1. Module Implementation Matrix

| Code | Module Name | Status | Backend | DB Schema | Test Coverage |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **P001 / DASH** | Dashboard | Unstarted | 0% | 0% | - |
| **P002 / MED** | Enterprise Medicine Master Catalog | **Completed** | 100% | 100% | 100% |
| **P002 / REF** | Enterprise Pharmaceutical Reference Data Engine | **Completed** | 100% | 100% | 100% |
| **P003 / INV** | Enterprise Inventory & Batch Management | **Completed** | 100% | 100% | 100% |
| **P003 / STK** | Enterprise Stock Movement Engine | **Completed** | 100% | 100% | 100% |
| **P003 / ADJ** | Enterprise Stock Adjustment & Stock Count | **Completed** | 100% | 100% | 100% |
| **P003 / TRF** | Enterprise Inter-Branch & Warehouse Stock Transfer | **Completed** | 100% | 100% | 100% |
| **P003 / ALT** | Enterprise Expiry, Recall & Inventory Alert Management | **Completed** | 100% | 100% | 100% |
| **P004 / POS** | Enterprise POS & Sales Management | **Completed** | 100% | 100% | 100% |
| **P005 / SAL** | Sales Management | **Completed** | 100% | 100% | 100% |
| **P005 / RET** | Enterprise Customer Sales Returns & Refund Management | **Completed** | 100% | 100% | 100% |
| **P006 / PUR** | Enterprise Purchasing & Purchase Order Management | **Completed** | 100% | 100% | 100% |
| **P006 / REC** | Enterprise Goods Receipt & Receiving Management | **Completed** | 100% | 100% | 100% |
| **P006 / RET** | Enterprise Purchase Returns & Supplier Returns | **Completed** | 100% | 100% | 100% |
| **P007 / SUP** | Enterprise Supplier Management | **Completed** | 100% | 100% | 100% |
| **P008 / CUS** | Enterprise Customer Management | **Completed** | 100% | 100% | 100% |
| **P009 / RX** | Prescriptions | Unstarted | 0% | 0% | - |
| **P010 / ACC** | Enterprise Supplier Invoices & Accounts Payable Foundation | **Completed** | 100% | 100% | 100% |
| **P011 / RPT** | Reports | Unstarted | 0% | 0% | - |
| **P012 / BR** | Branch Management | **Completed** | 100% | 100% | 100% |
| **P012 / COM** | Company Management | **Completed** | 100% | 100% | 100% |
| **P013 / USR** | Enterprise User Management | **Completed** | 100% | 100% | 100% |
| **P014 / ROL** | Roles & Permissions (RBAC) | **Completed** | 100% | 100% | 100% |
| **P015 / NOT** | Notifications | Unstarted | 0% | 0% | - |
| **P016 / SUB** | Subscriptions & Billing | **Completed (Core)** | 100% | 100% | 100% |
| **P017 / TEN** | Tenant Management | **Completed** | 100% | 100% | 100% |
| **P018 / MKT** | Marketplace Readiness | Unstarted | 0% | 0% | - |
| **P019 / AI** | AI Readiness | Unstarted | 0% | 0% | - |
| **P020 / CMP** | Compliance & Market Packs | Unstarted | 0% | 0% | - |
| **P021 / SET** | Settings & Configuration | **Completed (Core)** | 100% | 100% | 100% |
| **P022 / AUD** | Audit Log | Partial | 50% | 50% | 100% |

---

## 2. Completed Foundation Modules

### Core Platform Infrastructure
- **Base Models**: UUID Primary Keys (`UUIDBase`), Audit stamps (`FullAuditModel`), Timestamps (`TimeStampedBase`), Soft Delete (`SoftDeleteBase`, `SoftDeleteManager`).
- **Response Envelope**: [`ApiRenderer`](file:///f:/wateen%20proj/pharmcy/backend/apps/common/api/renderers.py) standardizing `{success, status_code, message, data, errors, meta}` for all JSON API responses.
- **Error Normalization**: Central [`api_exception_handler`](file:///f:/wateen%20proj/pharmcy/backend/apps/common/api/exceptions.py) mapping domain exceptions into standardized error lists.
- **Request Context & Isolation Middleware**: [`RequestContextMiddleware`](file:///f:/wateen%20proj/pharmcy/backend/apps/common/middleware/request_context.py), [`TenantIdentificationMiddleware`](file:///f:/wateen%20proj/pharmcy/backend/apps/common/middleware/tenant.py) supporting HTTP headers (`X-Tenant-ID`, `X-Tenant-Slug`) and Host subdomains (`<slug>.pharmacloud.local`).

### User Identity & Authentication (`apps.authentication` / `P013`)
- JWT authentication with token rotation, refresh blacklisting, and session tracking.

### Dynamic RBAC Engine (`apps.rbac` / `P014`)
- Evaluation Engine with Redis caching layer, DAG hierarchy resolver, user overrides, role versioning audit, and escalation protection.

### Tenant Management (`apps.tenants` / `P017`)
- Lifecycle Operations, Tenant Profiles, Tenant Settings, Tenant Subscriptions, Tenant Subdomains, Provisioning Engine, and REST APIs under `/api/v1/tenants/`.

### Company Management (`apps.companies` / `P012` / `IMP-008`)
- Legal business entities (`Company`), operational parameters (`CompanySettings`), lifecycle status management, and REST APIs under `/api/v1/companies/`.

### Branch Management (`apps.branches` / `P012-BR` / `IMP-009`)
- Physical pharmacy & warehouse branch locations (`Branch`), operational settings (`BranchSettings`), manager assignment, company transfer, and REST APIs under `/api/v1/branches/`.

### Enterprise User Management (`apps.users` / `P013-USR` / `IMP-010`)
- HR & employment profiles (`EmployeeProfile`), multi-branch assignment, role assignment, account locking/unlocking, password resets, and REST APIs under `/api/v1/users/`.

### Enterprise Medicine Master Catalog (`apps.medicines` / `P002-MED` / `IMP-011`)
- Master pharmaceutical catalog (`Medicine`) with classifications, clinical safety flags, barcode/SKU lookups, search engine, reference FK integration, bulk import/export, and REST APIs under `/api/v1/medicines/`.

### Enterprise Pharmaceutical Reference Data Engine (`apps.references` / `P002-REF` / `IMP-012`)
- **Platform-Wide Master Reference Engine**: Normalized reference catalogs for `MedicineCategory` (hierarchical tree), `Manufacturer`, `DosageForm`, `StrengthUnit`, `UnitOfMeasure` (UOM), `PackageType`, `RouteOfAdministration`, `AtcClassification` (WHO 5-level hierarchy), `StorageCondition`, `TaxCategory`.

### Enterprise Supplier Management (`apps.suppliers` / `P007-SUP` / `IMP-013`)
- **Supplier Profile & Domain**: `Supplier` model (`UUIDBase`, `FullAuditModel`, `TenantAwareModel`) supporting code, legal name, display name, supplier type, category, registration number, tax number, VAT number, and status (`active`, `inactive`, `suspended`, `blacklisted`, `archived`).
- **Contact, Geolocation & Financial Data**: Primary/secondary contacts, multi-channel phone/WhatsApp/mobile/email, physical address & geolocation (lat/long, Google Maps link), financial parameters (currency, payment terms, credit limit, balances, bank account, IBAN, SWIFT, tax category).
- **Licensing & Compliance Rating**: Commercial registration, drug license, license expiry dates, insurance info, preferred supplier flag, blacklisted flag, 5-star rating, and risk level (`low`, `medium`, `high`, `critical`).

### Enterprise Customer Management (`apps.customers` / `IMP-014`)
- **Customer Profile & Domain**: `Customer` model supporting code, legal name, trade name, customer type (`individual`, `pharmacy`, `hospital`, `clinic`, `wholesaler`, `distributor`, `government`, `other`), status lifecycle, taxonomy categories, and risk ratings.

### Enterprise Warehouse & Storage Location Management (`apps.warehouses` / `IMP-015`)
- **Warehouse Entity & Domain**: `Warehouse` entity supporting code, name, names in Arabic/English, types (`main`, `pharmacy`, `branch`, `distribution_center`, `cold_storage`, `controlled_drug`, `quarantine`, `returns`, `damaged`, `transit`, `virtual`, `other`), status lifecycle (`draft`, `active`, `inactive`, `suspended`, `temporarily_closed`, `archived`), tenant, company, optional branch link, manager assignment validation, contact info, geolocation, working hours, and default storage role flags.
- **Hierarchical Storage Location Engine**: `StorageLocation` supporting recursive depth (Warehouse → Zone → Aisle → Rack → Shelf → Bin / Cabinet / Freezer / Room), status lifecycle (`active`, `inactive`, `maintenance`, `blocked`, `full`), capacity & current utilization foundation, environmental control parameters (temperature range, humidity range), and storage conditions.

### Enterprise Inventory & Batch Management (`apps.inventory` / `IMP-016`)
- **Pharmaceutical Batch Engine**: `Batch` entity (`FullAuditModel`, `TenantAwareModel`) supporting batch number, lot number, manufacturing date, expiry date, registration number, country of origin, unit cost, selling price, storage requirements, and compliance status (`active`, `quarantine`, `expired`, `recalled`, `blocked`, `depleted`, `archived`).
- **Stock Position Balance Engine**: `InventoryItem` representing stock position of a medicine batch at a storage location within a warehouse. Enforces Decimal precision, non-negative quantity check constraints, available quantity calculation (`on_hand - reserved - damaged - quarantine`), unit cost, average cost (weighted average calculation), and last cost tracking.

### Enterprise Stock Movement Engine (`apps.stock_movement` / `IMP-017`)
- **Authoritative Stock Movement Engine**: `StockMovementEngine` executing double-entry inventory quantity modifications atomically inside `@transaction.atomic` blocks with `select_for_update()` pessimistic DB row locking.
- **Movement Types & Statuses**: Complete support for `OPENING_BALANCE`, `RECEIPT`, `ISSUE`, `SALE`, `SALE_RETURN`, `PURCHASE_RETURN`, `TRANSFER_OUT`, `TRANSFER_IN`, `ADJUSTMENT_IN`, `ADJUSTMENT_OUT`, `DAMAGE`, `EXPIRY`, `QUARANTINE`, `QUARANTINE_RELEASE`, `RESERVATION`, `RESERVATION_RELEASE`, `CORRECTION`, `RECALL`, `OTHER`.
- **Reversal Engine**: `reverse_movement(...)` creating compensating reversal movements, reversing line quantities, and preventing duplicate reversals.
- **FEFO Batch Allocation & Idempotency**: Automatic FEFO batch selection for outgoing issues/sales when unspecified, and tenant-scoped `idempotency_key` duplicate protection.
- **Sequence Generator**: Collision-safe document sequence code generator (`STK-2026-XXXXXX`, `TRF-2026-XXXXXX`, `REC-2026-XXXXXX`, `ISS-2026-XXXXXX`).
- **REST APIs**: Published endpoints under `/api/v1/stock-movements/` for CRUD, status processing (`/process/`, `/cancel/`, `/reverse/`), operational shortcuts (`/receive/`, `/issue/`, `/transfer/`), traceability reporting (`/traceability/`), and movement stats (`/stats/`).

### Enterprise Stock Adjustment & Stock Count (`apps.stock_adjustment` / `IMP-018`)
- **Stock Count Lifecycle Engine**: `StockCountService` managing the complete physical audit lifecycle: `DRAFT` → `IN_PROGRESS` → `SUBMITTED` → `APPROVED` → `RECONCILED` (or `RECOUNT_REQUIRED` / `CANCELLED` / `REJECTED`).
- **Blind Count Security & Masking**: Physical counters are prohibited from seeing system snapshot quantities or calculated variances during count entry when `is_blind_count=True`. Masked dynamically at the serializer layer.
- **Atomic Stock Movement Reconciliation**: Reconciliation triggers `StockMovementEngine` to generate authoritative double-entry inventory movements (`ADJUSTMENT_IN` for overages, `ADJUSTMENT_OUT` for shortages) with row locking and idempotency protection.
- **Multi-Counter Counting Sessions & Line Recounts**: `StockCountSession` and `StockCountRecount` models to track sub-team count assignments and line-level recount workflows.
- **REST APIs & Document Numbering**: Full REST endpoints under `/api/v1/stock-counts/` with sequential document number generation (`CNT-YYYY-XXXXXX`, `SES-YYYY-XXXXXX`, `REC-YYYY-XXXXXX`).

### Enterprise Inter-Branch & Warehouse Stock Transfer (`apps.stock_transfer` / `IMP-019`)
- **Stock Transfer Workflow Engine**: `StockTransferService` managing the complete transfer lifecycle: `DRAFT` → `REQUESTED` → `APPROVED` → `PICKING` → `READY_FOR_DISPATCH` → `DISPATCHED` / `IN_TRANSIT` → `RECEIVED` / `PARTIALLY_RECEIVED` / `DISCREPANCY` → `CLOSED`.
- **FEFO-Aware Picking**: Automatic FEFO batch selection for outgoing lines without specified batches, enforcing valid non-expired, non-recalled, non-quarantined stock selection.
- **Atomic Double-Entry Dispatch & Receiving**: Stock movement orchestration via `StockMovementEngine` using `TRANSFER_OUT` and `TRANSFER_IN` with zero direct inventory balance mutations.
- **Discrepancies & Damage Tracking**: Automatic `StockTransferDiscrepancy` generation for quantity shortages, overages, damaged goods during transport (`DAMAGE` movements), wrong batch, and wrong medicine delivery.
- **Compensating Reversals & Separation of Duties**: Reversal workflow creating compensating double-entry movements, preventing double reversal. Approval checks enforce separation of duties between requesters and approvers.
- **REST APIs & Sequential Numbering**: REST endpoints under `/api/v1/stock-transfers/` with sequential document code generation (`TRF-YYYY-XXXXXX`, `DISC-YYYY-XXXXXX`).

### Enterprise Expiry, Recall & Inventory Alert Management (`apps.alerts` / `IMP-020`)
- **Alert Scanner Engine**: `AlertScannerService` scanning active inventory balances and pharmaceutical batch expiry dates, generating/updating real-time `InventoryAlert` records for low stock, out of stock, near expiry (30/60/90 days), and expired stock.
- **Batch Recall & Auto-Quarantine Engine**: `BatchRecallService` managing formal pharmaceutical recall orders (`RCL-YYYY-XXXXXX`), setting batch status to `RECALLED`, and executing automated stock quarantining across all warehouses via `StockMovementEngine` (`QUARANTINE` movement type).
- **Acknowledgment & Resolution Lifecycle**: Full lifecycle tracking (`ACTIVE` → `ACKNOWLEDGED` → `RESOLVED` / `DISMISSED`) with user accountability and resolution notes.
- **REST APIs & Sequential Numbering**: Published endpoints under `/api/v1/alerts/` and `/api/v1/recalls/` with sequential document code generation (`ALT-YYYY-XXXXXX`, `RCL-YYYY-XXXXXX`).

### Enterprise Purchasing & Purchase Order Management (`apps.procurement` / `IMP-021`)
- **Purchase Requisition Engine**: `PurchaseRequisition` header & lines (`PR-YYYY-XXXXXX`) managing internal purchase requests (`DRAFT` → `SUBMITTED` → `APPROVED` / `REJECTED`).
- **Purchase Order Engine**: `PurchaseOrder` header & lines (`PO-YYYY-XXXXXX`) for supplier commitments (`DRAFT` → `PENDING_APPROVAL` → `APPROVED` → `SENT_TO_SUPPLIER` → `ACKNOWLEDGED` → `PARTIALLY_RECEIVED` → `FULLY_RECEIVED` → `CLOSED`). Zero direct inventory mutation.
- **Requisition to PO Conversion**: Service converting approved requisitions into POs grouped by preferred supplier with row locking idempotency.
- **Controlled Amendments & Separation of Duties**: `PurchaseOrderAmendment` audit trail for approved order modifications. Enforces creator != approver separation of duties.
- **REST APIs & Sequential Numbering**: Published endpoints under `/api/v1/purchase-requisitions/`, `/api/v1/purchase-orders/`, `/api/v1/supplier-prices/`.

### Enterprise Goods Receipt & Receiving Management (`apps.goods_receipt` / `IMP-022`)
- **Physical Goods Receiving Engine**: `GoodsReceipt` header & lines (`GRN-YYYY-XXXXXX`) receiving stock against Purchase Orders or standalone supplier deliveries (`DRAFT` → `RECEIVING` → `PENDING_VERIFICATION` → `COMPLETED`).
- **Batch Management & Expiry Validation**: Automatic `Batch` creation/reuse with expiry date validation, recall status checks, and cold chain temperature excursion tracking.
- **Authoritative Stock Movement Posting Engine**: `post_goods_receipt` executing physical inventory balance additions strictly via `StockMovementEngine` (`RECEIPT` / `QUARANTINE` / `DAMAGE`) with zero direct quantity mutations.
- **PO Quantity Reconciliation & Reversals**: Updates PO lines (`received_quantity`, `free_quantity_received`) and PO status (`PARTIALLY_RECEIVED`, `FULLY_RECEIVED`). `reverse_goods_receipt` executing compensating stock movements and restoring PO quantities.
- **REST APIs & Sequential Numbering**: Published endpoints under `/api/v1/goods-receipts/` (`/post/`, `/reverse/`, `/statistics/`).

### Enterprise Purchase Returns & Supplier Returns (`apps.purchase_returns` / `IMP-023`)
- **Supplier Returns Engine**: `PurchaseReturn` header & lines (`PRT-YYYY-XXXXXX`) returning stock against Goods Receipts and Purchase Orders (`DRAFT` → `REQUESTED` → `APPROVED` → `DISPATCHED` → `ACCEPTED` / `DISCREPANCY`).
- **Stock Movement Integration**: `dispatch_purchase_return` executing physical stock removals strictly through `StockMovementEngine` (`PURCHASE_RETURN`) with zero direct quantity mutations and stock level checks.
- **Supplier Acceptance & Discrepancies**: `record_supplier_acceptance` logging supplier accepted/rejected quantities, automatically creating `ReturnDiscrepancy` (`DISC-YYYY-XXXXXX`) for shortages and `SupplierCreditNote` (`CRN-YYYY-XXXXXX`) for accepted value.
- **Reversal Engine & Separation of Duties**: Reversal workflow executing compensating receipt movements. Approval checks enforce separation of duties.
- **REST APIs & Sequential Numbering**: Published endpoints under `/api/v1/purchase-returns/` (`/dispatch/`, `/supplier-acceptance/`, `/reverse/`, `/statistics/`).

### Enterprise Supplier Invoices & Accounts Payable Foundation (`apps.accounts_payable` / `IMP-024`)
- **Vendor Bill & Invoice Engine**: `SupplierInvoice` header & lines (`INV-YYYY-XXXXXX`) for vendor bills (`DRAFT` → `VERIFIED` → `APPROVED` → `POSTED` → `PARTIALLY_PAID` → `PAID`).
- **Three-Way Matching Engine**: Line-by-line verification across PO, Goods Receipt, and Invoice detecting `MATCHED`, `QUANTITY_VARIANCE`, `PRICE_VARIANCE`, `RECEIPT_MISSING`, `SUPPLIER_MISMATCH`.
- **AP Subledger & Duplicate Detection**: `AccountsPayableEntry` (`AP-YYYY-XXXXXX`) tracking outstanding vendor liabilities. Duplicate bill detection by `(tenant, supplier, supplier_invoice_number)`.
- **Supplier Payments & Credit Notes Integration**: `SupplierPayment` (`PAY-YYYY-XXXXXX`) and `CreditApplication` applying `SupplierCreditNote` (from IMP-023) against open payables. Supports partial payments, full payments, overpayment prevention, and payment reversals.
- **AP Aging & Supplier Balance Analytics**: Calculates AP aging buckets (Current, 1-30, 31-60, 61-90, 90+ days) and net supplier balance summary.
- **REST APIs & Sequential Numbering**: Published endpoints under `/api/v1/supplier-invoices/`, `/api/v1/supplier-payments/`, `/api/v1/accounts-payable/` (`/verify/`, `/post/`, `/apply-credit/`, `/aging/`, `/statistics/`).

### Enterprise POS & Sales Management (`apps.sales` / `IMP-025`)
- **POS Retail Counter & Cart Engine**: `SalesInvoice` and `SalesInvoiceLine` (`INV-YYYY-XXXXXX`) for retail sales (`DRAFT` -> `HELD` -> `COMPLETED` -> `VOIDED`).
- **FEFO Batch Allocation**: `FEFOBatchSelector` automatically selects earliest expiring non-expired, non-recalled, non-quarantined medicine batch.
- **Authoritative Stock Reduction**: Completing a sale reduces inventory strictly through `StockMovementEngine` (`SALE` movement type) with zero direct quantity mutations and row locking.
- **Payments, Change & Customer Credit**: `SalesPayment` (`PAY-YYYY-XXXXXX`) supporting cash, card, mobile wallet, split payments, cash change calculation, and customer credit sales with credit limit enforcement.
- **Void Workflow & Stock Restoration**: `void_completed_sale` creates compensating `SALE_RETURN` movements via `StockMovementEngine` and restores customer credit balance.
- **Cash Registers & Shift Sessions**: `CashRegister` (`REG-YYYY-XXXXXX`) and `RegisterSession` (`SES-YYYY-XXXXXX`) for managing cashier shift sessions and till cash reconciliation (expected cash vs actual count variance).
- **REST APIs & Barcode Search**: Endpoints under `/api/v1/sales/`, `/api/v1/pos/`, `/api/v1/cash-registers/`, `/api/v1/register-sessions/` (`/complete/`, `/void/`, `/lookup/barcode/`, `/analytics/`).

### Enterprise Customer Sales Returns & Refund Management (`apps.sales_returns` / `IMP-026`)
- **Customer Returns Engine**: `CustomerReturn` header & lines (`CRT-YYYY-XXXXXX`) managing customer sales returns against `SalesInvoice` (`DRAFT` → `REQUESTED` → `APPROVED` → `INSPECTION` → `ACCEPTED` / `PARTIALLY_ACCEPTED` / `REJECTED`).
- **Return Eligibility & Quantity Validation**: Line-by-line validation enforcing `requested_quantity <= original_sold - previously_returned`.
- **Quality Inspection & Stock Restoration**: Quality inspection logging accepted vs rejected quantities per line. Stock restoration executed strictly via `StockMovementEngine` (`SALE_RETURN` for sealed stock, `QUARANTINE` for damaged/opened stock) with zero direct quantity mutations.
- **Refund Disbursements & Store Credit**: `CustomerRefund` (`REF-YYYY-XXXXXX`) supporting cash, card, bank transfer, and store credit refunds (reducing customer balance liability).
- **Return Reversals & Separation of Duties**: Reversal workflow executing compensating `SALE` movements via `StockMovementEngine` and reversing customer store credit. Approval enforces creator != approver separation of duties.
- **REST APIs & Return Analytics**: Endpoints published under `/api/v1/customer-returns/` and `/api/v1/customer-refunds/` (`/approve/`, `/inspect/`, `/process-refund/`, `/reverse/`, `/statistics/`).

---

## 3. Next Recommended Module

**Module Code:** `IMP-027` — **Enterprise Prescription Management & Pharmacy Dispensing** (`apps.prescriptions`)

---

## 4. Test Verification Log

```bash


