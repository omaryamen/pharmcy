# Changelog — PharmaCloud ERP Backend

All notable changes to the PharmaCloud ERP Backend project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
