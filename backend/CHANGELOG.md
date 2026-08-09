# Changelog — PharmaCloud ERP Backend

All notable changes to the PharmaCloud ERP Backend project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.12.0] - 2026-08-09

### Added - Enterprise Stock Movement Engine (`apps.stock_movement` / `IMP-017`)
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
