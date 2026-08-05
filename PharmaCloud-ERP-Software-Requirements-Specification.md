# PharmaCloud ERP — Software Requirements Specification (SRS)

**Document Version:** 1.0  
**Document Status:** Draft for Architecture, API, DB, UI/UX, Frontend, Backend, QA, Security, and DevOps review  
**Standards Applied:** IEEE 29148-2018 · ISO/IEC/IEEE 12207 · ISO/IEC 25010 · OWASP ASVS 4.0 · OpenAPI 3.1 · Cloud-Native Best Practices · REST API Best Practices  
**Prepared For:** Software Architect · Database Architect · API Architect · Frontend Engineering · Backend Engineering · Security Engineering · QA Engineering · DevOps Engineering  
**Authority Hierarchy:** Business Requirements Document (BRD) v1.1 → Software Requirements Specification (SRS) v1.0 → Architecture → Design → Implementation

---

## Document Control

| Item | Detail |
|------|--------|
| Project | PharmaCloud ERP — Enterprise Multi-Tenant SaaS Pharmacy ERP |
| Version | 1.0 |
| Date | 2026-08-05 |
| Status | Draft for review (SRS phase) |
| Change Authority | Product Council (PM + Architecture + Business Analysis + Security/Compliance) |
| Review Cycle | On material scope change; re-baseline at Architecture Review Gate |
| Source of Truth | BRD v1.1 (Approved, 2026-08-05) — `PharmaCloud-ERP-Business-Analysis-Package.md` |
| Related Artefacts | PRD (in progress — see Open Issues OI-01), SRS, Architecture, REST API Contract (OpenAPI 3.1), Logical Data Model, BPMN Process Diagrams, Test Strategy |

---

## Version History

| Version | Date | Author | Change Description |
|---------|------|--------|---------------------|
| 1.0 | 2026-08-05 | Requirements Engineering | Initial baseline from BRD v1.1. All 22 product modules specified; 160+ functional requirements; NFRs, external interfaces, API, security, multi-tenant, database-logical, compliance, and traceability sections. |

---

## Executive Summary

PharmaCloud ERP is an enterprise, cloud-native, **multi-tenant SaaS pharmacy ERP platform** serving independent pharmacies, pharmacy chains, and (later) medical warehouses/distributors across **Yemen and the GCC** (KSA, UAE, Qatar, Kuwait, Bahrain, Oman), with Arabic (RTL) and English as the initial languages. The platform replaces fragmented cash-register, spreadsheet, paper-ledger, and manual-prescription operations with one integrated operating system covering point-of-sale (POS), prescription management, inventory with batch/expiry control, purchasing, supplier management, accounting, branch management, and reporting.

This SRS translates the approved BRD v1.1 into **implementation-ready software requirements** for architecture, database, API, frontend, backend, security, QA, and DevOps engineering. It preserves every BRD commitment:

- **One country-neutral core with plugin-based market packs** (taxation, e-invoicing, currency, language, calendar, drug reference, Rx mode, health-authority reporting) — no country-specific core code (BR-LOC-01, FR-LOC-01).
- **Automatic safety-rule enforcement** — expiry-before-sale, batch traceability, controlled-substance registers, prescription validity, negative-stock prevention (BR-STK, BR-CTL, BR-RX).
- **Multi-branch, multi-tenant architecture** — branch-level transaction attribution, inter-branch transfers, central policy push, tenant data isolation (BR-BRANCH, BR-TEN).
- **Accounting and tax** — balanced double-entry posting, day-close reconciliation, pluggable tax engines, ZATCA e-invoicing adapter readiness (BR-ACC, BR-TAX).
- **AI-ready and marketplace-ready foundations** — append-only/analytics-ready data model, feature-flagged capability rollout, partner API/sandbox (FR-AI, FR-MKT).

**Key binding commitments (carried from BRD Section 16, NFRs, and Rules):**

- Availability ≥ 99.5% monthly; checkout < 2 s; stock/branch queries < 2 s at 100k stock lines; day-close < 10 s (NFR-N-01/02).
- ≥ 1,500 concurrent terminals per region with no degradation > 10% at target scale (NFR-N-03).
- 100% of BR rules enforced in production code; 100% mandated audit events captured (KPI-12/13).
- Active sale survives a 30 s connectivity loss without data loss (NFR-N-08).
- RPO ≤ 24 h, RTO ≤ 4 h business time, restores tested quarterly (NFR-N-12).
- Arabic (RTL) and English fully supported from MVP; additional languages via market packs (NFR-N-11/17).

**Scope of this SRS:** functional requirements for 22 product modules (dashboard, medicines, inventory, POS, sales, purchasing, suppliers, customers, prescriptions, accounting, reports, branches, users, roles, notifications, subscriptions, tenant management, marketplace readiness, AI readiness, compliance & market packs, settings, audit log); non-functional requirements across 20 categories; external interface requirements; user-interface requirements; API requirements; security requirements; multi-tenant requirements; logical database requirements; compliance requirements; business-rule mapping; traceability matrix; risks; and future requirements.

**Known gaps / open items (non-blocking):** PRD artefact alignment (OI-01), legal validation of market packs (BRD AS-02), go-live sequencing decisions DEC-08/DEC-09, hosting region DEC-05, payment gateway DEC-06 — all tracked in Appendix B (Open Issues).

---

## Glossary

| Term | Definition |
|------|------------|
| AR | Accounts Receivable — money owed by credit customers to the pharmacy. |
| AP | Accounts Payable — money owed by the pharmacy to suppliers. |
| API | Application Programming Interface — contract through which software components interact. |
| Audit Trail | Immutable, chronological record of create/update/delete/privileged events with user, timestamp, before/after values, and source. |
| Availability | The proportion of time a service is operational and usable (target ≥ 99.5% monthly). |
| Batch / Lot | A quantity of a product produced/received together, tracked with a lot number and expiry date. |
| Barcode | Machine-readable representation of a product identifier (GS1/EAN/UPC or national code). |
| BRD | Business Requirements Document — the approved business requirements package (v1.1). |
| Branch | A single operating location (pharmacy store) that belongs to a tenant. |
| Cash Drawer / Register | The physical till; open/close events are attributed to an operator (shift management). |
| Controlled Substance | A medicine whose dispensing is legally restricted (scheduled) and must be recorded in a register. |
| Day-Close | End-of-day workflow that reconciles expected sales per payment type against declared cash and locks the day. |
| E-Invoice | Electronic invoice per market specification (e.g., ZATCA FATOORAH Phase 2 in KSA). |
| Entitlement | Set of features/limits a tenant may use under its subscription plan. |
| FIFO | First-In First-Out inventory valuation method (tenant default per BR-ACC-04). |
| GRN | Goods Receipt Note — record of accepting supplier delivery against a purchase order. |
| GSI | Global Standard identifiers and barcodes used in healthcare supply chains. |
| Market Pack | Versioned, isolated, pluggable module delivering market-specific behavior (tax, e-invoicing, currency, language, calendar, drug reference, Rx mode, health-authority reporting). |
| MoSCoW | Prioritization method: Must / Should / Could / Won't-have. |
| MRR / ARR | Monthly/Annual Recurring Revenue. |
| Multi-Tenant | One software instance serving many customers (tenants) with logical/isolated data per tenant. |
| NFR | Non-Functional Requirement — quality attribute requirement. |
| NRR | Net Revenue Retention. |
| OTC | Over-the-counter (non-prescription) product. |
| PO | Purchase Order — formal order to a supplier. |
| POS | Point of Sale — checkout terminal function. |
| PRD | Product Requirements Document (referenced; being produced — see OI-01). |
| RBAC | Role-Based Access Control — access granted via roles with module/action/branch scope. |
| Recall | Regulatory or supplier action to quarantine and block affected batches from sale. |
| RPO / RTO | Recovery Point Objective / Recovery Time Objective. |
| RTL | Right-to-Left script rendering (Arabic). |
| Rx | Prescription. |
| SaaS | Software as a Service. |
| SKU | Stock-Keeping Unit — distinct sellable product variant. |
| SLA | Service-Level Agreement. |
| SRS | Software Requirements Specification — this document. |
| Tenant | A contracted customer (pharmacy, chain, warehouse) with an isolated data space. |
| Void | Cancellation of a sale or sale line with reason capture; transaction preserved in audit trail. |
| ZATCA | Zakat, Tax and Customs Authority (KSA) — e-invoicing authority. |

---

## Table of Contents

1. [Introduction](#1-introduction)
   - 1.1 Purpose
   - 1.2 Scope
   - 1.3 Conventions and Requirement ID Scheme
   - 1.4 Intended Audience
   - 1.5 References
2. [Overall Description](#2-overall-description)
   - 2.1 Product Perspective
   - 2.2 Product Functions (Overview)
   - 2.3 User Classes and Characteristics
   - 2.4 Operating Environment
   - 2.5 Design and Implementation Constraints
   - 2.6 Assumptions and Dependencies
3. [Functional Requirements by Module](#3-functional-requirements-by-module)
   - 3.1 MOD-01 Dashboard
   - 3.2 MOD-02 Medicines / Product Master
   - 3.3 MOD-03 Inventory
   - 3.4 MOD-04 Point of Sale (POS)
   - 3.5 MOD-05 Sales Management
   - 3.6 MOD-06 Purchasing
   - 3.7 MOD-07 Suppliers
   - 3.8 MOD-08 Customers
   - 3.9 MOD-09 Prescriptions
   - 3.10 MOD-10 Accounting
   - 3.11 MOD-11 Reports
   - 3.12 MOD-12 Branches
   - 3.13 MOD-13 Users
   - 3.14 MOD-14 Roles & Permissions
   - 3.15 MOD-15 Notifications
   - 3.16 MOD-16 Subscriptions & Billing
   - 3.17 MOD-17 Tenant Management
   - 3.18 MOD-18 Marketplace Readiness
   - 3.19 MOD-19 AI Readiness
   - 3.20 MOD-20 Compliance & Market Packs
   - 3.21 MOD-21 Settings & Configuration
   - 3.22 MOD-22 Audit Log
4. [Non-Functional Requirements](#4-non-functional-requirements)
5. [External Interface Requirements](#5-external-interface-requirements)
6. [User Interface Requirements](#6-user-interface-requirements)
7. [API Requirements](#7-api-requirements)
8. [Security Requirements](#8-security-requirements)
9. [Multi-Tenant Requirements](#9-multi-tenant-requirements)
10. [Database Requirements (Logical)](#10-database-requirements-logical)
11. [Compliance Requirements](#11-compliance-requirements)
12. [Business Rules Mapping](#12-business-rules-mapping)
13. [Traceability Matrix](#13-traceability-matrix)
14. [Risks](#14-risks)
15. [Future Requirements](#15-future-requirements)
16. [Appendices](#16-appendices)
    - 16.1 Validation Checklist
    - 16.2 Open Issues & Decisions
    - 16.3 Recommendations
    - 16.4 Standards and References

---

# 1. Introduction

## 1.1 Purpose

This Software Requirements Specification (SRS) defines the complete set of requirements for the **PharmaCloud ERP** platform. It is the authoritative technical requirements contract between the business and the engineering delivery organization. The SRS is written per IEEE 29148-2018 and is intended to be sufficient for:

- **Software Architecture** — defining the system decomposition, plugin framework, multi-tenant model, and data flows.
- **Database Architecture** — defining logical data requirements, consistency, retention, and archiving.
- **REST API Design** — defining endpoint standards, contracts, versioning, and error semantics.
- **Frontend Development** — defining user interface, localization, and RTL behavior.
- **Backend Development** — defining functional behavior, business-rule enforcement, and workflows.
- **Security Engineering** — defining authentication, authorization, isolation, and privacy controls.
- **QA Engineering** — defining testable acceptance criteria and business-rule testability.
- **DevOps** — defining availability, resilience, observability, backup, and disaster-recovery requirements.

The SRS **does not** prescribe technology choices, database schemas, UI pixel design, or code. Those decisions belong to the Architecture and Design phases. Where the SRS uses a term that implies a technology (e.g., "JWT"), the requirement is a capability/behavioral requirement that may be satisfied by the equivalent mechanism chosen by architecture.

## 1.2 Scope

### 1.2.1 In Scope

This SRS covers the software requirements for the PharmaCloud ERP platform from MVP (Phase 1) through Enterprise, AI, and Marketplace phases as defined in BRD Section 18. All requirements trace to the approved BRD v1.1. The functional scope is organized into 22 product modules:

| # | Module Code | Module | BRD Source |
|---|-------------|--------|------------|
| 01 | DASH | Dashboard | FR-REP-01/02, FR-BR-03, FR-TEN-03, P15 |
| 02 | MED | Medicines / Product Master | FR-INV-01, BR-PRC, BR-TAX-01, FR-LOC-06 |
| 03 | INV | Inventory | FR-INV-02..07, BR-STK-01..07, P05/P07/P08 |
| 04 | POS | Point of Sale | FR-POS-01..07, FR-PH-03..05, P01 |
| 05 | SAL | Sales Management | FR-POS-04/07, FR-REP-01 ext, BR-SAL, BR-CASH |
| 06 | PUR | Purchasing | FR-PUR-01..03, BR-PUR-01..05, P04/P05 |
| 07 | SUP | Suppliers | FR-PUR-03..05, BR-SUP-01..05, P06 |
| 08 | CUS | Customers | FR-CUST-01..03, BR-CUST-01..03, BR-LOY-01, P16 |
| 09 | RX | Prescriptions | FR-RX-01..05, BR-RX-01..06, BR-CTL, P02 |
| 10 | ACC | Accounting | FR-ACC-01..05, BR-ACC-01..04, BR-TAX-01..03, P10 |
| 11 | RPT | Reports | FR-REP-01..04, BR-REP-01/02, P15 |
| 12 | BR | Branches | FR-BR-01..03, BR-BRANCH-01/02, P11 |
| 13 | USR | Users | FR-USR-01..03, BR-SEC-01..04, P14 |
| 14 | ROL | Roles & Permissions | FR-USR-01, BR-SEC-01/02, P14 |
| 15 | NOT | Notifications | FR-SUB-02, FR-TEN-03, P13 |
| 16 | SUB | Subscriptions & Billing | FR-SUB-01..04, BR-SUB-01..06, P13 |
| 17 | TEN | Tenant Management | FR-TEN-01..04, BR-TEN-01..03, P13 |
| 18 | MKT | Marketplace Readiness | FR-MKT-01/02, Roadmap Phase 6 |
| 19 | AI | AI Readiness | FR-AI-01..03, Roadmap Phase 5 |
| 20 | CMP | Compliance & Market Packs | FR-LOC-01/05..07, BR-LOC/PLUG/TAX, P17 |
| 21 | SET | Settings & Configuration | FR-TEN-02, FR-LOC-02..04, BR-LOC/CUR, P17 |
| 22 | AUD | Audit Log | FR-USR-03, BR-AUD-01, BR-SEC-03 |

### 1.2.2 Out of Scope (per BRD Section 8)

- Manufacturing/compounding scheduling and batch production (OOS-01).
- Full ERP back-office: HR/payroll, fixed assets, non-medical procurement (OOS-02).
- Patient-facing portal/mobile app, online ordering, delivery dispatch (OOS-03).
- Telemedicine/e-consultation (OOS-04).
- Insurance/TPA realtime claims adjudication (OOS-05; configurable module V3+).
- Hardware manufacturing/provisioning; software interfaces only (OOS-06).
- Offline-first POS disconnected mode (OOS-07; resilience caching only, NFR-N-08).
- Full clinical EHR (OOS-08).
- Supplier self-service ordering portal (OOS-09; later Marketplace).
- Languages beyond Arabic and English for MVP (OOS-10; plugin framework supports more).
- Per-tenant custom code / white-label core (OOS-11; configuration-over-customization policy).
- Arbitrary multi-geography data residency at MVP (OOS-12; Enterprise phase).

### 1.2.3 In-Scope as Trading/Indirect Parties (not licensed end-users)

Suppliers, wholesalers, credit customers, patients (privacy-scoped records only), and regulatory/tax authorities (via exports/reports only) — per BRD 7.2.

## 1.3 Conventions and Requirement ID Scheme

Every requirement in this SRS has a unique, stable ID and is a testable statement. The ID scheme is:

| Prefix | Meaning | Example |
|--------|---------|---------|
| `REQ-<MOD>-<nnn>` | Functional requirement of a module | REQ-POS-001 |
| `NFR-<CAT>-<nn>` | Non-functional requirement (category) | NFR-PERF-01 |
| `EXT-<IF>-<nn>` | External interface requirement | EXT-PAY-01 |
| `UI-<nn>` | User interface requirement | UI-010 |
| `API-<nn>` | API standard requirement | API-015 |
| `SEC-<nn>` | Security requirement | SEC-008 |
| `MT-<nn>` | Multi-tenant requirement | MT-006 |
| `DB-<nn>` | Logical database requirement | DB-012 |
| `CMP-<nn>` | Compliance requirement | CMP-004 |
| `AC-<REQID>-<nn>` | Acceptance criterion for a requirement | AC-REQ-POS-001-01 |
| `OI-<nn>` | Open issue | OI-001 |

**Priority levels:** `Must` (MVP contract — BRD 17.1), `Should` (high value, second wave — BRD 17.2), `Could` (differentiator — BRD 17.3), `Won't-now` (deferred — BRD 17.4). Estimates use T-shirt sizing (`S`, `M`, `L`, `XL`) as relative complexity, to be normalized to story points at planning.

**Status values:** `Draft`, `Approved`, `In Review`, `Implemented`, `Deferred`.

**Requirement statement form:** Each requirement uses "The system shall / must / shall not" and is verifiable by a test. No ambiguous words (e.g., "easy", "fast", "user-friendly") appear without a quantified acceptance criterion.

## 1.4 Intended Audience

| Audience | Relevant Sections |
|----------|-------------------|
| Software Architect | 2, 3, 4, 5, 7, 8, 9, 10 |
| Database Architect | 2, 3, 10, 13 |
| API Architect | 5.1, 7, 8 |
| Backend Engineers | 3, 4, 5, 7, 8, 9, 12 |
| Frontend Engineers | 3, 6, 7, 8 |
| Security Engineers | 4, 5.2, 7, 8, 9 |
| QA Engineers | 3 (AC), 4, 12, 13, 16.1 |
| DevOps Engineers | 4, 5.11, 8, 9, 10 |
| Product Manager / BA | 1, 2, 3 (as validation reference) |

## 1.5 References

| Ref | Document | Version | Date |
|-----|----------|---------|------|
| [BRD] | PharmaCloud ERP — Business Analysis Package | 1.1 (Approved) | 2026-08-05 |
| [IEEE-29148] | ISO/IEC/IEEE 29148:2018 — Requirements Engineering | 2018 | — |
| [IEEE-12207] | ISO/IEC/IEEE 12207 — Software Life Cycle Processes | 2017 | — |
| [ISO-25010] | ISO/IEC 25010 — Quality Model for Systems and Software | 2011 | — |
| [ASVS] | OWASP Application Security Verification Standard | 4.0 | — |
| [BABOK] | BABOK v3 — Business Analysis Body of Knowledge | v3 | — |
| [OpenAPI] | OpenAPI Specification | 3.1 | — |
| [BPMN] | Business Process Model and Notation | 2.0 | — |

---

# 2. Overall Description

## 2.1 Product Perspective

PharmaCloud ERP is a **greenfield** (no incumbent technical debt — BRD CN-07), cloud-native, API-first, multi-tenant SaaS platform. It is a **new self-contained system** that replaces the disconnected tools used by pharmacies today (cash register, stock spreadsheet, manual expiry ledger, paper prescriptions). It sits within a larger business and technical ecosystem:

```
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │                      PHARMA OPERATING ENVIRONMENT                             │
 │  Store hardware: barcode scanner · receipt printer · cash drawer · QR scan    │
 │  Payment rails: card terminals (in-store) · QR payment · (later gateways)      │
 │  Market ecosystem: national drug reference · e-prescription programs           │
 │  Regulatory: health authority reports · tax authority e-invoicing (ZATCA)      │
 └──────────────────────────────────────────────────────────────────────────────┘
                              │  interfaces (Section 5)
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │                            PharmaCloud ERP Platform                           │
 │  ┌──────┐ ┌──────┐ ┌───────┐ ┌──────┐ ┌────────┐ ┌─────────┐ ┌──────────┐    │
 │  │ POS  │ │ Rx   │ │Inventory│ │Purch │ │Accounting│ │Reports │ │  Admin   │   │
 │  └──────┘ └──────┘ └───────┘ └──────┘ └────────┘ └─────────┘ └──────────┘    │
 │  ── Core (country-neutral) ────────────────────────────────────────────────   │
 │  Market Pack A (GCC)     Market Pack B (Yemen)     Pack N (future)             │
 │  ── Plugin / Compliance Layer (BR-LOC-01, BR-PLUG-01/02) ─────────────────    │
 │  Multi-tenant core: tenants · branches · users · roles · subscriptions         │
 │  AI-ready data core: append-only · analytics-ready · feature-flagged           │
 └──────────────────────────────────────────────────────────────────────────────┘
                              │  (out of scope MVP: patient app, supplier portal,
                                 offline-first POS, telemedicine)
```

Key architectural envelopes (behavioral requirements; exact mechanism is Architecture's):

1. **Multi-tenant SaaS** with data-layer isolation (BR-TEN-01) and runtime entitlement enforcement (BR-TEN-02).
2. **Plugin-based compliance** — market packs deliver all market-specific behavior; core remains country-neutral (BR-LOC-01, FR-LOC-01). Packs are versioned, sandbox-validated, isolated (BR-PLUG-01/02).
3. **API-first** — every function is reachable via a versioned REST API (FR-MKT-01, Section 7).
4. **AI-ready** — append-only/analytics-ready persistence; no destructive updates (FR-AI-01); feature flags (FR-AI-03).
5. **Localization-native** — Arabic (RTL) + English (BR-LOC-03, FR-LOC-02); canonical business dates with Gregorian/Hijri display (BR-LOC-04); multi-currency with base + secondary (BR-CUR-01/02).

## 2.2 Product Functions (Overview)

The platform shall provide the following function groups (details in Section 3):

1. **Pharmacy Operations** — branch setup, register/drawer shifts, day-close, counter guidance (BRD P09, FR-PH-01..05).
2. **Inventory Management** — product master, batch/expiry tracking, reorder suggestions, cycle counts, adjustments, transfers, expiry watchlist, recalls (BRD P04/P05/P07/P08, FR-INV-01..07).
3. **Sales & POS** — barcode checkout, payments (cash/card/QR/mixed), receipts, returns/refunds, voids, price overrides, restricted-product approval, layaway/credit (BRD P01/P03, FR-POS-01..07).
4. **Purchasing & Suppliers** — POs with approvals, GRN with variance/backorder, supplier returns/claims, scorecards (BRD P04/P05/P06, FR-PUR-01..05).
5. **Customers** — customer master, credit, loyalty, statements, patient minimal profile (BRD P16, FR-CUST-01..03).
6. **Prescription Management** — Rx capture/validation/fulfillment, controlled-substance register, archive, digital-Rx adapter interface (BRD P02, FR-RX-01..05).
7. **Accounting & Tax** — double-entry posting, chart of accounts, day-close posting, tax computation/exports, period locking, e-invoicing adapter (BRD P10, FR-ACC-01..05).
8. **Reporting & Compliance** — operational reports, consolidated branch reports, scheduling/delivery, compliance exports (BRD P15, FR-REP-01..04).
9. **Branch Management** — hierarchy, central policy push, inter-branch transfers, head-office dashboards (BRD P11, FR-BR-01..03).
10. **Identity & Access** — RBAC, authentication policies, audit logging (BRD P14, FR-USR-01..03).
11. **Commercial Platform** — tenant lifecycle, subscriptions/billing, notifications, tenant health (BRD P13, FR-SUB-01..04, FR-TEN-01..04).
12. **Localization & Compliance Configuration** — market-pack framework, language/currency/calendar, national drug codes, e-invoicing (BRD P17, FR-LOC-01..07).
13. **Platform Readiness** — marketplace partner API/sandbox design-in (FR-MKT), AI data foundations (FR-AI).

## 2.3 User Classes and Characteristics

User classes are derived from BRD personas (Section 5) and stakeholder matrix (Section 4). Each class is defined by the modules/functions it accesses (RBAC scoping per BR-SEC-01/02).

| Class | BRD Persona | Description | Primary Modules | Access Mode |
|-------|-------------|-------------|-----------------|-------------|
| UC-01 Pharmacy Owner | P-01 Raj | Owns 1–2 pharmacies; daily overview; night-time review | DASH, RPT, INV, PUR, ACC (read), SET | Web (desktop/tablet) |
| UC-02 Pharmacist-in-Charge | P-02 Dr. Ayesha | Licensed; accountable for dispensing safety | POS, RX, CMP, INV, AUD (read) | Web + POS terminal |
| UC-03 Store/Branch Manager | P-03 Sam | Runs one branch; day-close; staff oversight | DASH, POS, RPT, BR, USR (branch scope), NOT | Web + POS terminal |
| UC-04 Cashier / Sales Assistant | P-04 Mei | High-volume checkout; minimal training | POS, CUS (minimal), NOT | POS terminal |
| UC-05 Purchase/Inventory Manager | P-05 Omar | Replenishment, supplier terms, expiry control | INV, PUR, SUP, CMP, RPT | Web |
| UC-06 Accounts/Finance Officer | P-06 Hina | Bookkeeping, tax, reconciliation | ACC, RPT, SUB (read), CUS (credit) | Web |
| UC-07 Chain Regional Manager | P-07 Daniel | Multiple branches; policy; rebalancing | DASH, BR, RPT, INV (transfer), ROL (delegate) | Web |
| UC-08 Tenant Administrator / IT Lead | P-08 Nadia | Users, roles, branches, subscriptions, config | USR, ROL, BR, SUB, TEN, SET, AUD | Web (admin) |
| UC-09 Customer Success (Internal) | P-10 Karim | Onboarding, training, health, retention | TEN, SUB, RPT, NOT, SET | Web (internal) |
| UC-10 Platform/Super Admin (Internal) | — (STK-08/STK-17 derived) | System-wide operations, market packs, feature flags | TEN, CMP, MKT, AI, AUD, NOT, SET | Web (internal, elevated) |
| UC-11 Patient / Customer (Indirect) | P-09 Priya | Not a licensed user; represented by staff at counter | — (consumes receipts, privacy-scoped record) | Indirect |
| UC-12 Supplier (Trading partner) | STK-20 | Not a user in MVP; interacts via PO/credit notes | — (out of MVP scope) | Indirect |

**Characteristics:** Mixed technical aptitude (low for UC-04, high for UC-08/UC-10); bilingual Arabic/English with mixed-script names; high transaction volume at POS; intermittent connectivity at stores; high staff turnover at counter roles requiring minimal training (< 30 min, NFR-N-09).

## 2.4 Operating Environment

The platform shall operate in the following environment:

1. **Deployment:** Cloud-native SaaS, single initial region (GCC-region preferred — BRD AS-06, DEC-05 pending), horizontally scalable compute, managed database service, object storage.
2. **Client devices:**
   - POS terminals: tablets/desktop PCs with barcode scanner, receipt printer, cash drawer, QR reader (peripheral abstraction per BRD CN-05).
   - Web clients: modern evergreen browsers (Chrome, Edge, Firefox, Safari) on desktop and tablet; minimum viewport 1280×800 desktop, 768×1024 tablet.
   - No native mobile app in MVP (responsive web; handheld scanning app is V2 — BRD 17.3).
3. **Connectivity:** Intermittent-but-adequate internet at stores (BRD AS-07); active-transaction resilience of 30 s (NFR-N-08); no full offline mode.
4. **Languages/Locales:** Arabic (RTL) and English (LTR); Gregorian and Hijri display calendars; multi-currency base (per tenant) + secondary (USD).
5. **Integration environment:** Payment terminals (in-store), SMS/email services, object storage, cloud notification service, and (per market) tax/e-invoicing adapters (ZATCA) and digital-Rx adapters.

## 2.5 Design and Implementation Constraints

Constraints are binding; carried from BRD Section 14 and localization sections.

| # | Constraint | Source |
|---|-----------|--------|
| CON-01 | No per-tenant custom code or white-label core; configuration-over-customization is product policy. | BRD CN-01, OOS-11 |
| CON-02 | All market-specific behavior must be delivered by market packs; core shall remain country-neutral. | BRD CN-02, CN-10, BR-LOC-01 |
| CON-03 | Maintenance windows restricted to outside 08:00–22:00 local; ≤ 4 h/month total. | BRD CN-03, NFR-N-01 |
| CON-04 | MVP production go-live targeted ~12 months; MoSCoW Musts are the MVP contract. | BRD CN-04, AS-03 |
| CON-05 | Hardware diversity requires a peripheral/device abstraction layer. | BRD CN-05 |
| CON-06 | Cross-border data-flow constraints require a hosting/residency decision per market. | BRD CN-06, DEC-05 |
| CON-07 | Greenfield — no legacy migration burden; clean architecture expected. | BRD CN-07 |
| CON-08 | Finite budget/capacity — phase gating with KPI checkpoints. | BRD CN-08 |
| CON-09 | GCC VAT framework and KSA ZATCA e-invoicing impose mandatory tax formats where served. | BRD CN-09 |
| CON-10 | Market packs must not compromise multi-tenant isolation or the country-neutral core. | BRD CN-10, BR-PLUG-01/02 |
| CON-11 | Initial languages Arabic (RTL) + English only; new languages via packs, no code change. | BRD OOS-10, NFR-N-17 |
| CON-12 | No full offline mode in MVP; only brief-outage resilience (30 s active transaction). | BRD OOS-07, NFR-N-08 |
| CON-13 | MVP compliance set = best-practice base + GCC-market configured set (VAT engine, ZATCA where KSA served). | BRD AS-02, DEC-02 |

## 2.6 Assumptions and Dependencies

The SRS inherits all BRD assumptions (AS-01…AS-17) as binding unless resolved. Key ones affecting technical requirements:

- AS-01 First markets Yemen + GCC; Arabic (RTL) + English. (Confirmed)
- AS-02 Legal validation of each market pack at SRS/launch. (Hold — OI-02)
- AS-06 Single-region hosting at MVP. (Pending DEC-05)
- AS-07 Intermittent internet; 30 s resilience sufficient. (Hold)
- AS-08 Barcode + printed receipts are the store default; digital receipts additive.
- AS-09 Suppliers reached by print/email PO in MVP.
- AS-11 Migration via structured CSV/Excel import + manual validation in MVP.
- AS-15 Multi-currency from MVP; base currency per tenant; USD secondary.
- AS-17 KSA launch requires ZATCA-compliant e-invoicing.

**Dependencies (technical):** availability of payment-gateway selection (DEC-06), hosting region (DEC-05), go-live sequencing (DEC-08/09), legal validation of market packs (AS-02), and national drug-reference data availability for GCC + Yemen packs (BRD 7.3). None block SRS/architecture kickoff (BRD §21).

---

# 3. Functional Requirements by Module

This section specifies the functional requirements of every module. Each module begins with an overview (business goal, description, target users, dependencies, priority) and a requirements catalog, followed by detailed requirement specifications. All requirements trace to the BRD; trace references use BRD IDs (`FR-*`, `BR-*`, `P-nn`, `KPI-*`, `BO-*`, `PG-*`).

**Reading key:** Priority — `Must` / `Should` / `Could` / `Won't-now` (per BRD §17). Estimate — T-shirt (S/M/L/XL). Status — Draft by default. Acceptance criteria are numbered `AC-<REQ-ID>-<nn>` and are mandatory test inputs for QA.

---

## 3.1 MOD-01 — Dashboard

### 3.1.1 Module Overview

| Attribute | Detail |
|-----------|--------|
| Module Name | Dashboard |
| Business Goal | Give owners, branch managers, and chain managers live, consolidated operational truth — the "open the dashboard daily in <1 min" success criterion of personas P-01, P-03, P-07 (BRD §5, P15). |
| Description | A role- and scope-aware home screen composed of configurable widgets (sales, profit, expiry watchlist, low stock, cash status, branch comparison). Data is generated from posted, reconciled data with a visible data-currency timestamp (BR-REP-01). |
| Business Value | Reduces manual report compilation; surfaces expiry/stockout/cash problems early; supports chain consolidation (OP-02); drives time-to-value (KPI-08/09). |
| Target Users | UC-01 Owner, UC-03 Store Manager, UC-07 Chain Regional Manager, UC-08 Tenant Admin, UC-09 Customer Success, UC-10 Platform Admin |
| Dependencies | All operational modules (INV, POS, ACC, RPT, BR, CMP); RBAC (USR/ROL); tenant config (TEN/SET) |
| Priority | Must (core widgets), Should (configurable layout) |
| Source / Trace | BRD FR-REP-01/02, FR-BR-03, FR-TEN-03, P15, BR-REP-01/02, KPI-08 |

### 3.1.2 Requirements Catalog

| ID | Requirement | Priority | Estimate | Dependencies | BRD Trace |
|----|-------------|----------|----------|--------------|-----------|
| REQ-DASH-001 | Owner Dashboard — daily sales, profit, expiry watchlist, cash status | Must | M | ACC, INV, POS postings | FR-REP-01, P15, BR-REP-01, P-01 |
| REQ-DASH-002 | Branch/Chain Consolidated Dashboard | Must | M | BR, BR-REP-02 | FR-BR-03, FR-REP-02, BR-REP-02, P-07 |
| REQ-DASH-003 | Head-Office Performance Comparison Dashboard | Should | M | DASH-002, BR | FR-REP-01 ext., P-07 |
| REQ-DASH-004 | Tenant Health Dashboard (internal) | Must | M | TEN, SUB, NOT | FR-TEN-03, P13, KPI-04/05 |
| REQ-DASH-005 | Expiry Watchlist Widget | Must | S | INV (FR-INV-06) | FR-INV-06, P08, BR-STK-04, P-01 |
| REQ-DASH-006 | Reorder / Low-Stock Widget | Must | S | INV (FR-INV-03) | FR-INV-03, BR-PUR-04, P-05 |
| REQ-DASH-007 | Configurable Widgets and Layout | Should | M | DASH-001, SET | FR-TEN-02, NFR-N-09 |
| REQ-DASH-008 | Sales Margin by Product Widget | Should | S | ACC (FIFO), POS | FR-REP-01 ext., BR-ACC-04 |
| REQ-DASH-009 | Data-Currency Indicator and Refresh | Must | S | RPT engine | BR-REP-01, NFR-N-02 |

### 3.1.3 Detailed Requirements

#### REQ-DASH-001 — Owner Dashboard

| Field | Detail |
|-------|--------|
| Description | The system shall provide a dashboard presenting the tenant's current-period sales (value and transaction count), gross profit, cash status per payment type, and a prioritized expiry watchlist, for the tenant or a selected branch. |
| Actors | UC-01 Owner, UC-03 Store Manager |
| Preconditions | User authenticated; tenant has active market pack (BR-LOC-02); at least one branch configured; data posted by prior day-close or live sales. |
| Postconditions | User sees a role- and branch-scoped summary; data refreshed per REQ-DASH-009. |
| Main Flow | 1. User opens Dashboard. 2. System applies RBAC + branch scope. 3. System loads summary aggregates from posted data (sales value, transaction count, gross profit, cash per payment type). 4. System loads expiry watchlist top items. 5. System renders widgets with data-currency timestamp. 6. User may switch tenant/branch scope. |
| Alternative Flows | 1a. No data for period — system shows empty-state with guidance. 2a. User lacks branch scope — system shows only accessible branches. 3a. Connectivity loss — system shows last available snapshot with currency timestamp and "stale" indicator. |
| Business Rules | BR-REP-01, BR-BRANCH-01, BR-TEN-02, BR-SEC-01/02 |
| Validation Rules | All figures derived from posted/reconciled data; no client-side fabrication. Currency timestamp mandatory on every widget. |
| Error Conditions | ERR-DASH-001: No permission → 403 and access-denied view. ERR-DASH-002: Branch scope invalid → error message, no partial data. ERR-DASH-003: Data source unavailable → stale indicator, no silent zero-fill. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-DASH-009, REQ-INV-003 (watchlist), REQ-POS postings, REQ-ACC postings |
| Acceptance Criteria | **AC-REQ-DASH-001-01:** Dashboard renders all mandated widgets for a valid scope in ≤ 3 s (p95) on 90 days of data. **AC-REQ-DASH-001-02:** Values match the corresponding report in REQ-RPT-001 to zero variance. **AC-REQ-DASH-001-03:** Every widget displays a data-currency timestamp; stale snapshot is visibly flagged. **AC-REQ-DASH-001-04:** Users see only branches in their scope. |
| Status | Draft |

#### REQ-DASH-002 — Branch/Chain Consolidated Dashboard

| Field | Detail |
|-------|--------|
| Description | The system shall present consolidated tenant-wide or multi-branch aggregates that balance exactly to the sum of branch-level values (BR-REP-02), with drill-down to any branch. |
| Actors | UC-07 Chain Regional Manager, UC-01 Owner, UC-08 Tenant Admin |
| Preconditions | Tenant has ≥ 2 branches; hierarchy defined (BR-BRANCH-01); user has consolidated scope. |
| Postconditions | User views consolidated metrics and can drill down to branch-level detail. |
| Main Flow | 1. User selects consolidated scope (tenant/all branches/region). 2. System aggregates per branch. 3. System renders totals with per-branch contribution. 4. User drills into a branch for detail. |
| Alternative Flows | 3a. Branch offline — system shows last posted values with timestamp and stale flag. |
| Business Rules | BR-BRANCH-01, BR-BRANCH-02, BR-REP-02, BR-TEN-02 |
| Validation Rules | Consolidated totals = Σ branch totals (unit test + runtime invariant). |
| Error Conditions | ERR-DASH-002-01: Inconsistent totals detected → block render, raise alert, log to AUD. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-BR-001 (hierarchy), REQ-BR-003 (head-office), REQ-RPT-002 |
| Acceptance Criteria | **AC-REQ-DASH-002-01:** Consolidated = Σ branch-level for sales, profit, cash (verified by reconciliation test). **AC-REQ-DASH-002-02:** Drill-down reaches branch in ≤ 2 clicks. **AC-REQ-DASH-002-03:** Render ≤ 3 s p95 at 40 branches. |
| Status | Draft |

#### REQ-DASH-003 — Head-Office Performance Comparison Dashboard

| Field | Detail |
|-------|--------|
| Description | The system shall provide comparative views (branch vs branch; vs targets) for sales, margin, stock health, and policy deviations, to support regional management (persona P-07). |
| Actors | UC-07 Chain Regional Manager |
| Preconditions | Consolidated dashboard enabled; targets optionally configured in SET. |
| Postconditions | Manager can identify under/over-performing branches and policy deviations. |
| Main Flow | 1. Select comparison period and metric. 2. System computes per-branch values and targets. 3. System renders ranking/comparison chart. 4. User filters by region. |
| Alternative Flows | 2a. No targets configured — targets omitted, actuals only. |
| Business Rules | BR-BRANCH-02, BR-REP-01/02 |
| Validation Rules | Comparison figures reconcile to consolidated report. |
| Error Conditions | ERR-DASH-003-01: Metric unsupported → disabled control. |
| Priority / Estimate | Should / M |
| Dependencies | REQ-DASH-002, REQ-SET-005 (targets) |
| Acceptance Criteria | **AC-REQ-DASH-003-01:** Comparison view renders ≤ 3 s for 40 branches. **AC-REQ-DASH-003-02:** Deviation-from-policy flags match the policy-push log (REQ-BR-002). |
| Status | Draft |

#### REQ-DASH-004 — Tenant Health Dashboard (Internal)

| Field | Detail |
|-------|--------|
| Description | The system shall provide an internal dashboard showing each tenant's usage, license/entitlement utilization (users/branches/transactions/storage vs plan limits), billing health, error rates, and a daily-computed health score (BRD FR-TEN-03). |
| Actors | UC-09 Customer Success, UC-10 Platform Admin |
| Preconditions | Internal platform role; tenant provisioning exists. |
| Postconditions | CS/Admin can identify at-risk tenants and act (contact, upgrade, support). |
| Main Flow | 1. Open tenant health list. 2. System computes health score daily (per NFR and quota data). 3. System flags alerts (usage ≥ 80/90/100%, billing overdue, error spikes). 4. User filters by segment/status. |
| Alternative Flows | 3a. Threshold crossed → automatic notification per REQ-NOT-002. |
| Business Rules | BR-TEN-02/03, BR-SUB-01/02, BR-SEC-02 |
| Validation Rules | Health score computed from deterministic weighted inputs; score history retained. |
| Error Conditions | ERR-DASH-004-01: Telemetry missing → score marked "insufficient data", never zero. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-TEN-003 (config), REQ-SUB-001 (limits), REQ-NOT-002 |
| Acceptance Criteria | **AC-REQ-DASH-004-01:** Health score computed and stored daily for every active tenant. **AC-REQ-DASH-004-02:** Quota warnings generated at 80/90/100% per BR-SUB-01. **AC-REQ-DASH-004-03:** Internal-only visibility enforced (RBAC). |
| Status | Draft |

#### REQ-DASH-005 — Expiry Watchlist Widget

| Field | Detail |
|-------|--------|
| Description | The system shall surface batches within configurable expiry thresholds (default 90/30 days per BR-STK-04) on the dashboard, prioritized by expiry date, with quarantine status. |
| Actors | UC-01, UC-02, UC-03, UC-05 |
| Preconditions | Batch/expiry data recorded (REQ-INV-001/003). |
| Postconditions | User sees expiring stock and acts (promote/return/destroy per P08). |
| Main Flow | 1. System evaluates batches vs thresholds daily. 2. System renders watchlist sorted by expiry. 3. User navigates to INV quarantine/disposition action. |
| Alternative Flows | 1a. No expiring stock — empty-state with next-check time. |
| Business Rules | BR-STK-04, BR-REP-01 |
| Validation Rules | Watchlist updates on a daily schedule and on demand; quarantined batches flagged. |
| Error Conditions | ERR-DASH-005-01: Batch data inconsistent → excluded + audit warning. |
| Priority / Estimate | Must / S |
| Dependencies | REQ-INV-003, REQ-INV-004 |
| Acceptance Criteria | **AC-REQ-DASH-005-01:** Watchlist reflects BR-STK-04 thresholds exactly (90/30 configurable). **AC-REQ-DASH-005-02:** Renders ≤ 2 s with 100k stock lines. |
| Status | Draft |

#### REQ-DASH-006 — Reorder / Low-Stock Widget

| Field | Detail |
|-------|--------|
| Description | The system shall surface current reorder suggestions (demand + min/max signals) from REQ-INV-005 on the dashboard with one-click navigation to purchase suggestions (REQ-PUR-004). |
| Actors | UC-01, UC-05 |
| Preconditions | Reorder logic configured (min/max or demand signal). |
| Postconditions | User can review and navigate to purchase suggestion list. |
| Main Flow | 1. System loads open suggestions. 2. Renders count + top items. 3. Navigate to PUR. |
| Alternative Flows | 1a. None — empty-state. |
| Business Rules | BR-PUR-04, BR-REP-01 |
| Validation Rules | Suggestions never auto-create POs (human confirmation required). |
| Error Conditions | ERR-DASH-006-01: Reorder config absent → hint to configure, no suggestions. |
| Priority / Estimate | Must / S |
| Dependencies | REQ-INV-005, REQ-PUR-004 |
| Acceptance Criteria | **AC-REQ-DASH-006-01:** Widget shows only active products with defined signals (BR-PUR-04). **AC-REQ-DASH-006-02:** Navigation to suggestion list in ≤ 1 click. |
| Status | Draft |

#### REQ-DASH-007 — Configurable Widgets and Layout

| Field | Detail |
|-------|--------|
| Description | The system shall allow authorized users to add/remove/reorder dashboard widgets and persist layout per user (and optional per-role default). |
| Actors | UC-01, UC-03, UC-07, UC-08 |
| Preconditions | RBAC grants dashboard-config permission. |
| Postconditions | Layout persisted; takes effect on next load. |
| Main Flow | 1. User enters edit mode. 2. Add/remove/reorder widgets. 3. Save. 4. System persists and reloads. |
| Alternative Flows | 3a. Exceeds widget quota — blocked with message. |
| Business Rules | BR-TEN-02, BR-SEC-02 |
| Validation Rules | Layout change audited (AUD); entitlements enforced (widget may be plan-gated). |
| Error Conditions | ERR-DASH-007-01: Unauthorized → 403. |
| Priority / Estimate | Should / M |
| Dependencies | REQ-SET-003 |
| Acceptance Criteria | **AC-REQ-DASH-007-01:** Layout persists across sessions for the user. **AC-REQ-DASH-007-02:** Widget availability enforced per plan entitlement. |
| Status | Draft |

#### REQ-DASH-008 — Sales Margin by Product Widget

| Field | Detail |
|-------|--------|
| Description | The system shall show gross margin by product/line based on FIFO cost valuation, supporting "which products actually make money" (P-01) and margin-based reordering. |
| Actors | UC-01, UC-05 |
| Preconditions | FIFO valuation active (BR-ACC-04); cost recorded at GRN. |
| Postconditions | User sees margin ranking and can open full margin report (REQ-RPT-001). |
| Main Flow | 1. System computes margin (revenue − COGS per FIFO). 2. Renders top/lowest margin items. 3. Drill to report. |
| Alternative Flows | 1a. Cost missing on some lines — excluded with flag and counted. |
| Business Rules | BR-ACC-04, BR-REP-01 |
| Validation Rules | Margin figures reconcile to ACC ledger. |
| Error Conditions | ERR-DASH-008-01: Valuation inconsistent → show warning, block export. |
| Priority / Estimate | Should / S |
| Dependencies | REQ-ACC-004, REQ-RPT-001 |
| Acceptance Criteria | **AC-REQ-DASH-008-01:** Margin reconciles to ledger to zero drift. **AC-REQ-DASH-008-02:** Missing-cost items flagged, never silently excluded. |
| Status | Draft |

#### REQ-DASH-009 — Data-Currency Indicator and Refresh

| Field | Detail |
|-------|--------|
| Description | The system shall display the data-currency timestamp on every dashboard widget and support manual refresh and configurable auto-refresh (default 60 s, no refresh during active POS sale screens). |
| Actors | All dashboard users |
| Preconditions | Dashboard rendered. |
| Postconditions | Widgets display current-as-of timestamp. |
| Main Flow | 1. System stamps each aggregate with last-posted time. 2. Renders. 3. Auto/manual refresh reloads aggregates. |
| Alternative Flows | 3a. Refresh fails (outage) — stale indicator retained, no data loss. |
| Business Rules | BR-REP-01, NFR-N-08 |
| Validation Rules | Timestamp must reflect source data generation time, not client clock. |
| Error Conditions | ERR-DASH-009-01: Clock skew > 5 min between server and client → display uses server time. |
| Priority / Estimate | Must / S |
| Dependencies | None |
| Acceptance Criteria | **AC-REQ-DASH-009-01:** All widgets show currency timestamp. **AC-REQ-DASH-009-02:** Refresh interval configurable per tenant; active-sale protection prevents disruptive reloads. |
| Status | Draft |

---

## 3.2 MOD-02 — Medicines / Product Master

### 3.2.1 Module Overview

| Attribute | Detail |
|-----------|--------|
| Module Name | Medicines / Product Master |
| Business Goal | Maintain a single authoritative, classification-aware product master for drugs, non-drugs, and service items, with multiple barcodes, batch handling rules, tax treatment, pricing, and national drug-code mapping (BRD FR-INV-01, FR-LOC-06). |
| Description | The product master is the shared reference for POS, inventory, purchasing, and accounting. It enforces pricing/tax/controlled-substance/restricted-category rules at the source. |
| Business Value | Eliminates price-lookup errors and duplicate codes (P-04); enables automatic tax computation (BR-TAX-01); enables national drug-code search and barcode resolution per market (FR-LOC-06); foundation of recall/controlled-substance management. |
| Target Users | UC-01, UC-05, UC-08 (admin), UC-03 |
| Dependencies | CMP (market pack for tax/drug reference), ROL (permission), AUD, SET |
| Priority | Must (core master), Could (advanced classes) |
| Source / Trace | BRD FR-INV-01, FR-POS-01, FR-LOC-06, BR-PRC-01..03, BR-TAX-01, BR-SAL-06, BR-CTL-01, P04/P05 |

### 3.2.2 Requirements Catalog

| ID | Requirement | Priority | Estimate | Dependencies | BRD Trace |
|----|-------------|----------|----------|--------------|-----------|
| REQ-MED-001 | Product Master Create/Edit (drug/non-drug/service) | Must | M | CMP, AUD | FR-INV-01, P04/P05 |
| REQ-MED-002 | Multiple Barcodes per Product | Must | S | MED-001 | FR-INV-01 |
| REQ-MED-003 | Batch/Lot Handling per Product Class | Must | S | MED-001 | BR-STK-01, FR-INV-02 |
| REQ-MED-004 | Tax Treatment per Product | Must | S | CMP (tax engine) | BR-TAX-01, FR-INV-01 |
| REQ-MED-005 | Pricing & Price Lists (per branch, HO override) | Must | M | BR, CMP | BR-PRC-01/02/03, FR-POS-01 |
| REQ-MED-006 | National Drug Code + GS1/SFDA Barcode Mapping | Must | L | CMP (market pack), MED-002 | FR-LOC-06 |
| REQ-MED-007 | Product Bulk Import (CSV/Excel) | Must | M | MED-001 | AS-11, FR-TEN-04 |
| REQ-MED-008 | Restricted-Category Flag & Approval Enforcement | Must | S | MED-001, POS | BR-SAL-06, FR-POS-06 |
| REQ-MED-009 | Controlled-Substance Classification | Must | M | MED-001, CMP | BR-CTL-01..04, FR-RX-03 |
| REQ-MED-010 | Product Categorization & Grouping | Should | S | MED-001 | FR-INV-01 |
| REQ-MED-011 | Product Deactivation with Safety Checks | Must | S | MED-001, INV | BR-AUD-01, BR-STK-02 |
| REQ-MED-012 | Duplicate Barcode Detection | Must | S | MED-002 | FR-INV-01 |

### 3.2.3 Detailed Requirements

#### REQ-MED-001 — Product Master Create/Edit

| Field | Detail |
|-------|--------|
| Description | The system shall allow authorized users to create and edit products with classification (drug / non-drug / service), pack units, barcodes, tax treatment, category, and class-specific attributes (e.g., batch-required flag, prescription-required flag). Product creation via form or import shall take ≤ 5 minutes (BRD FR-INV-01). |
| Actors | UC-05, UC-08, UC-01 |
| Preconditions | User has product-management permission; active market pack defines reference/labeling defaults. |
| Postconditions | Product persisted with audit record; available to POS/inventory/purchasing. |
| Main Flow | 1. User opens product form. 2. Enters classification and attributes. 3. System validates (tax treatment, barcode uniqueness, required fields, no negative price). 4. System persists product + audit event. |
| Alternative Flows | 3a. Duplicate barcode → error per REQ-MED-012. 3b. Import path → REQ-MED-007. 3c. Market pack requires extra fields (e.g., national code) → fields mandatory per pack. |
| Business Rules | BR-PRC-01/03, BR-TAX-01, BR-AUD-01, BR-SEC-02 |
| Validation Rules | Barcodes unique per tenant; price ≥ 0; tax treatment from active pack; controlled-substance flag requires market-valid classification. |
| Error Conditions | ERR-MED-001-01: Missing mandatory market-pack field → block save with field list. ERR-MED-001-02: Invalid tax treatment → block. ERR-MED-001-03: Unauthorized → 403. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-CMP-001 (pack defaults), REQ-AUD-001 |
| Acceptance Criteria | **AC-REQ-MED-001-01:** Create/edit completes in ≤ 5 min for a trained user. **AC-REQ-MED-001-02:** All creates/edits recorded immutably in audit log. **AC-REQ-MED-001-03:** Negative price rejected (BR-PRC-03). **AC-REQ-MED-001-04:** Market-pack mandatory fields enforced at save. |
| Status | Draft |

#### REQ-MED-002 — Multiple Barcodes per Product

| Field | Detail |
|-------|--------|
| Description | The system shall support multiple barcodes per product (GS1/EAN/UPC and national codes), all resolvable to the product at POS/inventory scan. |
| Actors | UC-05, UC-08 |
| Preconditions | Product exists. |
| Postconditions | All barcodes resolve to the product; new barcode additions are audit-logged. |
| Main Flow | 1. Open product. 2. Add barcode(s). 3. System validates uniqueness. 4. Save. |
| Alternative Flows | 3a. Barcode already used → reject with owner reference. |
| Business Rules | BR-AUD-01, FR-INV-01 (duplicate detection) |
| Validation Rules | Barcode format validated per active pack (GS1 checksum where applicable). |
| Error Conditions | ERR-MED-002-01: Duplicate → error identifying conflicting product. |
| Priority / Estimate | Must / S |
| Dependencies | REQ-MED-001 |
| Acceptance Criteria | **AC-REQ-MED-002-01:** Each barcode resolves to exactly one product; scan time < 1 s (REQ-POS-001). **AC-REQ-MED-002-02:** Duplicate barcode rejected across tenant. |
| Status | Draft |

#### REQ-MED-003 — Batch/Lot Handling per Product Class

| Field | Detail |
|-------|--------|
| Description | The system shall allow products to be classified as batch-managed (lot + expiry required at receipt) or no-batch (BR-STK-01 exception class), and enforce the appropriate receipt/sale behavior. |
| Actors | UC-05, UC-08 |
| Preconditions | Product class defined. |
| Postconditions | Inventory engine applies correct batch rules for the class. |
| Main Flow | 1. Configure class batch flag. 2. System enforces at GRN (batch+expiry required) or allows no-batch flow. |
| Alternative Flows | None. |
| Business Rules | BR-STK-01, BR-STK-02 |
| Validation Rules | Batch-managed class cannot receive stock without batch+future expiry. |
| Error Conditions | ERR-MED-003-01: Receipt without batch/expiry for batch class → blocked. |
| Priority / Estimate | Must / S |
| Dependencies | REQ-MED-001, REQ-INV-001 |
| Acceptance Criteria | **AC-REQ-MED-003-01:** Batch-class receipts require lot + non-past expiry; no-batch class allowed without. |
| Status | Draft |

#### REQ-MED-004 — Tax Treatment per Product

| Field | Detail |
|-------|--------|
| Description | The system shall assign each product a tax treatment from the active market pack (e.g., VAT 0/5/15% or exempt) and compute tax on every taxable sale line (BR-TAX-01). |
| Actors | UC-05, UC-08 |
| Preconditions | Active market pack defines tax rates (REQ-CMP-001). |
| Postconditions | Product tax treatment available to POS/ACC. |
| Main Flow | 1. Assign tax treatment. 2. System validates against pack. 3. Save. |
| Alternative Flows | 1a. Tenant override per pack policy → recorded with reason. |
| Business Rules | BR-TAX-01, BR-LOC-01, BR-TAX-03 |
| Validation Rules | Tax treatment must exist in active pack; rate changes versioned. |
| Error Conditions | ERR-MED-004-01: Unknown treatment → rejected. |
| Priority / Estimate | Must / S |
| Dependencies | REQ-CMP-001 |
| Acceptance Criteria | **AC-REQ-MED-004-01:** Tax computed on every taxable line per assigned treatment. **AC-REQ-MED-004-02:** Exempt products produce no tax. |
| Status | Draft |

#### REQ-MED-005 — Pricing & Price Lists

| Field | Detail |
|-------|--------|
| Description | The system shall maintain price lists (tenant and per-branch) with effective dates; sale-line prices derive from the active price list or an approved manual price (BR-PRC-01). Head-office may push central prices in chain tenancies with branch override + reason (BR-PRC-02, BR-BRANCH-02). |
| Actors | UC-01, UC-05, UC-08, UC-07 |
| Preconditions | Product exists; branch hierarchy where chain. |
| Postconditions | Effective prices available at POS; manual overrides approved and logged. |
| Main Flow | 1. Create/edit price list. 2. Apply to product/branch. 3. System activates on effective date. 4. POS uses active price. |
| Alternative Flows | 4a. Manual price at POS → REQ-POS-008 (approval + log). |
| Business Rules | BR-PRC-01/02/03, BR-BRANCH-02, BR-SEC-03 |
| Validation Rules | Price ≥ 0; not below minimum margin without approval (if enabled); negative price impossible. |
| Error Conditions | ERR-MED-005-01: Price below minimum margin without approval → blocked. ERR-MED-005-02: Overlapping effective dates → warning/conflict. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-BR-002 (policy push), REQ-CMP-002 (currency) |
| Acceptance Criteria | **AC-REQ-MED-005-01:** POS line price equals active price-list price or approved override. **AC-REQ-MED-005-02:** Overrides above threshold require approval and are logged. **AC-REQ-MED-005-03:** Central price push propagates to branches < 60 s (FR-BR-01). |
| Status | Draft |

#### REQ-MED-006 — National Drug Code + GS1/SFDA Barcode Mapping

| Field | Detail |
|-------|--------|
| Description | The system shall capture and store national drug-registration codes and GS1/SFDA-aligned barcodes per the active market pack, and resolve scans against them (BRD FR-LOC-06). |
| Actors | UC-05, UC-08 |
| Preconditions | Market pack provides national code schema/format. |
| Postconditions | Products searchable by national code; barcodes resolve per pack. |
| Main Flow | 1. Capture national code on product. 2. Validate format per pack. 3. Store and index. 4. POS search resolves by national code. |
| Alternative Flows | 1a. Reference-data import from pack → REQ-MED-007 variant. |
| Business Rules | BR-LOC-01, FR-LOC-06 |
| Validation Rules | National code format validated per active pack. |
| Error Conditions | ERR-MED-006-01: Invalid format → rejected with format hint. |
| Priority / Estimate | Must / L |
| Dependencies | REQ-CMP-006 (pack drug-reference), REQ-MED-002 |
| Acceptance Criteria | **AC-REQ-MED-006-01:** Scan of a GS1/national barcode resolves to product in < 1 s. **AC-REQ-MED-006-02:** National code searchable in < 2 s. |
| Status | Draft |

#### REQ-MED-007 — Product Bulk Import (CSV/Excel)

| Field | Detail |
|-------|--------|
| Description | The system shall support self-serve bulk import of products/customers via structured CSV/Excel with validation report, error rows, and dry-run (BRD AS-11). |
| Actors | UC-05, UC-08 |
| Preconditions | Import permission; template available. |
| Postconditions | Valid rows imported; invalid rows reported; import audit-logged. |
| Main Flow | 1. Download template. 2. Upload file. 3. System validates rows (mandatory fields, barcodes, tax, codes). 4. Dry-run report. 5. Commit valid rows; produce error report. |
| Alternative Flows | 3a. File malformed → reject with reason. 5a. Duplicate rows within file → dedupe/flag per policy. |
| Business Rules | BR-AUD-01, FR-TEN-04, AS-11 |
| Validation Rules | Row-level validation identical to form validation (REQ-MED-001). |
| Error Conditions | ERR-MED-007-01: Malformed file → blocked with message. ERR-MED-007-02: Exceeds import size limit → split guidance. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-MED-001, REQ-MED-002 |
| Acceptance Criteria | **AC-REQ-MED-007-01:** Import of 10k rows completes ≤ 10 min; error report lists every rejected row with reason. **AC-REQ-MED-007-02:** No partial unrecorded import — commit is atomic + audited. |
| Status | Draft |

#### REQ-MED-008 — Restricted-Category Flag & Approval Enforcement

| Field | Detail |
|-------|--------|
| Description | The system shall allow products to be flagged restricted-category (per config); POS shall block finalization of such lines until an authorized pharmacist approval event is recorded (BR-SAL-06). |
| Actors | UC-05, UC-08 (config), UC-02 (approve) |
| Preconditions | Restricted category configured; product flagged. |
| Postconditions | Restricted sale requires pharmacist approval before finalization. |
| Main Flow | 1. Flag product restricted. 2. POS sale with restricted line. 3. System blocks finalize. 4. Pharmacist approves with identity. 5. Sale finalizes. |
| Alternative Flows | 4a. No pharmacist on shift → sale held, not lost. |
| Business Rules | BR-SAL-06, BR-SEC-03, BR-AUD-01 |
| Validation Rules | Approval event carries pharmacist identity + timestamp. |
| Error Conditions | ERR-MED-008-01: Finalize without approval → blocked with clear prompt. |
| Priority / Estimate | Must / S |
| Dependencies | REQ-MED-001, REQ-POS-009 |
| Acceptance Criteria | **AC-REQ-MED-008-01:** Restricted line cannot finalize without approval event (BR-SAL-06). **AC-REQ-MED-008-02:** Approval logged with identity/timestamp. |
| Status | Draft |

#### REQ-MED-009 — Controlled-Substance Classification

| Field | Detail |
|-------|--------|
| Description | The system shall classify products as controlled substances per market configuration; every controlled-substance transaction shall create an immutable register entry (BR-CTL-01). |
| Actors | UC-08, UC-05 (view/enter), UC-02 |
| Preconditions | Market pack defines controlled-substance schedule schema. |
| Postconditions | Product participates in controlled-substance register; sales require purchaser/requisition reference where required (BR-CTL-02). |
| Main Flow | 1. Classify product. 2. System routes its transactions to register. 3. Register reconciles to stock at any time (BR-CTL-03). |
| Alternative Flows | 2a. Disposal → witnessed destruction per REQ-INV-010 (BR-CTL-04). |
| Business Rules | BR-CTL-01..04, BR-RX-06, FR-RX-03 |
| Validation Rules | Register entries immutable; no deletes; corrections via reversing entries. |
| Error Conditions | ERR-MED-009-01: Unsupported schedule for market → classification blocked. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-CMP-007 (controlled register per pack), REQ-MED-001 |
| Acceptance Criteria | **AC-REQ-MED-009-01:** Every controlled transaction creates an immutable register entry (receive/sell/transfer/adjust/destroy). **AC-REQ-MED-009-02:** Register reconciles to stock at any time. |
| Status | Draft |

#### REQ-MED-010 — Product Categorization & Grouping

| Field | Detail |
|-------|--------|
| Description | The system shall support hierarchical product categories and groups for reporting, recall scoping, and purchasing analytics. |
| Actors | UC-05, UC-08 |
| Preconditions | Product exists. |
| Postconditions | Categories usable in reports/filters. |
| Main Flow | 1. Create category tree. 2. Assign products. 3. Use in reports/filters. |
| Alternative Flows | None. |
| Business Rules | BR-REP-01, FR-INV-01 |
| Validation Rules | Category names unique per tenant; product category mandatory for drugs. |
| Error Conditions | ERR-MED-010-01: Cycle in hierarchy → rejected. |
| Priority / Estimate | Should / S |
| Dependencies | REQ-MED-001 |
| Acceptance Criteria | **AC-REQ-MED-010-01:** Category filter available in stock/sales reports. |
| Status | Draft |

#### REQ-MED-011 — Product Deactivation with Safety Checks

| Field | Detail |
|-------|--------|
| Description | The system shall allow product deactivation only when safe: no sellable stock remains, no open POs, and deactivation never deletes history (soft deactivate + audit) (BR-AUD-01). |
| Actors | UC-05, UC-08 |
| Preconditions | Product exists. |
| Postconditions | Product excluded from new sales/POs; history preserved. |
| Main Flow | 1. Request deactivation. 2. System checks sellable stock + open POs. 3. Blocks or allows with reason. 4. Audit event. |
| Alternative Flows | 2a. Sellable stock > 0 → block with stock summary; require adjustment/transfer first. |
| Business Rules | BR-AUD-01, BR-STK-02, BR-PUR-01 |
| Validation Rules | No deletion of transactional history (soft-delete/archive per DB requirements). |
| Error Conditions | ERR-MED-011-01: Blocked due to stock → message with quantities. |
| Priority / Estimate | Must / S |
| Dependencies | REQ-INV-001, REQ-AUD-001 |
| Acceptance Criteria | **AC-REQ-MED-011-01:** Deactivation blocked while sellable stock or open POs exist. **AC-REQ-MED-011-02:** Historical transactions remain queryable after deactivation. |
| Status | Draft |

#### REQ-MED-012 — Duplicate Barcode Detection

| Field | Detail |
|-------|--------|
| Description | The system shall detect and reject duplicate barcodes (and duplicate national codes) tenant-wide at creation, import, and receipt (BRD FR-INV-01). |
| Actors | System |
| Preconditions | Barcode captured. |
| Postconditions | No two active products share a barcode/national code. |
| Main Flow | 1. Capture barcode. 2. System checks uniqueness. 3. Unique → accept; duplicate → reject with reference. |
| Alternative Flows | None. |
| Business Rules | FR-INV-01 |
| Validation Rules | Uniqueness enforced in form, import, and API. |
| Error Conditions | ERR-MED-012-01: Duplicate → 409 with owner product reference. |
| Priority / Estimate | Must / S |
| Dependencies | REQ-MED-002 |
| Acceptance Criteria | **AC-REQ-MED-012-01:** Duplicate barcode rejected across all entry paths. |
| Status | Draft |

---

## 3.3 MOD-03 — Inventory

### 3.3.1 Module Overview

| Attribute | Detail |
|-----------|--------|
| Module Name | Inventory |
| Business Goal | Track stock at product-batch-location level with quantity, cost, expiry, and status; prevent stockouts, expiry write-offs, and negative balances; support cycle counts, adjustments, transfers, and recalls (BRD FR-INV-02..07). |
| Description | The inventory engine is the correctness core of the platform. It enforces batch/expiry rules, status transitions (sellable/quarantined/committed), reorder logic, and reconciliation with accounting valuation (FIFO). |
| Business Value | Directly attacks the top cost drivers: expired stock, out-of-stocks, cash shrinkage from miscounting; provides lot-level traceability for safety and recalls (OP-01); basis for KPI-15/16. |
| Target Users | UC-02, UC-03, UC-05, UC-07 |
| Dependencies | MED (product master), PUR (GRN inputs), BR (transfers), ACC (valuation), CMP (pack rules) |
| Priority | Must |
| Source / Trace | BRD FR-INV-02..07, P05/P07/P08, BR-STK-01..07, BR-RECALL-01, BR-CTL-01..04, BR-ACC-04, KPI-15/16 |

### 3.3.2 Requirements Catalog

| ID | Requirement | Priority | Estimate | Dependencies | BRD Trace |
|----|-------------|----------|----------|--------------|-----------|
| REQ-INV-001 | Product-Batch-Location Stock Tracking | Must | XL | MED-003, PUR GRN | FR-INV-02, BR-STK-01/02, NFR-N-02 |
| REQ-INV-002 | Stock Status Transitions (sellable/quarantined/committed) | Must | M | INV-001 | FR-INV-02, BR-STK-04 |
| REQ-INV-003 | Expiry Watchlist & Quarantine | Must | M | INV-001 | FR-INV-06, BR-STK-04, P08 |
| REQ-INV-004 | Reorder Suggestions (demand + min/max) | Must | M | INV-001 | FR-INV-03, BR-PUR-04 |
| REQ-INV-005 | Cycle Counting | Must | L | INV-001 | FR-INV-04, BR-STK-03, P07 |
| REQ-INV-006 | Stock Adjustments (reason + approval) | Must | M | INV-001 | FR-INV-05, BR-STK-03/07, P07 |
| REQ-INV-007 | Negative-Stock Prevention & Correction | Must | M | INV-001 | BR-STK-07, BR-STK-02 |
| REQ-INV-008 | Inter-Branch Transfers (batch-level) | Must | XL | INV-001, BR | FR-INV-05, BR-STK-06, P11 |
| REQ-INV-009 | Recall Quarantine & Block | Must | L | INV-001, CMP | FR-INV-07, BR-RECALL-01, P08 |
| REQ-INV-010 | Disposal/Destruction Workflow | Must | M | INV-001, CMP | BR-CTL-04, P08 |
| REQ-INV-011 | Inventory Valuation Consistency (FIFO) | Must | L | INV-001, ACC | BR-ACC-04, P10 |
| REQ-INV-012 | Handheld Barcode Inventory App (V2) | Should | L | INV-005/006 | BRD §17.3, Roadmap V2 |

### 3.3.3 Detailed Requirements

#### REQ-INV-001 — Product-Batch-Location Stock Tracking

| Field | Detail |
|-------|--------|
| Description | The system shall maintain stock at product-batch-location level including quantity on hand, committed quantity, cost, expiry date, and status, for every sellable and quarantined unit. Batch-level stock queries shall return in < 2 s at 100k stock lines (BRD FR-INV-02, NFR-N-02). |
| Actors | UC-02, UC-03, UC-05, System |
| Preconditions | Product exists; GRN received (batch+expiry captured per BR-STK-01); location (branch) exists. |
| Postconditions | Stock ledger updated atomically with audit; accounting valuation affected per REQ-INV-011. |
| Main Flow | 1. Transaction (sale, receipt, transfer, adjust) changes stock. 2. System validates sellable availability (BR-STK-02). 3. System updates stock ledger atomically. 4. System posts audit + valuation effect. |
| Alternative Flows | 2a. Insufficient sellable stock → block finalization (BR-STK-02). |
| Business Rules | BR-STK-01, BR-STK-02, BR-STK-07, BR-AUD-01 |
| Validation Rules | Quantity ≥ 0 (sellable); committed + on-hand invariant maintained; single source of truth for stock. |
| Error Conditions | ERR-INV-001-01: Oversell attempt → blocked with available quantity. ERR-INV-001-02: Query > 2 s at 100k lines → performance defect (acceptance bound). |
| Priority / Estimate | Must / XL |
| Dependencies | REQ-MED-003, REQ-PUR-002 (GRN), REQ-ACC-004 |
| Acceptance Criteria | **AC-REQ-INV-001-01:** Stock query < 2 s p95 at 100k stock lines. **AC-REQ-INV-001-02:** Stock ledger reconciles to accounting valuation with 0 unexplained variance. **AC-REQ-INV-001-03:** No transaction reduces sellable stock below zero. |
| Status | Draft |

#### REQ-INV-002 — Stock Status Transitions

| Field | Detail |
|-------|--------|
| Description | The system shall manage stock statuses (sellable, quarantined, committed) with enforced transition rules: near-expiry → quarantined (BR-STK-04); recall → quarantined + blocked (BR-RECALL-01); committed quantities reserved for orders/transfers. |
| Actors | UC-02, UC-05, System |
| Preconditions | Batch tracked. |
| Postconditions | Status changes applied and audited; sale exclusion enforced by status. |
| Main Flow | 1. System evaluates batch (expiry threshold, recall list). 2. Transitions to quarantined with reason. 3. Blocks sale of quarantined stock unless Pharmacist-in-Charge override with documented justification (BR-STK-04). |
| Alternative Flows | 3a. Override → reason + identity captured and visible in reports (BR-BRANCH-02 pattern; BR-SEC-03). |
| Business Rules | BR-STK-04, BR-RECALL-01, BR-AUD-01 |
| Validation Rules | Quarantined stock cannot be sold without documented override. |
| Error Conditions | ERR-INV-002-01: Sale of quarantined stock without override → blocked. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-INV-001 |
| Acceptance Criteria | **AC-REQ-INV-002-01:** Batch within 30-day threshold auto-quarantined and blocked from sale (BR-STK-04). **AC-REQ-INV-002-02:** Override recorded with justification and identity. |
| Status | Draft |

#### REQ-INV-003 — Expiry Watchlist & Quarantine

| Field | Detail |
|-------|--------|
| Description | The system shall maintain an expiry watchlist (thresholds configurable; defaults 90/30 days) and disposition workflow (promotion, return, destruction) with documented outcomes (P08). |
| Actors | UC-02, UC-05, UC-01 |
| Preconditions | Batch/expiry data present. |
| Postconditions | Watchlist current; disposition actions executed and audited. |
| Main Flow | 1. Daily evaluation. 2. Watchlist updates. 3. Disposition decision. 4. Action executed (return per REQ-PUR-003 / destroy per REQ-INV-010). 5. Ledger impact posted. |
| Alternative Flows | 3a. Pharmacist override of quarantine (BR-STK-04). |
| Business Rules | BR-STK-04, BR-SUP-03, BR-CTL-04 |
| Validation Rules | Disposition never creates negative stock; destruction witnessed for controlled substances (BR-CTL-04). |
| Error Conditions | ERR-INV-003-01: Disposition of controlled substance without witness → blocked. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-INV-001, REQ-INV-010, REQ-PUR-003 |
| Acceptance Criteria | **AC-REQ-INV-003-01:** Watchlist thresholds configurable (defaults 90/30). **AC-REQ-INV-003-02:** All dispositions documented with reason and audit. |
| Status | Draft |

#### REQ-INV-004 — Reorder Suggestions

| Field | Detail |
|-------|--------|
| Description | The system shall generate reorder suggestions from demand signals (sales velocity, seasonality) and configured min/max for active products only; suggestions shall never auto-create purchase orders (BR-PUR-04). |
| Actors | UC-05, UC-01 |
| Preconditions | Min/max or demand signals configured for products. |
| Postconditions | Suggestion list available for human review and PO conversion (REQ-PUR-001). |
| Main Flow | 1. Generate suggestions. 2. Rank by urgency. 3. Display. 4. User selects to create PO. |
| Alternative Flows | 1a. No signal configured → product excluded. |
| Business Rules | BR-PUR-04, FR-INV-03 |
| Validation Rules | Suggestion is advisory; PO creation always requires human confirmation. |
| Error Conditions | ERR-INV-004-01: Config absent → empty list with setup hint. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-INV-001, REQ-PUR-001 |
| Acceptance Criteria | **AC-REQ-INV-004-01:** Only active products with defined signals generate suggestions. **AC-REQ-INV-004-02:** No suggestion auto-creates a PO. |
| Status | Draft |

#### REQ-INV-005 — Cycle Counting

| Field | Detail |
|-------|--------|
| Description | The system shall support scheduled cycle counts with count batch, variance reconciliation, and approval-driven adjustments (BRD FR-INV-04). |
| Actors | UC-03, UC-05, UC-02 |
| Preconditions | Count schedule configured. |
| Postconditions | Count batch completed; variances reconciled and posted via adjustment rules (REQ-INV-006). |
| Main Flow | 1. Generate count batch. 2. User enters counted quantities. 3. System computes variance. 4. User documents reason. 5. Approval per threshold. 6. Post adjustment. |
| Alternative Flows | 4a. Variance above threshold → requires manager approval (BR-STK-03). |
| Business Rules | BR-STK-03, BR-STK-07, BR-AUD-01 |
| Validation Rules | Count entry cannot create negative stock; reason mandatory on variance. |
| Error Conditions | ERR-INV-005-01: Negative count → rejected. |
| Priority / Estimate | Must / L |
| Dependencies | REQ-INV-006 |
| Acceptance Criteria | **AC-REQ-INV-005-01:** Cycle count batch completes with variance report. **AC-REQ-INV-005-02:** Variance adjustments require reason + approval above threshold. |
| Status | Draft |

#### REQ-INV-006 — Stock Adjustments

| Field | Detail |
|-------|--------|
| Description | The system shall support stock adjustments with mandatory reason codes (damage, theft, count-variance, expiry, error, regulatory); adjustments above the configured value threshold require manager approval (BR-STK-03). |
| Actors | UC-02, UC-03, UC-05 |
| Preconditions | Stock exists; reason code available. |
| Postconditions | Adjustment posted with audit; stock value updated. |
| Main Flow | 1. Select batch. 2. Enter delta + reason. 3. If above threshold → approval. 4. Post. |
| Alternative Flows | 2a. Negative correction of negative balance → manager-approval path (BR-STK-07). |
| Business Rules | BR-STK-03, BR-STK-07, BR-AUD-01, BR-SEC-03 |
| Validation Rules | Reason code mandatory; approval recorded for threshold-crossing adjustments. |
| Error Conditions | ERR-INV-006-01: No reason → blocked. ERR-INV-006-02: Above threshold without approval → blocked. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-INV-001 |
| Acceptance Criteria | **AC-REQ-INV-006-01:** Every adjustment records reason + user. **AC-REQ-INV-006-02:** Threshold approvals enforced and audited. |
| Status | Draft |

#### REQ-INV-007 — Negative-Stock Prevention & Correction

| Field | Detail |
|-------|--------|
| Description | The system shall prevent negative stock from normal transactions; only a manager-approved adjustment with mandatory reason may correct a negative balance (BR-STK-07). |
| Actors | System, UC-05, UC-03 |
| Preconditions | — |
| Postconditions | Sellable quantity never negative via normal flow. |
| Main Flow | 1. Transaction requests quantity. 2. System validates availability (BR-STK-02). 3. Insufficient → block. |
| Alternative Flows | 2a. Correction of an existing negative balance → manager-approved adjustment (BR-STK-07). |
| Business Rules | BR-STK-02, BR-STK-07 |
| Validation Rules | Post-condition invariant: sellable ≥ 0 after all normal transactions. |
| Error Conditions | ERR-INV-007-01: Oversell → block. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-INV-001 |
| Acceptance Criteria | **AC-REQ-INV-007-01:** No normal transaction creates negative stock (verified invariant). **AC-REQ-INV-007-02:** Negative-balance corrections require manager approval + reason. |
| Status | Draft |

#### REQ-INV-008 — Inter-Branch Transfers

| Field | Detail |
|-------|--------|
| Description | The system shall support batch-level inter-branch transfers with manifest, in-transit handling, variance handling, and cost allocation; source decrease must equal destination increase before close (BR-STK-06). |
| Actors | UC-03, UC-05, UC-07 |
| Preconditions | ≥ 2 branches; batch available at source. |
| Postconditions | Transfer closed balanced; both branches updated; audit complete. |
| Main Flow | 1. Create transfer at batch level. 2. Approve (qty/cost). 3. Source ships with manifest. 4. Destination receives; matches manifest. 5. Variances handled (shortage/overage). 6. Close balanced. |
| Alternative Flows | 5a. In-transit loss → variance handling with reason + audit (BR-STK-06). |
| Business Rules | BR-STK-06, BR-BRANCH-01, BR-AUTH-01, BR-AUD-01 |
| Validation Rules | Invariant: Σ source decreases = Σ destination increases at close. |
| Error Conditions | ERR-INV-008-01: Unbalanced close → blocked until resolved. |
| Priority / Estimate | Must / XL |
| Dependencies | REQ-INV-001, REQ-BR-001 |
| Acceptance Criteria | **AC-REQ-INV-008-01:** Transfer closes balanced (source = destination). **AC-REQ-INV-008-02:** Manifest and variance handling audited. **AC-REQ-INV-008-03:** Approval enforced per authorization limits. |
| Status | Draft |

#### REQ-INV-009 — Recall Quarantine & Block

| Field | Detail |
|-------|--------|
| Description | On a recall, the system shall automatically quarantine all affected batch/lot inventory across all branches and block sales, producing a system-wide affected-quantity report in < 30 s (BR-RECALL-01, FR-INV-07). |
| Actors | UC-02, UC-05, UC-10 |
| Preconditions | Recall notice received; affected batches identified (batch/product/branch scope). |
| Postconditions | All affected stock quarantined + blocked; report generated; customer traceability where applicable. |
| Main Flow | 1. Create recall. 2. Identify affected batches. 3. System quarantines across branches. 4. System blocks sales. 5. Report generated. 6. Notify customers if traced (REQ-NOT-003). 7. Execute returns/destruction (REQ-PUR-003 / REQ-INV-010). |
| Alternative Flows | 6a. Traceable customer records exist → notification sent (BRD P08). |
| Business Rules | BR-RECALL-01, BR-STK-04, BR-CTL-02, BR-AUD-01 |
| Validation Rules | Quarantine applied to every affected batch, all branches. |
| Error Conditions | ERR-INV-009-01: Incomplete batch identification → recall creation blocked until resolved. |
| Priority / Estimate | Must / L |
| Dependencies | REQ-INV-001, REQ-CMP-007 |
| Acceptance Criteria | **AC-REQ-INV-009-01:** One action quarantines all affected batches across branches. **AC-REQ-INV-009-02:** Affected-quantity report < 30 s. **AC-REQ-INV-009-03:** Sale of recalled batches blocked system-wide. |
| Status | Draft |

#### REQ-INV-010 — Disposal/Destruction Workflow

| Field | Detail |
|-------|--------|
| Description | The system shall support documented disposal/destruction with witness identity + timestamp before stock removal; controlled substances require witnessed destruction (BR-CTL-04). |
| Actors | UC-02, UC-05 |
| Preconditions | Batch eligible for disposal (expiry/damage/recall). |
| Postconditions | Stock removed with disposal certificate; ledger impact posted. |
| Main Flow | 1. Create disposal. 2. Capture witness for controlled substances. 3. Confirm removal. 4. Post ledger + audit. |
| Alternative Flows | 2a. Non-controlled → witness optional per policy. |
| Business Rules | BR-CTL-04, BR-AUD-01 |
| Validation Rules | Controlled-substance destruction requires witness identity + timestamp. |
| Error Conditions | ERR-INV-010-01: Missing witness for controlled substance → blocked. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-INV-001, REQ-CMP-007 |
| Acceptance Criteria | **AC-REQ-INV-010-01:** Controlled destruction blocked without witness. **AC-REQ-INV-010-02:** Disposal certificate generated + audit recorded. |
| Status | Draft |

#### REQ-INV-011 — Inventory Valuation Consistency (FIFO)

| Field | Detail |
|-------|--------|
| Description | The system shall value inventory on a consistent cost basis per tenant policy (FIFO default) across all postings, and reconcile inventory value to the general ledger (BR-ACC-04). |
| Actors | System, UC-06 |
| Preconditions | Cost captured at GRN (BR-PUR-02). |
| Postconditions | Inventory valuation consistent and ledger-reconciled after each day-close. |
| Main Flow | 1. Cost recorded at receipt. 2. COGS computed per valuation basis at sale. 3. Postings flow to ledger. 4. Reconciliation check at day-close (BR-ACC-02). |
| Alternative Flows | 1a. Cost variance approved per BR-STK-05 → valuation reflects approved cost. |
| Business Rules | BR-ACC-04, BR-ACC-02, BR-PUR-02 |
| Validation Rules | Valuation basis consistent per tenant; changes require audited policy change. |
| Error Conditions | ERR-INV-011-01: Reconciliation mismatch → day-close blocked (BR-ACC-02). |
| Priority / Estimate | Must / L |
| Dependencies | REQ-ACC-002, REQ-PUR-002 |
| Acceptance Criteria | **AC-REQ-INV-011-01:** Inventory value = GL inventory account after close. **AC-REQ-INV-011-02:** COGS computed per FIFO (or tenant policy). |
| Status | Draft |

#### REQ-INV-012 — Handheld Barcode Inventory App (V2)

| Field | Detail |
|-------|--------|
| Description | (V2) The system shall provide a handheld-barcode scanning workflow for cycle counts and adjustments (BRD §17.3 Could-have, Roadmap V2). |
| Actors | UC-03, UC-05 |
| Preconditions | V2 release; device with scanner. |
| Postconditions | Count/adjust performed on device, synced to system. |
| Main Flow | 1. Open count on device. 2. Scan items. 3. Enter quantities. 4. Sync. |
| Alternative Flows | 4a. Offline → queued and synced on reconnect (V2 offline review per BRD Phase 2). |
| Business Rules | BR-STK-03 |
| Validation Rules | Synced data validated as form entry. |
| Error Conditions | ERR-INV-012-01: Sync conflict → resolution prompt. |
| Priority / Estimate | Should / L |
| Dependencies | REQ-INV-005, REQ-INV-006 |
| Acceptance Criteria | **AC-REQ-INV-012-01 (V2):** Handheld count feeds cycle-count workflow. |
| Status | Deferred |

---

## 3.4 MOD-04 — Point of Sale (POS)

### 3.4.1 Module Overview

| Attribute | Detail |
|-----------|--------|
| Module Name | Point of Sale (POS) |
| Business Goal | Deliver a fast, safe, zero-training checkout for high-volume counter operations — barcode-first, sub-10-second, with enforced business rules on expiry, price, restricted products, and payments (BRD P01, P-04). |
| Description | POS is the highest-frequency surface: scan/search → cart → discount → payment (cash/card/QR/mixed) → receipt. It enforces BR-SAL, BR-PRC, BR-TAX, BR-STK, and BR-CASH rules at the point of sale and posts to stock, sales journal, cash drawer, and (via day-close) ledger. |
| Business Value | Speed and correctness at the counter eliminate price disputes, expiry risk, and under-reporting (KPI-11, KPI-17); minimal training reduces staff-turnover cost (NFR-N-09). |
| Target Users | UC-02, UC-03, UC-04, UC-01 (review) |
| Dependencies | MED (prices/barcodes), INV (stock), CUS (credit/loyalty), ACC (posting), CMP (tax/receipt footer), BR (branch attribution) |
| Priority | Must |
| Source / Trace | BRD FR-POS-01..07, FR-PH-03..05, P01/P03, BR-SAL-01..06, BR-PRC-01..03, BR-TAX-01, BR-CUST-01, BR-CASH-01/02, NFR-N-08 |

### 3.4.2 Requirements Catalog

| ID | Requirement | Priority | Estimate | Dependencies | BRD Trace |
|----|-------------|----------|----------|--------------|-----------|
| REQ-POS-001 | Barcode-First Checkout | Must | L | MED-002, INV-001 | FR-POS-01, P01 |
| REQ-POS-002 | Fast Search with Autocorrect | Must | M | MED-001 | FR-POS-01, P-04 |
| REQ-POS-003 | Cart with Line/Order Discounts | Must | M | POS-001 | FR-POS-01, BR-SAL-02 |
| REQ-POS-004 | Cash/Card/QR/Mixed Payments with Tender | Must | L | CMP (currency), EXT-PAY | FR-POS-02, BR-CUR-01 |
| REQ-POS-005 | Receipts (Print/Email/QR) with Tax + Legal Footer | Must | M | CMP (footer), EXT-RCP | FR-POS-03, BR-TAX-01, BR-LOC-01 |
| REQ-POS-006 | Returns/Refunds (linked to original sale) | Must | L | POS-001, ACC | FR-POS-04, BR-SAL-03/05 |
| REQ-POS-007 | Void with Reason Capture | Must | M | POS-001 | FR-POS-05, BR-SAL-04 |
| REQ-POS-008 | Price Override with Approval | Must | M | MED-005 | FR-POS-05, BR-PRC-01, BR-SEC-03 |
| REQ-POS-009 | Restricted-Product Pharmacist Approval | Must | M | MED-008 | FR-POS-06, BR-SAL-06 |
| REQ-POS-010 | Layaway / Credit Sale | Must | S | CUS-002 | FR-POS-07, BR-CUST-01 |
| REQ-POS-011 | Register/Drawer Shift Management | Must | M | USR | FR-PH-03, P09 |
| REQ-POS-012 | Active-Transaction Resilience | Must | L | Platform infra | FR-PH-05, NFR-N-08 |

### 3.4.3 Detailed Requirements

#### REQ-POS-001 — Barcode-First Checkout

| Field | Detail |
|-------|--------|
| Description | The system shall support barcode-first checkout: scan-to-cart in < 1 s, with cart, line/order-level actions, and finalization in ≤ 3 steps for trained staff (BRD FR-POS-01, FR-PH-04). |
| Actors | UC-04, UC-02, UC-03 |
| Preconditions | Register open (REQ-POS-011); product barcodes indexed; stock available. |
| Postconditions | Sale posted: stock decremented, sales journal updated, receipt issued. |
| Main Flow | 1. Cashier scans/selects items. 2. System validates stock availability (BR-STK-02), price (BR-PRC-01), restricted flag (BR-SAL-06), expiry (BR-STK-04). 3. System applies discounts per policy (BR-SAL-02). 4. Cashier selects payment. 5. Tender + change. 6. Finalize → post stock + sales journal. 7. Issue receipt. |
| Alternative Flows | 2a. Insufficient stock → line flagged, quantity capped, user informed. 2b. Expired/quarantined batch → blocked unless override (REQ-INV-002). 2c. Restricted item → pharmacist approval (REQ-POS-009). 6a. Credit customer → credit decision (REQ-POS-010). |
| Business Rules | BR-SAL-01, BR-SAL-02, BR-SAL-06, BR-STK-02, BR-STK-04, BR-PRC-01, BR-TAX-01 |
| Validation Rules | No finalize with zero lines or unpriced line (BR-SAL-01); price from active list or approved override. |
| Error Conditions | ERR-POS-001-01: Zero lines → finalize blocked. ERR-POS-001-02: Unpriced line → blocked with prompt. ERR-POS-001-03: Stock insufficient → capped with message. |
| Priority / Estimate | Must / L |
| Dependencies | REQ-MED-002, REQ-INV-001, REQ-CMP-003 (currency/tax) |
| Acceptance Criteria | **AC-REQ-POS-001-01:** Scan-to-cart < 1 s; search < 2 s (FR-POS-01). **AC-REQ-POS-001-02:** Scan-and-sell completes in ≤ 3 steps, < 10 s for trained staff (FR-PH-04, NFR-N-02). **AC-REQ-POS-001-03:** Oversell and expired/quarantined lines blocked per rules. **AC-REQ-POS-001-04:** Sale posts stock + journal atomically. |
| Status | Draft |

#### REQ-POS-002 — Fast Search with Autocorrect

| Field | Detail |
|-------|--------|
| Description | The system shall provide fast product search with autocorrect, phonetic-tolerant Latin/Arabic input handling, and result ranking, resolving to product in < 2 s (FR-POS-01). |
| Actors | UC-04, UC-02 |
| Preconditions | Product index current. |
| Postconditions | User selects correct product; no typing of full drug names required. |
| Main Flow | 1. Type partial name/barcode. 2. System returns ranked results with autocorrect. 3. User selects. |
| Alternative Flows | 2a. No match → "create request / search national code" path. |
| Business Rules | BR-PRC-01, NFR-N-09 |
| Validation Rules | Search covers name, synonyms, national code, barcode. |
| Error Conditions | ERR-POS-002-01: Search > 2 s → performance bound. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-MED-001, REQ-MED-006 |
| Acceptance Criteria | **AC-REQ-POS-002-01:** Search results in < 2 s p95. **AC-REQ-POS-002-02:** Autocorrect handles common misspellings and Arabic/Latin mixed names (BR-LOC-03). |
| Status | Draft |

#### REQ-POS-003 — Cart with Line/Order Discounts

| Field | Detail |
|-------|--------|
| Description | The system shall support line- and order-level discounts per tenant policy; discount % above tenant maximum (default 10%) or above absolute amount requires manager override with reason (BR-SAL-02). |
| Actors | UC-04, UC-03, UC-02 |
| Preconditions | Cart non-empty; discount policy configured. |
| Postconditions | Discount applied/approved; recorded on receipt and audit. |
| Main Flow | 1. Apply discount. 2. System compares to thresholds. 3. Within limits → apply. 4. Above → manager override with reason. |
| Alternative Flows | 4a. No manager available → discount blocked, sale can proceed undiscounted. |
| Business Rules | BR-SAL-02, BR-SEC-03, BR-AUD-01 |
| Validation Rules | Discount never below configured floor; override logged. |
| Error Conditions | ERR-POS-003-01: Discount exceeds limit without approval → blocked. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-POS-001, REQ-SET-004 (policy) |
| Acceptance Criteria | **AC-REQ-POS-003-01:** Above-threshold discounts require manager override + reason (BR-SAL-02). **AC-REQ-POS-003-02:** Applied discounts appear on receipt and audit. |
| Status | Draft |

#### REQ-POS-004 — Cash/Card/QR/Mixed Payments with Tender

| Field | Detail |
|-------|--------|
| Description | The system shall support cash, card, QR, and mixed payments with tender entry, change calculation, and per-payment-type reconciliation feeding day-close (FR-POS-02, BR-CASH-01). Multi-currency handling per BR-CUR-01 where configured. |
| Actors | UC-04, UC-02 |
| Preconditions | Payment methods enabled per tenant/branch; register open. |
| Postconditions | Payment captured and reconciled per type; day-close variance logic applied later. |
| Main Flow | 1. Select payment type(s). 2. Enter tendered amount (cash) or authorize (card/QR via EXT-PAY). 3. System computes change. 4. Record per-type amounts. |
| Alternative Flows | 3a. Short tender → prompt. 4a. Card terminal offline → cash/QR fallback or hold per policy. |
| Business Rules | BR-CASH-01, BR-CUR-01, BR-TAX-01 |
| Validation Rules | Σ payment lines = sale total (within policy tolerance); currency conversion rates audited. |
| Error Conditions | ERR-POS-004-01: Payment total mismatch → blocked. ERR-POS-004-02: Unsupported currency → rejected. |
| Priority / Estimate | Must / L |
| Dependencies | REQ-CMP-003, EXT-PAY |
| Acceptance Criteria | **AC-REQ-POS-004-01:** Mixed payments supported with exact tender reconciliation. **AC-REQ-POS-004-02:** Cash variance logic feeds day-close (BR-CASH-01). **AC-REQ-POS-004-03:** Multi-currency captures applied rate (BR-CUR-01). |
| Status | Draft |

#### REQ-POS-005 — Receipts (Print/Email/QR) with Tax + Legal Footer

| Field | Detail |
|-------|--------|
| Description | The system shall generate receipts (print, email, QR) with tax detail and legal footer per the active market pack, in < 3 s (FR-POS-03, BR-TAX-01, BR-LOC-01). Digital receipts are additive (AS-08). |
| Actors | UC-04, UC-02 |
| Preconditions | Sale finalized; pack defines footer/tax format. |
| Postconditions | Receipt issued; (KSA) e-invoice path triggered per REQ-ACC-005. |
| Main Flow | 1. Finalize sale. 2. System renders receipt per pack template. 3. Print/email/QR per choice. |
| Alternative Flows | 3a. Printer offline → digital/QR fallback with reprint. 3b. E-invoicing market → transmission required before issue (BR-TAX-03). |
| Business Rules | BR-TAX-01, BR-TAX-03, BR-LOC-01, FR-POS-03 |
| Validation Rules | Tax lines reconcile to totals; legal footer from pack. |
| Error Conditions | ERR-POS-005-01: Receipt generation > 3 s → bound. ERR-POS-005-02: E-invoice transmission failure → issue blocked (BR-TAX-03). |
| Priority / Estimate | Must / M |
| Dependencies | REQ-CMP-001, REQ-ACC-005, EXT-RCP |
| Acceptance Criteria | **AC-REQ-POS-005-01:** Receipt generated < 3 s with tax detail + legal footer. **AC-REQ-POS-005-02:** E-invoicing market: invoice issued only after validated transmission (BR-TAX-03). |
| Status | Draft |

#### REQ-POS-006 — Returns/Refunds

| Field | Detail |
|-------|--------|
| Description | The system shall support returns/refunds referencing the original sale, with reason capture, stock re-admittance decision (restock/quarantine), refund per original payment method, and approval above threshold (FR-POS-04, BR-SAL-03/05). |
| Actors | UC-04, UC-03, UC-02, UC-06 |
| Preconditions | Original sale exists; item returnable per policy. |
| Postconditions | Return posted (stock + ledger reversal); refund/credit issued; audit preserved. |
| Main Flow | 1. Locate original sale. 2. Select return lines. 3. Capture reason + condition assessment. 4. Decide restock vs quarantine (BR-SAL-05). 5. Above threshold → manager approval. 6. Post reversal. 7. Issue refund/credit receipt. |
| Alternative Flows | 4a. Returned controlled substance → mandatory quarantine (BR-SAL-05). 5a. Threshold exceeded without approval → blocked. |
| Business Rules | BR-SAL-03, BR-SAL-05, BR-STK-02, BR-CTL-04, BR-ACC-01 |
| Validation Rules | Return must reference original sale; refund ≤ original amount per policy. |
| Error Conditions | ERR-POS-006-01: No original sale → blocked. ERR-POS-006-02: Refund above threshold without approval → blocked. |
| Priority / Estimate | Must / L |
| Dependencies | REQ-POS-001, REQ-ACC-001 |
| Acceptance Criteria | **AC-REQ-POS-006-01:** Every return links to the original transaction (BR-SAL-03). **AC-REQ-POS-006-02:** Controlled substances returned → quarantine (BR-SAL-05). **AC-REQ-POS-006-03:** Reversal posts balanced entries (BR-ACC-01). |
| Status | Draft |

#### REQ-POS-007 — Void with Reason Capture

| Field | Detail |
|-------|--------|
| Description | The system shall support voiding a sale or line with mandatory reason capture and original operator identity; voided transactions remain fully preserved in the audit trail (BR-SAL-04). |
| Actors | UC-04, UC-03 |
| Preconditions | Sale exists in audit trail. |
| Postconditions | Sale marked void; preserved immutably; stock/journal reversed. |
| Main Flow | 1. Select sale/line. 2. Capture reason. 3. Confirm void. 4. Post reversal + audit. |
| Alternative Flows | 3a. Privileged void per policy → approval/2FA (BR-SEC-03). |
| Business Rules | BR-SAL-04, BR-SEC-03, BR-AUD-01 |
| Validation Rules | Void preserves original record; reason mandatory. |
| Error Conditions | ERR-POS-007-01: Missing reason → blocked. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-POS-001 |
| Acceptance Criteria | **AC-REQ-POS-007-01:** Voided transactions preserved immutably with operator identity (BR-SAL-04). **AC-REQ-POS-007-02:** Reason mandatory. |
| Status | Draft |

#### REQ-POS-008 — Price Override with Approval

| Field | Detail |
|-------|--------|
| Description | The system shall support manual price override at POS; changes above threshold require approval and are logged (BR-PRC-01, BR-SEC-03). |
| Actors | UC-04, UC-03, UC-02 |
| Preconditions | Sale line exists. |
| Postconditions | Approved override applied and logged. |
| Main Flow | 1. Override price. 2. System compares to threshold. 3. Within → apply. 4. Above → approval. 5. Log. |
| Alternative Flows | 4a. Not approved → original price stands. |
| Business Rules | BR-PRC-01, BR-PRC-03, BR-SEC-03 |
| Validation Rules | Price ≥ 0; not below minimum margin without approval (if enabled). |
| Error Conditions | ERR-POS-008-01: Below minimum margin without approval → blocked. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-MED-005 |
| Acceptance Criteria | **AC-REQ-POS-008-01:** Overrides above threshold require approval + log. **AC-REQ-POS-008-02:** Overrides appear on audit trail. |
| Status | Draft |

#### REQ-POS-009 — Restricted-Product Pharmacist Approval

| Field | Detail |
|-------|--------|
| Description | The system shall block finalization of restricted-category lines until an authorized pharmacist records an approval event (BR-SAL-06, REQ-MED-008). |
| Actors | UC-04 (initiate), UC-02 (approve) |
| Preconditions | Line flagged restricted. |
| Postconditions | Sale finalizes only after pharmacist approval. |
| Main Flow | 1. Restricted line added. 2. System blocks finalize. 3. Pharmacist approves (identity + timestamp). 4. Finalize. |
| Alternative Flows | 3a. Approval declined → line removed. |
| Business Rules | BR-SAL-06, BR-SEC-03, BR-AUD-01 |
| Validation Rules | Approval event mandatory before finalize. |
| Error Conditions | ERR-POS-009-01: Finalize without approval → blocked. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-MED-008 |
| Acceptance Criteria | **AC-REQ-POS-009-01:** Restricted line cannot finalize without pharmacist approval. |
| Status | Draft |

#### REQ-POS-010 — Layaway / Credit Sale

| Field | Detail |
|-------|--------|
| Description | The system shall support layaway and credit sales for eligible customers per BR-CUST-01: credit decision (limit/aging) enforced at checkout; layaway tracking with deposit/balance (FR-POS-07). |
| Actors | UC-04, UC-06, UC-01 |
| Preconditions | Customer credit-enabled (REQ-CUS-002); credit policy configured. |
| Postconditions | Credit sale posted to AR; layaway tracked with payments. |
| Main Flow | 1. Select credit/layaway customer. 2. System checks credit limit + aging (BR-CUST-01). 3. Approve/block. 4. Post to AR. |
| Alternative Flows | 3a. Limit exceeded / overdue → blocked; alternative payment offered. |
| Business Rules | BR-CUST-01, BR-CUST-02, BR-ACC-01 |
| Validation Rules | No credit sale without available limit and clean aging status. |
| Error Conditions | ERR-POS-010-01: Overdue customer → credit blocked. |
| Priority / Estimate | Must / S |
| Dependencies | REQ-CUS-002 |
| Acceptance Criteria | **AC-REQ-POS-010-01:** Credit decision enforced at checkout (BR-CUST-01). **AC-REQ-POS-010-02:** Credit sale posts to AR with audit. |
| Status | Draft |

#### REQ-POS-011 — Register/Drawer Shift Management

| Field | Detail |
|-------|--------|
| Description | The system shall support register/drawer open-close (shift) events with operator attribution and per-shift sales, feeding day-close (FR-PH-03, P09). |
| Actors | UC-04, UC-03 |
| Preconditions | User assigned to register; branch open. |
| Postconditions | Open/close events logged; shift sales reconciled at close. |
| Main Flow | 1. Open register (operator attributed). 2. Process sales. 3. Close register with declared cash. 4. System records variance for day-close. |
| Alternative Flows | 3a. Variance → reason + approval per BR-CASH-01. |
| Business Rules | FR-PH-03, BR-CASH-01/02 |
| Validation Rules | Register events time-stamped and operator-attributed. |
| Error Conditions | ERR-POS-011-01: Double open → blocked. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-USR-001 |
| Acceptance Criteria | **AC-REQ-POS-011-01:** Open/close logged with operator + timestamp. **AC-REQ-POS-011-02:** Shift sales roll into day-close. |
| Status | Draft |

#### REQ-POS-012 — Active-Transaction Resilience

| Field | Detail |
|-------|--------|
| Description | The system shall survive brief connectivity loss (30 s) without losing or corrupting the active transaction; the sale completes on reconnect with no silent data loss (FR-PH-05, NFR-N-08). |
| Actors | UC-04, System |
| Preconditions | POS session active. |
| Postconditions | No transaction loss/corruption; recovery transparent to operator. |
| Main Flow | 1. Transaction in progress. 2. Connectivity lost ≤ 30 s. 3. System buffers transaction locally. 4. Reconnect → commit; reconcile. |
| Alternative Flows | 2a. Outage > 30 s → explicit operator prompt; no silent partial commit (NFR-N-08). |
| Business Rules | NFR-N-08, BR-AUD-01 |
| Validation Rules | No silent data loss; recovery integrity verified. |
| Error Conditions | ERR-POS-012-01: Partial commit risk → transaction held, user notified. |
| Priority / Estimate | Must / L |
| Dependencies | Platform resilience layer |
| Acceptance Criteria | **AC-REQ-POS-012-01:** Active sale survives 30 s outage and completes on reconnect (FR-PH-05). **AC-REQ-POS-012-02:** No silent data loss or duplicate posting. |
| Status | Draft |

---

## 3.5 MOD-05 — Sales Management

### 3.5.1 Module Overview

| Attribute | Detail |
|-----------|--------|
| Module Name | Sales Management |
| Business Goal | Provide post-sale sales intelligence and control: full sales journal, margin analytics, layaway lifecycle, returns/refunds management, and prevention of under-reporting through day-close reconciliation (BRD P01/P03/P09). |
| Description | Complements the POS by managing sales history, margin, layaway, returns, and promotions. Ensures every sale is captured, posted, and reconciled (KPI-17). |
| Business Value | Identifies which products actually make money (P-01); guarantees sales capture (KPI-17); manages credit/layaway lifecycle; supports promotions (V2). |
| Target Users | UC-01, UC-03, UC-06, UC-07 |
| Dependencies | POS, ACC, CUS, INV |
| Priority | Must (journal/margin/returns), Could (promotions) |
| Source / Trace | BRD FR-POS-04/07, FR-REP-01 ext., P03/P09, BR-SAL-03..05, BR-CASH-01, BR-ACC-01 |

### 3.5.2 Requirements Catalog

| ID | Requirement | Priority | Estimate | Dependencies | BRD Trace |
|----|-------------|----------|----------|--------------|-----------|
| REQ-SAL-001 | Sales Journal & Transaction History | Must | M | POS | P01/P03, BR-AUD-01 |
| REQ-SAL-002 | Sales Margin by Product Report | Must | M | ACC (FIFO) | FR-REP-01 ext., BR-ACC-04 |
| REQ-SAL-003 | Layaway Management | Should | M | CUS-002, POS-010 | FR-POS-07, P16 |
| REQ-SAL-004 | Promotions Engine | Could | L | POS-003 | BRD §17.3, Roadmap V2 |
| REQ-SAL-005 | Return & Refund Management | Must | M | POS-006 | P03, BR-SAL-03/05 |
| REQ-SAL-006 | Day-Close Reconciliation Support (anti under-reporting) | Must | M | POS-004, ACC | BR-CASH-01, KPI-17 |

### 3.5.3 Detailed Requirements

#### REQ-SAL-001 — Sales Journal & Transaction History

| Field | Detail |
|-------|--------|
| Description | The system shall maintain a complete, searchable sales journal (all finalized, voided, and returned transactions) with line-level detail, operator, branch, and payment breakdown (P01/P03 outputs, BR-AUD-01). |
| Actors | UC-01, UC-03, UC-06, UC-07 |
| Preconditions | Sales posted. |
| Postconditions | Journal queryable; voided/returned entries visible with status. |
| Main Flow | 1. Query journal by date/branch/operator/status. 2. System returns entries. 3. Drill into transaction lines. |
| Alternative Flows | 1a. Filter by void/return status. |
| Business Rules | BR-AUD-01, BR-REP-01 |
| Validation Rules | Voided/returned records never removed; totals reconcile to reports. |
| Error Conditions | ERR-SAL-001-01: Query > 2 s at 90-day scale → bound. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-POS-001, REQ-POS-007 |
| Acceptance Criteria | **AC-REQ-SAL-001-01:** All transactions incl. void/return appear in journal. **AC-REQ-SAL-001-02:** Journal reconciles to day-close totals (0 variance). |
| Status | Draft |

#### REQ-SAL-002 — Sales Margin by Product Report

| Field | Detail |
|-------|--------|
| Description | The system shall report sales margin by product using FIFO cost valuation, with filters (date/branch/category), reconciling to the ledger (FR-REP-01 ext., BR-ACC-04). |
| Actors | UC-01, UC-06, UC-07 |
| Preconditions | COGS posted (REQ-INV-011). |
| Postconditions | Margin report available for purchase/price decisions. |
| Main Flow | 1. Select period/branch/category. 2. System computes revenue − COGS per product. 3. Render/export. |
| Alternative Flows | 1a. Lines missing cost → flagged with count. |
| Business Rules | BR-ACC-04, BR-REP-01/02 |
| Validation Rules | Report reconciles to ledger; zero unexplained drift. |
| Error Conditions | ERR-SAL-002-01: Reconciliation mismatch → export blocked. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-INV-011, REQ-RPT-001 |
| Acceptance Criteria | **AC-REQ-SAL-002-01:** Margin reconciles to ledger to 0 drift. **AC-REQ-SAL-002-02:** Missing-cost lines flagged. |
| Status | Draft |

#### REQ-SAL-003 — Layaway Management

| Field | Detail |
|-------|--------|
| Description | The system shall manage layaway: create with deposit, track balance, payments, expiry/pickup, cancellation, and refund per policy (FR-POS-07, P16). |
| Actors | UC-04, UC-03, UC-06 |
| Preconditions | Customer record exists (REQ-CUS-001). |
| Postconditions | Layaway lifecycle tracked and audited. |
| Main Flow | 1. Create layaway with deposit. 2. Payments applied. 3. Balance tracked. 4. Pickup or cancel. |
| Alternative Flows | 4a. Cancel → refund per policy; stock released. |
| Business Rules | BR-CUST-01, BR-AUD-01, BR-ACC-01 |
| Validation Rules | Payments post to AR/ledger correctly. |
| Error Conditions | ERR-SAL-003-01: Cancel with outstanding balance → approval required. |
| Priority / Estimate | Should / M |
| Dependencies | REQ-CUS-001, REQ-POS-010 |
| Acceptance Criteria | **AC-REQ-SAL-003-01:** Layaway balance/payments tracked and audited. **AC-REQ-SAL-003-02:** Cancellation follows policy with refund handling. |
| Status | Draft |

#### REQ-SAL-004 — Promotions Engine (V2)

| Field | Detail |
|-------|--------|
| Description | (V2) The system shall support a promotions engine (multi-buy, percentage off, free-item) beyond standard discount rules, with policy limits and audit (BRD §17.3, Roadmap V2). |
| Actors | UC-01, UC-03 |
| Preconditions | V2 release. |
| Postconditions | Promotions applied at POS within policy. |
| Main Flow | 1. Define promotion. 2. Activate by date/branch. 3. POS applies. |
| Alternative Flows | 3a. Conflict with discount policy → resolution precedence. |
| Business Rules | BR-SAL-02 |
| Validation Rules | Promotions never exceed configured floors. |
| Error Conditions | ERR-SAL-004-01: Invalid combination → blocked. |
| Priority / Estimate | Could / L |
| Dependencies | REQ-POS-003 |
| Acceptance Criteria | **AC-REQ-SAL-004-01 (V2):** Promotions applied within policy limits; audited. |
| Status | Deferred |

#### REQ-SAL-005 — Return & Refund Management

| Field | Detail |
|-------|--------|
| Description | The system shall manage returns/refunds across the tenant: original-sale linkage, reason capture, condition-based restock/quarantine, manager approvals above threshold, and ledger reversal (P03, BR-SAL-03/05). |
| Actors | UC-03, UC-06, UC-02 |
| Preconditions | Returns posted from POS (REQ-POS-006). |
| Postconditions | Return register complete; approvals tracked. |
| Main Flow | 1. List/query returns. 2. View linkage to original sale. 3. Approve/review. 4. Export to ACC. |
| Alternative Flows | 2a. Unmatched return → flagged for investigation. |
| Business Rules | BR-SAL-03, BR-SAL-05, BR-ACC-01 |
| Validation Rules | Every return references an original sale. |
| Error Conditions | ERR-SAL-005-01: Orphan return detected → alert. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-POS-006 |
| Acceptance Criteria | **AC-REQ-SAL-005-01:** Return register complete and linked to originals. **AC-REQ-SAL-005-02:** Approval workflow enforced. |
| Status | Draft |

#### REQ-SAL-006 — Day-Close Reconciliation Support

| Field | Detail |
|-------|--------|
| Description | The system shall reconcile expected sales per payment type against declared cash at day-close, requiring documented resolution (and approval above threshold) for variances, ensuring 100% sales capture (BR-CASH-01, KPI-17). |
| Actors | UC-03, UC-06 |
| Preconditions | Register closed; sales posted. |
| Postconditions | Day locked; variance resolved; ledger posted. |
| Main Flow | 1. Compute expected per payment type. 2. Enter declared cash. 3. Compute variance. 4. Resolve with reason; approve above threshold. 5. Lock day; post ledger. |
| Alternative Flows | 4a. Unresolved variance → day remains open; alert. 5a. Post-close correction → manager-authorized re-open with audit (BR-CASH-02). |
| Business Rules | BR-CASH-01, BR-CASH-02, BR-ACC-01/02/03 |
| Validation Rules | Day closes once; re-open audited. |
| Error Conditions | ERR-SAL-006-01: Variance unresolved → lock blocked. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-POS-004, REQ-ACC-001 |
| Acceptance Criteria | **AC-REQ-SAL-006-01:** Day-close reconciles per payment type; variance resolution documented (BR-CASH-01). **AC-REQ-SAL-006-02:** Post-close changes require audited re-open (BR-CASH-02). |
| Status | Draft |

---

## 3.6 MOD-06 — Purchasing

### 3.6.1 Module Overview

| Attribute | Detail |
|-----------|--------|
| Module Name | Purchasing |
| Business Goal | Convert demand signals into controlled, traceable supplier orders: POs with approvals, goods receipt with batch/expiry/variance/backorder handling, and purchase returns/claims (BRD P04/P05/P06). |
| Description | Purchasing connects reorder intelligence to supplier commitments and receiving. It enforces authorization limits, order/receipt variance controls, and cost/landed-cost recording. |
| Business Value | Right stock at right cost with low expiry write-offs; higher supplier fill-rates; cost control (BR-PUR-01..05); basis of supplier scorecards. |
| Target Users | UC-05, UC-01, UC-03 |
| Dependencies | INV, SUP, MED, ACC |
| Priority | Must |
| Source / Trace | BRD FR-PUR-01..03, P04/P05/P06, BR-PUR-01..05, BR-STK-05, BR-SUP-03/05 |

### 3.6.2 Requirements Catalog

| ID | Requirement | Priority | Estimate | Dependencies | BRD Trace |
|----|-------------|----------|----------|--------------|-----------|
| REQ-PUR-001 | Purchase Order Creation with Approval Workflow | Must | L | SUP-001, INV-004 | FR-PUR-01, BR-PUR-01/03 |
| REQ-PUR-002 | Goods Receipt (GRN) with Batch/Expiry/Variance/Backorder | Must | XL | INV-001, MED-003 | FR-PUR-02, BR-STK-05, BR-PUR-02/05 |
| REQ-PUR-003 | Purchase Returns & Credit-Note Claims | Must | L | PUR-002, SUP-004 | FR-PUR-03, BR-SUP-03/05 |
| REQ-PUR-004 | Purchase Suggestion List (from Reorder) | Must | M | INV-004 | FR-INV-03, BR-PUR-04 |
| REQ-PUR-005 | PO Status Tracking | Must | M | PUR-001 | P04 |
| REQ-PUR-006 | PO Dispatch to Supplier (Print/Email) | Must | S | PUR-001 | AS-09, P04 |
| REQ-PUR-007 | Backordering | Must | M | PUR-002 | FR-PUR-02, BR-STK-05 |

### 3.6.3 Detailed Requirements

#### REQ-PUR-001 — Purchase Order Creation with Approval Workflow

| Field | Detail |
|-------|--------|
| Description | The system shall create POs with approved supplier, expected date, line-level items with quantity and agreed price; PO creation above the tenant authorization limit requires a second authorized user's approval (BR-PUR-01/03). |
| Actors | UC-05, UC-01 |
| Preconditions | Supplier approved (REQ-SUP-001); authorization limits configured (REQ-SET-004); product exists. |
| Postconditions | PO issued (status), approved per limits, available for dispatch. |
| Main Flow | 1. Create PO (from suggestions or manual). 2. Select supplier; validate onboarding + credit terms (BR-SUP-01/04). 3. Add lines with qty/price/expected date. 4. Validate against limits. 5. Submit → approval if above limit. 6. Issue PO. |
| Alternative Flows | 5a. Above limit → routed for second approval; not issued until approved. 3a. Blocked supplier → approval required (BR-SUP-04). |
| Business Rules | BR-PUR-01, BR-PUR-03, BR-SUP-01, BR-SUP-04, BR-AUTH-01 |
| Validation Rules | PO must have approved supplier + expected date + line-level price/qty before issue (BR-PUR-01). |
| Error Conditions | ERR-PUR-001-01: No approved supplier → blocked. ERR-PUR-001-02: Above limit without approval → not issued. |
| Priority / Estimate | Must / L |
| Dependencies | REQ-SUP-001, REQ-INV-004, REQ-SET-004 |
| Acceptance Criteria | **AC-REQ-PUR-001-01:** PO create ≤ 5 min (FR-PUR-01). **AC-REQ-PUR-001-02:** Approval enforced by authorization limit (BR-PUR-03). **AC-REQ-PUR-001-03:** Only approved suppliers receive POs (BR-SUP-01). |
| Status | Draft |

#### REQ-PUR-002 — Goods Receipt (GRN) with Batch/Expiry/Variance/Backorder

| Field | Detail |
|-------|--------|
| Description | The system shall record goods receipt against a PO with batch/lot + expiry capture (BR-STK-01), quantity/price variance handling (BR-STK-05), over-receipt tolerance approval (default 2%), backorder creation, and posting of stock and payables (BR-PUR-02). |
| Actors | UC-05, UC-03, UC-02 (QC) |
| Preconditions | Open PO; delivery note matched. |
| Postconditions | Stock updated at batch level; variance documented; payables updated; backorders created where applicable. |
| Main Flow | 1. Select open PO. 2. Enter received quantities/batches/expiry. 3. Quality check. 4. Compare to PO (shortage/overage/price change). 5. Within tolerance → accept. 6. Beyond tolerance → approval. 7. Post stock + payables; create backorder if applicable. |
| Alternative Flows | 4a. Shortage → variance reason + backorder option (BR-STK-05). 4b. Overage beyond 2% → manager approval (BR-STK-05). 5a. Rejected lines → supplier return flow (REQ-PUR-003). |
| Business Rules | BR-STK-01, BR-STK-02, BR-STK-05, BR-PUR-02, BR-PUR-05, BR-SUP-02, BR-ACC-01 |
| Validation Rules | Cost/price per PO unless variance approved (BR-PUR-02); receipt cannot exceed ordered without approval (BR-PUR-05). |
| Error Conditions | ERR-PUR-002-01: Batch-class product without batch/expiry → blocked (BR-STK-01). ERR-PUR-002-02: Over-receipt without approval → blocked. |
| Priority / Estimate | Must / XL |
| Dependencies | REQ-INV-001, REQ-MED-003, REQ-PUR-001 |
| Acceptance Criteria | **AC-REQ-PUR-002-01:** GRN posts batch-level stock + payables atomically. **AC-REQ-PUR-002-02:** Variances recorded with reason; backorder created on shortage (BR-STK-05). **AC-REQ-PUR-002-03:** Over-receipt beyond 2% requires approval (BR-PUR-05). |
| Status | Draft |

#### REQ-PUR-003 — Purchase Returns & Credit-Note Claims

| Field | Detail |
|-------|--------|
| Description | The system shall support supplier returns referencing the original purchase/GRN, generating a claim awaiting supplier credit note, with aging and reconciliation (FR-PUR-03, BR-SUP-03/05). |
| Actors | UC-05, UC-06 |
| Preconditions | Returnable stock identified (expiry/damage/recall/wrong supply). |
| Postconditions | Return posted; claim tracked; credit note reconciled; payables adjusted. |
| Main Flow | 1. Create supplier return referencing GRN. 2. Capture reason + evidence. 3. Supplier authorization (if required). 4. Dispatch goods. 5. Await credit note. 6. Reconcile credit note to claim. 7. Post payables adjustment. |
| Alternative Flows | 6a. Credit note partial/mismatch → variance handling + escalation. 7a. Uncollected > 90 days → aging report (BR-SUP-05). |
| Business Rules | BR-SUP-03, BR-SUP-05, BR-STK-02, BR-ACC-01 |
| Validation Rules | Return references original purchase/GRN (BR-SUP-03). |
| Error Conditions | ERR-PUR-003-01: No original GRN reference → blocked. |
| Priority / Estimate | Must / L |
| Dependencies | REQ-PUR-002, REQ-SUP-004 |
| Acceptance Criteria | **AC-REQ-PUR-003-01:** Every claim references original GRN (BR-SUP-03). **AC-REQ-PUR-003-02:** Claims > 90 days appear on aging report (BR-SUP-05). |
| Status | Draft |

#### REQ-PUR-004 — Purchase Suggestion List

| Field | Detail |
|-------|--------|
| Description | The system shall present reorder suggestions (REQ-INV-004) as a purchase suggestion list for conversion into POs; no auto-PO creation (BR-PUR-04). |
| Actors | UC-05, UC-01 |
| Preconditions | Suggestions generated. |
| Postconditions | User can convert selected suggestions to PO draft. |
| Main Flow | 1. Open suggestion list. 2. Review. 3. Select → create PO draft. |
| Alternative Flows | 2a. Exclude items. |
| Business Rules | BR-PUR-04 |
| Validation Rules | PO creation requires human confirmation. |
| Error Conditions | ERR-PUR-004-01: No suggestions → empty-state. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-INV-004 |
| Acceptance Criteria | **AC-REQ-PUR-004-01:** Suggestions convert to PO only via explicit user action. |
| Status | Draft |

#### REQ-PUR-005 — PO Status Tracking

| Field | Detail |
|-------|--------|
| Description | The system shall track PO lifecycle status (draft, pending approval, issued, partially received, fully received, closed, cancelled) with timestamps (P04). |
| Actors | UC-05, UC-01 |
| Preconditions | PO exists. |
| Postconditions | Status current and auditable. |
| Main Flow | 1. PO created → draft. 2. Approval → issued. 3. Receipts → received. 4. Close/cancel. |
| Alternative Flows | 4a. Cancel issued PO → reason + approval if received lines exist. |
| Business Rules | BR-AUD-01, BR-PUR-01 |
| Validation Rules | Status transitions valid; history retained. |
| Error Conditions | ERR-PUR-005-01: Invalid transition → rejected. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-PUR-001 |
| Acceptance Criteria | **AC-REQ-PUR-005-01:** Status transitions recorded with audit. |
| Status | Draft |

#### REQ-PUR-006 — PO Dispatch to Supplier (Print/Email)

| Field | Detail |
|-------|--------|
| Description | The system shall dispatch issued POs to suppliers by print or email (integration later) (AS-09). |
| Actors | UC-05 |
| Preconditions | PO issued. |
| Postconditions | Dispatch recorded; supplier acknowledged (optional). |
| Main Flow | 1. Select PO. 2. Print/email. 3. Record dispatch. |
| Alternative Flows | 3a. Email failure → retry/fallback print. |
| Business Rules | AS-09 |
| Validation Rules | Dispatch event audited. |
| Error Conditions | ERR-PUR-006-01: No contact configured → print-only path. |
| Priority / Estimate | Must / S |
| Dependencies | REQ-PUR-001, EXT-EMAIL |
| Acceptance Criteria | **AC-REQ-PUR-006-01:** PO dispatch via print/email recorded. |
| Status | Draft |

#### REQ-PUR-007 — Backordering

| Field | Detail |
|-------|--------|
| Description | The system shall create and track backorders for short-received PO lines, with follow-up and cancellation handling (FR-PUR-02, BR-STK-05). |
| Actors | UC-05 |
| Preconditions | Shortage recorded at GRN. |
| Postconditions | Backorder tracked until fulfilled/cancelled. |
| Main Flow | 1. GRN shortage. 2. Create backorder. 3. Track. 4. Fulfill on next receipt or cancel. |
| Alternative Flows | 4a. Cancel → reason + audit. |
| Business Rules | BR-STK-05 |
| Validation Rules | Backorder quantities consistent with shortage. |
| Error Conditions | ERR-PUR-007-01: Backorder exceeds shortage → blocked. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-PUR-002 |
| Acceptance Criteria | **AC-REQ-PUR-007-01:** Backorders created on shortage and tracked to resolution. |
| Status | Draft |

---

## 3.7 MOD-07 — Suppliers

### 3.7.1 Module Overview

| Attribute | Detail |
|-----------|--------|
| Module Name | Suppliers |
| Business Goal | Maintain a trusted supplier base with onboarding, terms, credit configuration, performance scorecards, and claims handling (BRD P04/P06, FR-PUR-04/05). |
| Description | The supplier master governs who can receive POs, what terms apply, and how performance is scored from goods-receipt and returns events. |
| Business Value | Better supplier terms (P-01/P-05), higher fill-rates, claims recovery (OP-02); basis of purchasing decisions. |
| Target Users | UC-05, UC-06, UC-01 |
| Dependencies | PUR, ACC |
| Priority | Must |
| Source / Trace | BRD FR-PUR-04/05, P04/P06, BR-SUP-01..05 |

### 3.7.2 Requirements Catalog

| ID | Requirement | Priority | Estimate | Dependencies | BRD Trace |
|----|-------------|----------|----------|--------------|-----------|
| REQ-SUP-001 | Supplier Master with Onboarding Status | Must | M | USR | FR-PUR-05, BR-SUP-01 |
| REQ-SUP-002 | Supplier Terms & Credit Configuration | Must | M | SUP-001 | BR-SUP-04 |
| REQ-SUP-003 | Supplier Performance Scorecards | Must | M | PUR-002, PUR-003 | FR-PUR-04, BR-SUP-02 |
| REQ-SUP-004 | Supplier Returns & Claims Aging | Must | M | PUR-003 | FR-PUR-03, BR-SUP-03/05 |
| REQ-SUP-005 | Supplier Order History | Should | S | PUR-001 | P04 |
| REQ-SUP-006 | Supplier Credit-Note Reconciliation | Must | M | PUR-003 | P06, BR-SUP-03 |

### 3.7.3 Detailed Requirements

#### REQ-SUP-001 — Supplier Master with Onboarding Status

| Field | Detail |
|-------|--------|
| Description | The system shall maintain a supplier master with onboarding status (prospect → approved → blocked), contact data, and only approved suppliers may receive POs (BR-SUP-01). |
| Actors | UC-05, UC-08 |
| Preconditions | Tenant configured. |
| Postconditions | Supplier lifecycle managed and audited. |
| Main Flow | 1. Create supplier. 2. Complete onboarding data. 3. Approve. 4. Use in POs. |
| Alternative Flows | 4a. Blocked supplier → PO blocked or approval-required (BR-SUP-04). |
| Business Rules | BR-SUP-01, BR-SUP-04, BR-AUD-01 |
| Validation Rules | Only approved suppliers receive POs. |
| Error Conditions | ERR-SUP-001-01: PO with unapproved supplier → blocked (BR-SUP-01). |
| Priority / Estimate | Must / M |
| Dependencies | REQ-USR-001 |
| Acceptance Criteria | **AC-REQ-SUP-001-01:** Supplier lifecycle enforced (BR-SUP-01). **AC-REQ-SUP-001-02:** Changes audited. |
| Status | Draft |

#### REQ-SUP-002 — Supplier Terms & Credit Configuration

| Field | Detail |
|-------|--------|
| Description | The system shall configure supplier payment terms (payment days, credit limit) and enforce them at PO creation; blocked suppliers require approval (BR-SUP-04). |
| Actors | UC-05, UC-06 |
| Preconditions | Supplier approved. |
| Postconditions | Terms applied to POs. |
| Main Flow | 1. Configure terms/limits. 2. PO creation validates terms. |
| Alternative Flows | 2a. Blocked/limit-exceeded → approval path. |
| Business Rules | BR-SUP-04 |
| Validation Rules | Terms enforced at PO creation. |
| Error Conditions | ERR-SUP-002-01: Exceeds credit limit → blocked/approval. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-SUP-001 |
| Acceptance Criteria | **AC-REQ-SUP-002-01:** Supplier credit terms enforced at PO creation (BR-SUP-04). |
| Status | Draft |

#### REQ-SUP-003 — Supplier Performance Scorecards

| Field | Detail |
|-------|--------|
| Description | The system shall score supplier performance (fill rate, on-time, quality) automatically from goods receipt and returns events (FR-PUR-04, BR-SUP-02). |
| Actors | UC-05, UC-01 |
| Preconditions | Receipt/returns events present. |
| Postconditions | Scorecards current and available for decisions. |
| Main Flow | 1. Events feed scoring. 2. Compute metrics. 3. Render scorecard. |
| Alternative Flows | 1a. Insufficient events → "insufficient data" state. |
| Business Rules | BR-SUP-02 |
| Validation Rules | Scores computed from events only. |
| Error Conditions | ERR-SUP-003-01: No events → not scored. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-PUR-002, REQ-PUR-003 |
| Acceptance Criteria | **AC-REQ-SUP-003-01:** Scores computed automatically from receipt/returns events. |
| Status | Draft |

#### REQ-SUP-004 — Supplier Returns & Claims Aging

| Field | Detail |
|-------|--------|
| Description | The system shall track supplier returns/claims and age them; uncollected credit notes older than 90 days must appear on the aging report (BR-SUP-05). |
| Actors | UC-05, UC-06 |
| Preconditions | Claims created (REQ-PUR-003). |
| Postconditions | Aging report current. |
| Main Flow | 1. Claims tracked. 2. Age computed. 3. Report lists > 90-day items. |
| Alternative Flows | 3a. Escalation action → notified. |
| Business Rules | BR-SUP-05 |
| Validation Rules | Aging computed from credit-note reconciliation dates. |
| Error Conditions | ERR-SUP-004-01: None. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-PUR-003 |
| Acceptance Criteria | **AC-REQ-SUP-004-01:** Credit notes > 90 days uncollected appear on aging report (BR-SUP-05). |
| Status | Draft |

#### REQ-SUP-005 — Supplier Order History

| Field | Detail |
|-------|--------|
| Description | The system shall present full order history per supplier (POs, receipts, returns, credit notes) (P04). |
| Actors | UC-05, UC-01 |
| Preconditions | Order data present. |
| Postconditions | History viewable. |
| Main Flow | 1. Open supplier. 2. View history. |
| Alternative Flows | None. |
| Business Rules | BR-REP-01 |
| Validation Rules | History from posted data. |
| Error Conditions | ERR-SUP-005-01: None. |
| Priority / Estimate | Should / S |
| Dependencies | REQ-PUR-001 |
| Acceptance Criteria | **AC-REQ-SUP-005-01:** Order history reconciles to posted data. |
| Status | Draft |

#### REQ-SUP-006 — Supplier Credit-Note Reconciliation

| Field | Detail |
|-------|--------|
| Description | The system shall reconcile received supplier credit notes to open claims and post payables adjustments, with variance handling (P06, BR-SUP-03). |
| Actors | UC-06 |
| Preconditions | Claim open; credit note received. |
| Postconditions | Claim reconciled; payables adjusted. |
| Main Flow | 1. Enter credit note. 2. Match to claim. 3. Variance handling. 4. Post payables adjustment. |
| Alternative Flows | 3a. Partial mismatch → variance flag + escalation. |
| Business Rules | BR-SUP-03, BR-ACC-01 |
| Validation Rules | Reconciliation balances; posting balanced. |
| Error Conditions | ERR-SUP-006-01: Unbalanced → blocked. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-PUR-003 |
| Acceptance Criteria | **AC-REQ-SUP-006-01:** Credit notes reconciled to claims; payables adjusted with audit. |
| Status | Draft |

---

## 3.8 MOD-08 — Customers

### 3.8.1 Module Overview

| Attribute | Detail |
|-----------|--------|
| Module Name | Customers |
| Business Goal | Manage customers (walk-in profiles, credit customers, loyalty members) and privacy-scoped patient records, driving credit control, loyalty, and statements (BRD P16, FR-CUST-01..03). |
| Description | Customer master with consent records, credit profiles (limits/aging/blocking), loyalty (earn/redeem), statements, and patient minimal profiles for prescription linkage. |
| Business Value | Credit-sales control reduces bad debt (BR-CUST-01); loyalty raises retention and ARPU (OP-09); statements build trust. |
| Target Users | UC-04, UC-06, UC-01 |
| Dependencies | POS, ACC, PRIV (CMP) |
| Priority | Must (core), Should (statements automation) |
| Source / Trace | BRD FR-CUST-01..03, P16, BR-CUST-01..03, BR-LOY-01, BR-PRIV-01 |

### 3.8.2 Requirements Catalog

| ID | Requirement | Priority | Estimate | Dependencies | BRD Trace |
|----|-------------|----------|----------|--------------|-----------|
| REQ-CUS-001 | Customer Master (Privacy-Scoped) | Must | M | CMP (privacy) | FR-CUST-01, BR-PRIV-01 |
| REQ-CUS-002 | Credit Customers (Limits/Aging/Block) | Must | L | CUS-001, ACC | FR-CUST-02, BR-CUST-01/02 |
| REQ-CUS-003 | Loyalty Program | Must | M | CUS-001 | FR-CUST-03, BR-LOY-01 |
| REQ-CUS-004 | Customer Statements | Should | M | CUS-002 | FR-CUST-02, BR-CUST-03 |
| REQ-CUS-005 | Patient Minimal Profile (Rx-Linked) | Must | M | RX, CMP (privacy) | FR-RX-01, BR-PRIV-01 |
| REQ-CUS-006 | Consent / Opt-In Management | Must | S | CUS-001 | FR-CUST-01, BR-PRIV-01, NFR-N-06 |

### 3.8.3 Detailed Requirements

#### REQ-CUS-001 — Customer Master (Privacy-Scoped)

| Field | Detail |
|-------|--------|
| Description | The system shall maintain a customer master (walk-in profile, loyalty opt-in, credit profile) with privacy-scoped fields; customer lookup < 2 s; consent recorded (FR-CUST-01). |
| Actors | UC-04, UC-06 |
| Preconditions | Tenant configured. |
| Postconditions | Customer record searchable; consent recorded. |
| Main Flow | 1. Create/lookup customer. 2. Record consent/opt-in. 3. Save. |
| Alternative Flows | 1a. Walk-in without profile → anonymous sale allowed. |
| Business Rules | BR-PRIV-01, BR-AUD-01, NFR-N-06 |
| Validation Rules | Consent recorded for any marketing use; minimal data principle. |
| Error Conditions | ERR-CUS-001-01: Lookup > 2 s → bound. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-CMP-004 (privacy regime) |
| Acceptance Criteria | **AC-REQ-CUS-001-01:** Customer lookup < 2 s. **AC-REQ-CUS-001-02:** Consent recorded and audited. |
| Status | Draft |

#### REQ-CUS-002 — Credit Customers (Limits/Aging/Block)

| Field | Detail |
|-------|--------|
| Description | The system shall support credit-enabled customers with limits, aging, blocking, and statements; credit sales only when available limit and no overdue balance beyond threshold (BR-CUST-01); posting to AR with audit (BR-CUST-02). |
| Actors | UC-04, UC-06, UC-01 |
| Preconditions | Customer credit profile configured. |
| Postconditions | Credit decisions enforced; AR accurate. |
| Main Flow | 1. Configure credit profile. 2. Sale-time decision (REQ-POS-010). 3. Post AR. 4. Payment allocation. 5. Statement. |
| Alternative Flows | 2a. Limit exceeded / overdue → block. |
| Business Rules | BR-CUST-01, BR-CUST-02, BR-CUST-03 |
| Validation Rules | Credit sale requires available limit and clean aging. |
| Error Conditions | ERR-CUS-002-01: Overdue → blocked. |
| Priority / Estimate | Must / L |
| Dependencies | REQ-CUS-001, REQ-ACC-001 |
| Acceptance Criteria | **AC-REQ-CUS-002-01:** Credit decisions enforced (BR-CUST-01). **AC-REQ-CUS-002-02:** AR postings audited (BR-CUST-02). |
| Status | Draft |

#### REQ-CUS-003 — Loyalty Program

| Field | Detail |
|-------|--------|
| Description | The system shall support loyalty points (earn/redeem/expire) per tenant policy, with redemption limits and auditable point transactions (BR-LOY-01). |
| Actors | UC-04, UC-06, UC-01 |
| Preconditions | Loyalty policy configured; customer opted in. |
| Postconditions | Points ledger consistent. |
| Main Flow | 1. Earn points on sale. 2. Redeem within limits. 3. Expire per policy. 4. Ledger updated. |
| Alternative Flows | 2a. Redemption limit exceeded → blocked. |
| Business Rules | BR-LOY-01 |
| Validation Rules | Points ledger consistent; transactions auditable. |
| Error Conditions | ERR-CUS-003-01: Redemption beyond limit → blocked. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-CUS-001 |
| Acceptance Criteria | **AC-REQ-CUS-003-01:** Points accrue/redeem per policy with audit. |
| Status | Draft |

#### REQ-CUS-004 — Customer Statements

| Field | Detail |
|-------|--------|
| Description | The system shall generate customer statements reflecting all invoices, payments, and credit notes within the period (BR-CUST-03). |
| Actors | UC-06 |
| Preconditions | AR data present. |
| Postconditions | Statement generated/exported. |
| Main Flow | 1. Select customer/period. 2. Generate. 3. Export/send. |
| Alternative Flows | 3a. Email delivery via EXT-EMAIL. |
| Business Rules | BR-CUST-03 |
| Validation Rules | Statement balances to AR ledger. |
| Error Conditions | ERR-CUS-004-01: Mismatch → export blocked. |
| Priority / Estimate | Should / M |
| Dependencies | REQ-CUS-002 |
| Acceptance Criteria | **AC-REQ-CUS-004-01:** Statements reflect all invoices/payments/credit notes (BR-CUST-03). |
| Status | Draft |

#### REQ-CUS-005 — Patient Minimal Profile (Rx-Linked)

| Field | Detail |
|-------|--------|
| Description | The system shall store patient minimal profiles (privacy-scoped) linked to prescriptions; only role-authorized staff can view prescription-linked identity (FR-RX-01, BR-PRIV-01). |
| Actors | UC-02, UC-06 |
| Preconditions | Rx module enabled. |
| Postconditions | Rx linked to patient; access restricted. |
| Main Flow | 1. Create/lookup patient. 2. Link Rx. 3. Access controlled by role. |
| Alternative Flows | 1a. Anonymized placeholder per privacy config (BR-RX-01). |
| Business Rules | BR-PRIV-01, BR-RX-01 |
| Validation Rules | Access restricted by role; exports consent-scoped. |
| Error Conditions | ERR-CUS-005-01: Unauthorized access attempt → 403 + audit. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-RX-001, REQ-CMP-004 |
| Acceptance Criteria | **AC-REQ-CUS-005-01:** Rx linked to privacy-scoped patient record. **AC-REQ-CUS-005-02:** Identity view restricted to authorized roles (BR-PRIV-01). |
| Status | Draft |

#### REQ-CUS-006 — Consent / Opt-In Management

| Field | Detail |
|-------|--------|
| Description | The system shall manage customer consent/opt-in (marketing, loyalty, digital receipts, privacy regime) with audit (FR-CUST-01, NFR-N-06). |
| Actors | UC-04, UC-06 |
| Preconditions | Customer record exists. |
| Postconditions | Consent state tracked and auditable. |
| Main Flow | 1. Capture consent. 2. Record channel/date. 3. Enforce in processing. |
| Alternative Flows | 3a. Marketing to non-consented customer → suppressed. |
| Business Rules | BR-PRIV-01, NFR-N-06 |
| Validation Rules | Consent recorded before marketing use. |
| Error Conditions | ERR-CUS-006-01: Use without consent → suppressed + alert. |
| Priority / Estimate | Must / S |
| Dependencies | REQ-CUS-001 |
| Acceptance Criteria | **AC-REQ-CUS-006-01:** Consent captured and enforced; audited. |
| Status | Draft |

---

## 3.9 MOD-09 — Prescriptions

### 3.9.1 Module Overview

| Attribute | Detail |
|-----------|--------|
| Module Name | Prescriptions |
| Business Goal | Digitize the Rx lifecycle — intake, validation, fulfillment, controlled-substance logging, archive, and digital-Rx interface — so every dispense is legally traceable (BRD P02, FR-RX-01..05). |
| Description | Handles paper and digital prescriptions with validity enforcement, pharmacist verification, refill/repeat controls, controlled-substance register integration, and retention-compliant archive. |
| Business Value | Legal traceability (P-02); safety enforcement (invalid/expired/over-quantity blocked); positions platform for national e-Rx programs (OP-06). |
| Target Users | UC-02 (Pharmacist-in-Charge), UC-03, UC-06 (register), UC-10 (adapter config) |
| Dependencies | CUS (patient profile), INV (stock), CMP (market Rx mode + controlled register), AUD |
| Priority | Must (core), Should (digital Rx adapter) |
| Source / Trace | BRD FR-RX-01..05, P02, BR-RX-01..06, BR-CTL-01..04, BR-PRIV-01, NFR-N-14 |

### 3.9.2 Requirements Catalog

| ID | Requirement | Priority | Estimate | Dependencies | BRD Trace |
|----|-------------|----------|----------|--------------|-----------|
| REQ-RX-001 | Rx Capture (issuer, date, items, qty, directions, attachments) | Must | L | CUS-005, MED | FR-RX-01, BR-RX-01 |
| REQ-RX-002 | Rx Validation (validity window, refills, quantity) | Must | L | RX-001 | FR-RX-02, BR-RX-02/03/05 |
| REQ-RX-003 | Fulfillment & Pharmacist Verification (dispense signature) | Must | L | RX-002, INV | FR-RX-02, BR-RX-04, BR-RX-06 |
| REQ-RX-004 | Controlled-Substance Register (Immutable) | Must | XL | RX-003, CMP-007 | FR-RX-03, BR-CTL-01..03 |
| REQ-RX-005 | Rx Archive & Retention | Must | M | RX-001 | FR-RX-04, BR-AUD-01, NFR-N-14 |
| REQ-RX-006 | Digital Rx Adapter Interface | Should | L | CMP (Rx mode) | FR-RX-05, BR-LOC-01, OP-06 |
| REQ-RX-007 | Refill/Repeat Management | Must | M | RX-002 | BR-RX-05, P02 |

### 3.9.3 Detailed Requirements

#### REQ-RX-001 — Rx Capture

| Field | Detail |
|-------|--------|
| Description | The system shall capture prescriptions with issuer, issue date, patient reference (or anonymized placeholder per privacy config), prescribed items, quantities, directions, and image/attachment capture (attachment ≤ 5 MB) before fulfillment (FR-RX-01, BR-RX-01). |
| Actors | UC-02, UC-03 |
| Preconditions | Rx module enabled; market pack defines Rx mode (paper/digital). |
| Postconditions | Rx record complete and available for validation. |
| Main Flow | 1. Create Rx. 2. Enter issuer/date/patient/items/qty/directions. 3. Attach scan/image (≤ 5 MB). 4. Save as incomplete until fulfillment. |
| Alternative Flows | 1a. Digital Rx import → adapter (REQ-RX-006). 3a. Attachment oversize → rejected. |
| Business Rules | BR-RX-01, BR-PRIV-01 |
| Validation Rules | All mandatory fields recorded before fulfillment (BR-RX-01). |
| Error Conditions | ERR-RX-001-01: Missing mandatory field → save-for-fulfillment blocked. |
| Priority / Estimate | Must / L |
| Dependencies | REQ-CUS-005, REQ-MED-001 |
| Acceptance Criteria | **AC-REQ-RX-001-01:** Rx record complete before fulfillment (BR-RX-01). **AC-REQ-RX-001-02:** Attachment ≤ 5 MB enforced (FR-RX-01). |
| Status | Draft |

#### REQ-RX-002 — Rx Validation

| Field | Detail |
|-------|--------|
| Description | The system shall enforce prescription validity: issue date within configurable window (default 90 days) without Pharmacist-in-Charge approval; dispensed quantity not exceeding prescribed unless clinically justified; refill count not exceeding prescribed refills unless revalidated (BR-RX-02/03/05). |
| Actors | UC-02, System |
| Preconditions | Rx captured. |
| Postconditions | Valid Rx proceed; invalid flagged for approval/justification. |
| Main Flow | 1. System validates issue window, quantity, refills. 2. Valid → allow fulfillment. 3. Invalid → block or route to Pharmacist-in-Charge approval + justification. |
| Alternative Flows | 3a. Over-quantity with clinical justification recorded by Pharmacist-in-Charge → allow (BR-RX-03). |
| Business Rules | BR-RX-02, BR-RX-03, BR-RX-05 |
| Validation Rules | Default validity 90 days; refill count enforced. |
| Error Conditions | ERR-RX-002-01: Expired Rx without approval → blocked. |
| Priority / Estimate | Must / L |
| Dependencies | REQ-RX-001 |
| Acceptance Criteria | **AC-REQ-RX-002-01:** Expired/over-quantity/over-refill blocked or approved-with-justification (FR-RX-02). **AC-REQ-RX-002-02:** Validity window configurable (default 90). |
| Status | Draft |

#### REQ-RX-003 — Fulfillment & Pharmacist Verification

| Field | Detail |
|-------|--------|
| Description | The system shall require pharmacist verification for each fulfilled prescription — identity + timestamp (dispense signature) recorded in the audit trail (BR-RX-04); controlled prescriptions additionally require valid issuer reference and documentation before fulfillment (BR-RX-06). |
| Actors | UC-02, UC-03 |
| Preconditions | Rx validated; stock available. |
| Postconditions | Rx fulfilled; dispense signature recorded; stock decremented. |
| Main Flow | 1. Verify Rx. 2. Check stock/expiry per line. 3. Dispense. 4. Record pharmacist verification + timestamp. 5. Update stock. 6. Record charges/payment. |
| Alternative Flows | 2a. Insufficient stock → partial/backorder per policy. 6a. Controlled substance → register entry per REQ-RX-004. |
| Business Rules | BR-RX-04, BR-RX-06, BR-STK-02, BR-CTL-01 |
| Validation Rules | Dispense signature mandatory (BR-RX-04); controlled Rx needs issuer reference (BR-RX-06). |
| Error Conditions | ERR-RX-003-01: Missing verification → fulfillment blocked. |
| Priority / Estimate | Must / L |
| Dependencies | REQ-RX-002, REQ-INV-001 |
| Acceptance Criteria | **AC-REQ-RX-003-01:** Every fulfilled Rx carries pharmacist identity + timestamp (BR-RX-04). **AC-REQ-RX-003-02:** Controlled Rx blocked without valid issuer reference (BR-RX-06). |
| Status | Draft |

#### REQ-RX-004 — Controlled-Substance Register

| Field | Detail |
|-------|--------|
| Description | The system shall maintain an immutable controlled-substance register: every transaction (receive, sell, transfer, adjust, destroy) creates a register entry with user, timestamp, quantity, and batch; register must reconcile to stock at any time; physical-count variance requires immediate documented review (BR-CTL-01..03). |
| Actors | UC-02, UC-06, UC-05 |
| Preconditions | Controlled classification active (REQ-MED-009). |
| Postconditions | Register immutable and reconcilable. |
| Main Flow | 1. Controlled transaction occurs. 2. Register entry created (user/timestamp/qty/batch). 3. Reconciliation check on demand. |
| Alternative Flows | 3a. Variance → documented review + compliance notification if above threshold (BR-CTL-03). |
| Business Rules | BR-CTL-01, BR-CTL-02, BR-CTL-03 |
| Validation Rules | Register immutable; no deletes; reconciliation = register ↔ stock. |
| Error Conditions | ERR-RX-004-01: Reconciliation mismatch → alert + review. |
| Priority / Estimate | Must / XL |
| Dependencies | REQ-MED-009, REQ-CMP-007 |
| Acceptance Criteria | **AC-REQ-RX-004-01:** Every controlled transaction creates an immutable register entry (BR-CTL-01). **AC-REQ-RX-004-02:** Register reconciles to stock at any time (BR-CTL-03). |
| Status | Draft |

#### REQ-RX-005 — Rx Archive & Retention

| Field | Detail |
|-------|--------|
| Description | The system shall archive fulfilled prescriptions (paper scan or digital reference) for the configured retention period with retrieval < 10 s and enforced retention (FR-RX-04, NFR-N-14). |
| Actors | UC-02, UC-06 |
| Preconditions | Rx fulfilled. |
| Postconditions | Archive retrievable; retention enforced. |
| Main Flow | 1. Archive on fulfillment. 2. Retention enforced. 3. Retrieval on request. |
| Alternative Flows | 3a. Beyond retention → purge per policy (with audit). |
| Business Rules | FR-RX-04, BR-AUD-01, NFR-N-14 |
| Validation Rules | Retention configurable per regulatory minimum. |
| Error Conditions | ERR-RX-005-01: Retrieval > 10 s → bound. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-RX-001, EXT-OBJ |
| Acceptance Criteria | **AC-REQ-RX-005-01:** Archive retrieval < 10 s; retention enforced. |
| Status | Draft |

#### REQ-RX-006 — Digital Rx Adapter Interface

| Field | Detail |
|-------|--------|
| Description | The system shall expose a configurable interface point for digital prescriptions per market (adapter contract documented; stub in MVP) (FR-RX-05). |
| Actors | UC-10, UC-02 |
| Preconditions | Market pack defines Rx mode; adapter contract documented. |
| Postconditions | Digital Rx import path available per market. |
| Main Flow | 1. Configure adapter. 2. Import digital Rx. 3. Validate per market. 4. Route to Rx workflow. |
| Alternative Flows | 3a. Validation failure → quarantine + alert. |
| Business Rules | FR-RX-05, BR-LOC-01 |
| Validation Rules | Adapter contract versioned; no core change for new market. |
| Error Conditions | ERR-RX-006-01: Adapter unavailable for market → disabled with notice. |
| Priority / Estimate | Should / L |
| Dependencies | REQ-CMP-005 |
| Acceptance Criteria | **AC-REQ-RX-006-01:** Adapter contract documented; MVP stub implemented (FR-RX-05). |
| Status | Draft |

#### REQ-RX-007 — Refill/Repeat Management

| Field | Detail |
|-------|--------|
| Description | The system shall manage refill/repeat tracking; refill count must not exceed prescribed refills unless revalidated (BR-RX-05). |
| Actors | UC-02 |
| Preconditions | Rx with refills prescribed. |
| Postconditions | Refill history tracked; limits enforced. |
| Main Flow | 1. Dispense initial. 2. Refill request. 3. Validate remaining refills. 4. Dispense/record. |
| Alternative Flows | 3a. Refills exhausted → revalidation required. |
| Business Rules | BR-RX-05 |
| Validation Rules | Refill count ≤ prescribed unless revalidated. |
| Error Conditions | ERR-RX-007-01: Refills exceeded → blocked. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-RX-002 |
| Acceptance Criteria | **AC-REQ-RX-007-01:** Refill limits enforced (BR-RX-05). |
| Status | Draft |

---

## 3.10 MOD-10 — Accounting

### 3.10.1 Module Overview

| Attribute | Detail |
|-----------|--------|
| Module Name | Accounting |
| Business Goal | Post every financial event as balanced double-entry, reconcile ledger to sub-ledgers, compute tax per market, and produce tax-return-ready outputs — with period locking and audited reversals (BRD P10, FR-ACC-01..05). |
| Description | The accounting core is the financial truth of the platform. Full financial-statement depth is phased (V3 per BRD §18); MVP must deliver double-entry posting, day-close posting, tax exports, and period locking. |
| Business Value | One-click day-close and tax-return-ready exports (P-06); audit trail (BR-ACC-03); e-invoicing readiness for KSA (RK-16); basis of KPI-14. |
| Target Users | UC-06, UC-01 |
| Dependencies | POS, INV, PUR, SUP, CUS, CMP (tax engine) |
| Priority | Must (core), Should (financial statements V3) |
| Source / Trace | BRD FR-ACC-01..05, P10, BR-ACC-01..04, BR-TAX-01..03, BR-CASH-02 |

### 3.10.2 Requirements Catalog

| ID | Requirement | Priority | Estimate | Dependencies | BRD Trace |
|----|-------------|----------|----------|--------------|-----------|
| REQ-ACC-001 | Double-Entry Posting Engine | Must | XL | All posting sources | FR-ACC-01, BR-ACC-01 |
| REQ-ACC-002 | Chart of Accounts, AR/AP, Cash/Bank Ledgers | Must | L | ACC-001 | FR-ACC-02 |
| REQ-ACC-003 | Inventory Valuation Posting (FIFO) | Must | L | ACC-001, INV-011 | FR-ACC-02, BR-ACC-04 |
| REQ-ACC-004 | Tax Computation & Tax-Ready Exports | Must | L | ACC-001, CMP-001 | FR-ACC-03, BR-TAX-01/02 |
| REQ-ACC-005 | Period Locking & Audited Reversals | Must | M | ACC-001 | FR-ACC-04, BR-ACC-03, BR-CASH-02 |
| REQ-ACC-006 | Market Tax Engines & E-Invoicing (ZATCA) | Must | XL | CMP-001, CMP-002 | FR-ACC-05, FR-LOC-05, BR-TAX-03 |
| REQ-ACC-007 | Ledger-Subledger Reconciliation at Day-Close | Must | M | ACC-001 | BR-ACC-02, KPI-14 |
| REQ-ACC-008 | Financial Statements (P&L, Balance Sheet) | Should | L | ACC-001 | FR-ACC-02, Roadmap V3 |

### 3.10.3 Detailed Requirements

#### REQ-ACC-001 — Double-Entry Posting Engine

| Field | Detail |
|-------|--------|
| Description | The system shall post balanced double-entry entries for all financial events automatically; unbalanced posting is rejected (FR-ACC-01, BR-ACC-01). |
| Actors | System, UC-06 |
| Preconditions | Financial event occurs (sale, return, receipt, payment, adjustment). |
| Postconditions | Balanced entries posted; audit recorded. |
| Main Flow | 1. Event mapped to chart of accounts. 2. System computes entries. 3. Balance check (Σ debits = Σ credits). 4. Post. |
| Alternative Flows | 3a. Unbalanced → rejected with diagnostic. |
| Business Rules | BR-ACC-01 |
| Validation Rules | Zero unbalanced posts allowed. |
| Error Conditions | ERR-ACC-001-01: Unbalanced → rejected. |
| Priority / Estimate | Must / XL |
| Dependencies | REQ-POS-001, REQ-PUR-002, REQ-INV-006, REQ-CUS-002 |
| Acceptance Criteria | **AC-REQ-ACC-001-01:** Zero unbalanced postings (BR-ACC-01). **AC-REQ-ACC-001-02:** All financial events auto-posting. |
| Status | Draft |

#### REQ-ACC-002 — Chart of Accounts, AR/AP, Cash/Bank Ledgers

| Field | Detail |
|-------|--------|
| Description | The system shall provide a chart of accounts, AR/AP, cash/bank ledgers, and inventory valuation accounts; reports match sub-ledgers (FR-ACC-02). |
| Actors | UC-06, UC-08 |
| Preconditions | Accounting configured. |
| Postconditions | Ledgers current; sub-ledger match. |
| Main Flow | 1. Configure COA (per market pack defaults). 2. Postings populate ledgers. 3. Reports read from ledgers. |
| Alternative Flows | 1a. Market pack provides default COA → applied. |
| Business Rules | FR-ACC-02, BR-ACC-02 |
| Validation Rules | Reports reconcile to sub-ledgers. |
| Error Conditions | ERR-ACC-002-01: COA inconsistency → validation error. |
| Priority / Estimate | Must / L |
| Dependencies | REQ-ACC-001 |
| Acceptance Criteria | **AC-REQ-ACC-002-01:** Reports match sub-ledgers (FR-ACC-02). |
| Status | Draft |

#### REQ-ACC-003 — Inventory Valuation Posting (FIFO)

| Field | Detail |
|-------|--------|
| Description | The system shall post inventory valuation on a consistent cost basis (FIFO default) across all postings (BR-ACC-04); valuation changes are audited policy changes. |
| Actors | System |
| Preconditions | Cost captured at GRN (REQ-PUR-002). |
| Postconditions | Inventory value consistent with policy. |
| Main Flow | 1. Receipt → inventory asset debit. 2. Sale → COGS debit + inventory credit (per FIFO). 3. Reconciliation at close. |
| Alternative Flows | 3a. Mismatch → day-close blocked (REQ-ACC-007). |
| Business Rules | BR-ACC-04 |
| Validation Rules | Consistent cost basis per tenant. |
| Error Conditions | ERR-ACC-003-01: Basis inconsistency → alert. |
| Priority / Estimate | Must / L |
| Dependencies | REQ-ACC-001, REQ-INV-011 |
| Acceptance Criteria | **AC-REQ-ACC-003-01:** Inventory value = GL inventory account (BR-ACC-04). |
| Status | Draft |

#### REQ-ACC-004 — Tax Computation & Tax-Ready Exports

| Field | Detail |
|-------|--------|
| Description | The system shall compute tax on every taxable line per product tax treatment and produce tax-return-ready exports reconciling to posted sales to 0 drift (FR-ACC-03, BR-TAX-01/02). |
| Actors | UC-06 |
| Preconditions | Tax engine from market pack; sales posted. |
| Postconditions | Tax export available and reconciling. |
| Main Flow | 1. Compute tax per rate. 2. Aggregate per rate. 3. Generate export. 4. Reconcile to sales. |
| Alternative Flows | 4a. Drift > 0 → export blocked + investigation. |
| Business Rules | BR-TAX-01, BR-TAX-02 |
| Validation Rules | Tax export reconciles to 0 drift (default tolerance 0.00). |
| Error Conditions | ERR-ACC-004-01: Drift → blocked export. |
| Priority / Estimate | Must / L |
| Dependencies | REQ-ACC-001, REQ-CMP-001 |
| Acceptance Criteria | **AC-REQ-ACC-004-01:** Tax computed per rate on every taxable line. **AC-REQ-ACC-004-02:** Exports reconcile to 0 drift (BR-TAX-02). |
| Status | Draft |

#### REQ-ACC-005 — Period Locking & Audited Reversals

| Field | Detail |
|-------|--------|
| Description | The system shall lock posted periods after close; any change requires an audited reversing entry (BR-ACC-03); post-close corrections require manager-authorized re-open with full audit (BR-CASH-02). |
| Actors | UC-06, UC-03 |
| Preconditions | Period closed. |
| Postconditions | Locked periods reject unapproved changes. |
| Main Flow | 1. Close/lock period. 2. Change request. 3. Authorized re-open (audited). 4. Reversing entry posted. |
| Alternative Flows | 3a. Not authorized → rejected. |
| Business Rules | BR-ACC-03, BR-CASH-02 |
| Validation Rules | Locked periods immutable without audited reversal. |
| Error Conditions | ERR-ACC-005-01: Unauthorized change → rejected. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-ACC-001 |
| Acceptance Criteria | **AC-REQ-ACC-005-01:** Locked periods reject unapproved changes (FR-ACC-04). **AC-REQ-ACC-005-02:** Reversals audited. |
| Status | Draft |

#### REQ-ACC-006 — Market Tax Engines & E-Invoicing

| Field | Detail |
|-------|--------|
| Description | The system shall support market-specific tax engines and e-invoicing (e.g., ZATCA Phase 2) via active market packs; invoice considered issued only after validation and transmission per pack spec; transmission failure blocks issue (FR-ACC-05, FR-LOC-05, BR-TAX-03). |
| Actors | UC-06, System |
| Preconditions | Active market pack requires e-invoicing (KSA). |
| Postconditions | E-invoice validated/transmitted before issue. |
| Main Flow | 1. Sale generates invoice. 2. Pack validates format. 3. Transmit to authority. 4. Success → mark issued. 5. Failure → block issue + alert. |
| Alternative Flows | 5a. Retry/queue with alert; issue remains blocked until success (BR-TAX-03). |
| Business Rules | BR-TAX-03, BR-LOC-01 |
| Validation Rules | No issue without validated transmission where required. |
| Error Conditions | ERR-ACC-006-01: Transmission failure → issue blocked (BR-TAX-03). |
| Priority / Estimate | Must / XL |
| Dependencies | REQ-CMP-001, REQ-CMP-002 |
| Acceptance Criteria | **AC-REQ-ACC-006-01:** E-invoice validated + transmitted before issue (FR-ACC-05). **AC-REQ-ACC-006-02:** Failure blocks issue. |
| Status | Draft |

#### REQ-ACC-007 — Ledger-Subledger Reconciliation at Day-Close

| Field | Detail |
|-------|--------|
| Description | The system shall reconcile the general ledger to sub-ledgers (sales, purchases, AR, AP, inventory) after each day-close; mismatch blocks the close (BR-ACC-02, KPI-14). |
| Actors | UC-06, System |
| Preconditions | Day-close triggered (REQ-SAL-006). |
| Postconditions | Reconciliation verified or close blocked. |
| Main Flow | 1. Day-close posts. 2. Reconcile GL ↔ sub-ledgers. 3. Pass → close. 4. Fail → block + investigation. |
| Alternative Flows | 4a. Investigation + correction → audited. |
| Business Rules | BR-ACC-02 |
| Validation Rules | 0 unexplained variance. |
| Error Conditions | ERR-ACC-007-01: Mismatch → close blocked. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-ACC-001, REQ-SAL-006 |
| Acceptance Criteria | **AC-REQ-ACC-007-01:** GL reconciles to sub-ledgers after each close (BR-ACC-02). |
| Status | Draft |

#### REQ-ACC-008 — Financial Statements (V3)

| Field | Detail |
|-------|--------|
| Description | (V3) The system shall provide financial statements (P&L, balance sheet, cash flow) and deep accounting (AR/AP maturity, multi-ledger) per BRD Phase 3. |
| Actors | UC-06 |
| Preconditions | V3 release; accounting core mature. |
| Postconditions | Statements generated from posted data. |
| Main Flow | 1. Select period. 2. Generate statement. 3. Export/validate. |
| Alternative Flows | None. |
| Business Rules | BR-ACC-01..04 |
| Validation Rules | Statements balance. |
| Error Conditions | ERR-ACC-008-01: Unbalanced → blocked. |
| Priority / Estimate | Should / L |
| Dependencies | REQ-ACC-001..007 |
| Acceptance Criteria | **AC-REQ-ACC-008-01 (V3):** P&L/Balance sheet balance and reconcile to ledger. |
| Status | Deferred |

---

## 3.11 MOD-11 — Reports

### 3.11.1 Module Overview

| Attribute | Detail |
|-----------|--------|
| Module Name | Reports |
| Business Goal | Deliver standard operational and compliance reports from posted, reconciled data, with consolidation, scheduling, and export (BRD P15, FR-REP-01..04). |
| Description | Reporting engine covering sales, stock, expiry, low stock, purchases, supplier, cash, profit/margin, and branch comparison; consolidated multi-branch roll-ups; scheduling/delivery; compliance exports. |
| Business Value | Visibility drives owner/manager decisions (P-01/P-03/P-07); compliance exports satisfy regulators; scheduling removes manual work (P-06). |
| Target Users | UC-01, UC-03, UC-06, UC-07, UC-09 |
| Dependencies | All operational modules; ACC (posted data) |
| Priority | Must (core), Should (scheduling) |
| Source / Trace | BRD FR-REP-01..04, P15, BR-REP-01/02, BR-AUD-01 |

### 3.11.2 Requirements Catalog

| ID | Requirement | Priority | Estimate | Dependencies | BRD Trace |
|----|-------------|----------|----------|--------------|-----------|
| REQ-RPT-001 | Standard Operational Reports | Must | L | ACC, INV, POS, PUR | FR-REP-01 |
| REQ-RPT-002 | Consolidated Multi-Branch Reporting | Must | L | BR, DASH-002 | FR-REP-02, BR-REP-02 |
| REQ-RPT-003 | Report Scheduling & Delivery | Should | M | RPT-001, NOT | FR-REP-03 |
| REQ-RPT-004 | Compliance Report Exports | Must | M | CMP, AUD | FR-REP-04, BR-AUD-01 |
| REQ-RPT-005 | Report Export (PDF/Excel/CSV) | Must | S | RPT-001 | FR-REP-03 |
| REQ-RPT-006 | Data-Currency Timestamp on Reports | Must | S | RPT-001 | BR-REP-01 |
| REQ-RPT-007 | Ad-Hoc Report Builder | Could | L | RPT-001 | BRD §17.3 (differentiator) |

### 3.11.3 Detailed Requirements

#### REQ-RPT-001 — Standard Operational Reports

| Field | Detail |
|-------|--------|
| Description | The system shall generate standard operational reports (sales, stock, expiry, low stock, purchases, supplier, cash, profit/margin, branch comparison) from posted data in < 10 s for 90-day data at tenant scale (FR-REP-01). |
| Actors | UC-01, UC-03, UC-06, UC-07 |
| Preconditions | Posted data exists. |
| Postconditions | Reports rendered/exported. |
| Main Flow | 1. Select report + scope/period. 2. Generate from posted data. 3. Validate totals. 4. Render/export. |
| Alternative Flows | 3a. Unposted/unreconciled data → excluded with timestamp note. |
| Business Rules | BR-REP-01 |
| Validation Rules | Report from posted, reconciled data; currency timestamp shown. |
| Error Conditions | ERR-RPT-001-01: Generation > 10 s for 90-day scope → bound. |
| Priority / Estimate | Must / L |
| Dependencies | REQ-ACC-001, REQ-INV-001, REQ-POS-001 |
| Acceptance Criteria | **AC-REQ-RPT-001-01:** Report < 10 s for 90-day data (FR-REP-01). **AC-REQ-RPT-001-02:** Totals validate against source ledgers. |
| Status | Draft |

#### REQ-RPT-002 — Consolidated Multi-Branch Reporting

| Field | Detail |
|-------|--------|
| Description | The system shall consolidate multi-branch reports so consolidated = Σ branch reports with no duplication (FR-REP-02, BR-REP-02, BR-BRANCH-01). |
| Actors | UC-07, UC-01 |
| Preconditions | Branch hierarchy defined. |
| Postconditions | Consolidated report balances to branches. |
| Main Flow | 1. Select consolidated scope. 2. Aggregate per hierarchy. 3. Validate balance. |
| Alternative Flows | 2a. Branch data stale → timestamp flag. |
| Business Rules | BR-REP-02, BR-BRANCH-01 |
| Validation Rules | Consolidated = Σ branch (invariant). |
| Error Conditions | ERR-RPT-002-01: Imbalance → block render. |
| Priority / Estimate | Must / L |
| Dependencies | REQ-BR-001 |
| Acceptance Criteria | **AC-REQ-RPT-002-01:** Consolidated = Σ branches (BR-REP-02). |
| Status | Draft |

#### REQ-RPT-003 — Report Scheduling & Delivery

| Field | Detail |
|-------|--------|
| Description | The system shall support scheduled report generation and delivery (email/in-app) per tenant configuration (FR-REP-03). |
| Actors | UC-01, UC-06, UC-07 |
| Preconditions | Report + schedule configured. |
| Postconditions | Deliveries on time; failures alerted. |
| Main Flow | 1. Configure schedule. 2. Job runs. 3. Deliver. |
| Alternative Flows | 3a. Failure → retry + alert (REQ-NOT-002). |
| Business Rules | FR-REP-03 |
| Validation Rules | Delivery on schedule. |
| Error Conditions | ERR-RPT-003-01: Delivery failure → alert. |
| Priority / Estimate | Should / M |
| Dependencies | REQ-RPT-001, REQ-NOT-001 |
| Acceptance Criteria | **AC-REQ-RPT-003-01:** Scheduled deliveries delivered on time (FR-REP-03). |
| Status | Draft |

#### REQ-RPT-004 — Compliance Report Exports

| Field | Detail |
|-------|--------|
| Description | The system shall produce compliance exports (audit, controlled-substance register, tax, recall) per market pack, time-stamped and complete (FR-REP-04, FR-LOC-07). |
| Actors | UC-06, UC-02, UC-10 |
| Preconditions | Data present; pack defines format. |
| Postconditions | Exports complete and validated. |
| Main Flow | 1. Select compliance report. 2. Generate per pack spec. 3. Export. |
| Alternative Flows | 2a. Format not in pack → disabled. |
| Business Rules | FR-REP-04, BR-AUD-01, FR-LOC-07 |
| Validation Rules | Export validated against pack spec. |
| Error Conditions | ERR-RPT-004-01: Invalid format → blocked. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-AUD-001, REQ-CMP-007 |
| Acceptance Criteria | **AC-REQ-RPT-004-01:** Compliance exports per pack spec, complete + time-stamped. |
| Status | Draft |

#### REQ-RPT-005 — Report Export (PDF/Excel/CSV)

| Field | Detail |
|-------|--------|
| Description | The system shall export reports to PDF, Excel, and CSV with consistent layout and reconciliation (FR-REP-03). |
| Actors | All report users |
| Preconditions | Report generated. |
| Postconditions | Export available. |
| Main Flow | 1. Generate. 2. Export. |
| Alternative Flows | None. |
| Business Rules | FR-REP-03 |
| Validation Rules | Export totals = on-screen totals. |
| Error Conditions | ERR-RPT-005-01: Export mismatch → blocked. |
| Priority / Estimate | Must / S |
| Dependencies | REQ-RPT-001 |
| Acceptance Criteria | **AC-REQ-RPT-005-01:** Exports complete; totals match on-screen. |
| Status | Draft |

#### REQ-RPT-006 — Data-Currency Timestamp

| Field | Detail |
|-------|--------|
| Description | Every report shall display the data-currency timestamp (BR-REP-01). |
| Actors | System |
| Preconditions | Report generated. |
| Postconditions | Timestamp visible. |
| Main Flow | 1. Stamp. 2. Render. |
| Alternative Flows | None. |
| Business Rules | BR-REP-01 |
| Validation Rules | Timestamp = source data generation time. |
| Error Conditions | ERR-RPT-006-01: Missing timestamp → render warning. |
| Priority / Estimate | Must / S |
| Dependencies | REQ-RPT-001 |
| Acceptance Criteria | **AC-REQ-RPT-006-01:** Data-currency timestamp displayed (BR-REP-01). |
| Status | Draft |

#### REQ-RPT-007 — Ad-Hoc Report Builder

| Field | Detail |
|-------|--------|
| Description | (Could) The system shall provide an ad-hoc report builder for authorized users to compose custom reports from analytics-ready data (BRD §17.3). |
| Actors | UC-07, UC-09 |
| Preconditions | Feature entitlement. |
| Postconditions | Custom report saved/shared. |
| Main Flow | 1. Compose. 2. Validate against data model. 3. Save/export. |
| Alternative Flows | None. |
| Business Rules | BR-REP-01 |
| Validation Rules | Query against analytics-ready data only. |
| Error Conditions | ERR-RPT-007-01: Unsupported field → rejected. |
| Priority / Estimate | Could / L |
| Dependencies | REQ-AI-001 (analytics data) |
| Acceptance Criteria | **AC-REQ-RPT-007-01 (Could):** Custom reports from analytics data. |
| Status | Deferred |

---

## 3.12 MOD-12 — Branches

### 3.12.1 Module Overview

| Attribute | Detail |
|-----------|--------|
| Module Name | Branches |
| Business Goal | Model multi-branch tenancy with hierarchy, central policy push, transaction attribution, and head-office consolidation — enabling chain operations on the same tenant architecture (BRD P11/P13, FR-BR-01..03). |
| Description | Branch management is the structural backbone of chain tenancies: every transaction belongs to exactly one branch; policies pushed centrally; transfers coordinated; consolidated reporting rolls up per hierarchy. |
| Business Value | Chain expansion economics (OP-02); consistent policy (BR-BRANCH-02); dead-stock/stockout rebalancing (P-07). |
| Target Users | UC-08, UC-07, UC-03 |
| Dependencies | TEN, USR, INV |
| Priority | Must (chains), native from MVP (PG-03) |
| Source / Trace | BRD FR-BR-01..03, P11/P13, BR-BRANCH-01/02, BR-STK-06 |

### 3.12.2 Requirements Catalog

| ID | Requirement | Priority | Estimate | Dependencies | BRD Trace |
|----|-------------|----------|----------|--------------|-----------|
| REQ-BR-001 | Branch Hierarchy | Must | M | TEN | FR-PH-01, BR-BRANCH-01 |
| REQ-BR-002 | Central Policy Push | Must | M | BR-001 | FR-BR-01, BR-BRANCH-02 |
| REQ-BR-003 | Head-Office Consolidated Access | Must | M | BR-001, DASH-002 | FR-BR-03 |
| REQ-BR-004 | Transaction Branch Attribution | Must | M | BR-001, POS | BR-BRANCH-01 |
| REQ-BR-005 | Inter-Branch Transfer Coordination | Must | M | BR-001, INV-008 | FR-BR-02, BR-STK-06 |

### 3.12.3 Detailed Requirements

#### REQ-BR-001 — Branch Hierarchy

| Field | Detail |
|-------|--------|
| Description | The system shall support configuring one or more branches per tenant (address, tax registration, operating profile) and a branch hierarchy (FR-PH-01); every transaction belongs to exactly one branch (BR-BRANCH-01). |
| Actors | UC-08 |
| Preconditions | Tenant provisioned. |
| Postconditions | Branch(es) configured; hierarchy defined. |
| Main Flow | 1. Create branch. 2. Set address/tax/operating profile. 3. Define hierarchy. |
| Alternative Flows | 3a. Single-branch tenant → flat hierarchy. |
| Business Rules | BR-BRANCH-01, FR-PH-01 |
| Validation Rules | Transaction attribution mandatory; consolidated roll-up no duplication. |
| Error Conditions | ERR-BR-001-01: Missing branch on transaction → rejected. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-TEN-001 |
| Acceptance Criteria | **AC-REQ-BR-001-01:** Branch create/edit ≤ 2 min (FR-PH-01). **AC-REQ-BR-001-02:** Every transaction attributed to exactly one branch (BR-BRANCH-01). |
| Status | Draft |

#### REQ-BR-002 — Central Policy Push

| Field | Detail |
|-------|--------|
| Description | Head-office policy (pricing, discounts, product availability, approval thresholds) shall be pushed centrally; branch deviation requires override with reason, visible in reports (FR-BR-01, BR-BRANCH-02). Push propagates in < 60 s. |
| Actors | UC-07, UC-08 |
| Preconditions | Chain tenant; policy configured. |
| Postconditions | Policy active at branches; deviations flagged. |
| Main Flow | 1. Configure policy. 2. Push to branches. 3. Branches apply. 4. Deviations override with reason. |
| Alternative Flows | 4a. Deviation → reason captured + visible in reports (BR-BRANCH-02). |
| Business Rules | BR-BRANCH-02 |
| Validation Rules | Push propagation < 60 s (FR-BR-01). |
| Error Conditions | ERR-BR-002-01: Push failure → retry + alert. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-BR-001, REQ-SET-004 |
| Acceptance Criteria | **AC-REQ-BR-002-01:** Policy push propagates < 60 s (FR-BR-01). **AC-REQ-BR-002-02:** Deviations flagged with reason in reports. |
| Status | Draft |

#### REQ-BR-003 — Head-Office Consolidated Access

| Field | Detail |
|-------|--------|
| Description | The system shall provide head-office dashboards and consolidated access across branches with live data within 1 min of transaction (FR-BR-03). |
| Actors | UC-07, UC-01 |
| Preconditions | Chain tenant. |
| Postconditions | Head office sees live consolidated view. |
| Main Flow | 1. Open head-office dashboard. 2. View live data. |
| Alternative Flows | 2a. Branch lag > 1 min → stale flag. |
| Business Rules | FR-BR-03, BR-REP-02 |
| Validation Rules | Live within 1 min. |
| Error Conditions | ERR-BR-003-01: Data lag → flag. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-DASH-002 |
| Acceptance Criteria | **AC-REQ-BR-003-01:** Head office sees branch data within 1 min (FR-BR-03). |
| Status | Draft |

#### REQ-BR-004 — Transaction Branch Attribution

| Field | Detail |
|-------|--------|
| Description | All transactions (sales, receipts, adjustments, transfers, Rx) shall carry branch attribution; consolidated reports roll up without duplication (BR-BRANCH-01). |
| Actors | System |
| Preconditions | Branch exists. |
| Postconditions | Attribution enforced. |
| Main Flow | 1. Transaction created. 2. Branch resolved from context. 3. Stored. |
| Alternative Flows | 2a. Ambiguous → default branch or error. |
| Business Rules | BR-BRANCH-01 |
| Validation Rules | No transaction without branch. |
| Error Conditions | ERR-BR-004-01: Missing branch → rejected. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-BR-001 |
| Acceptance Criteria | **AC-REQ-BR-004-01:** 100% transactions branch-attributed. |
| Status | Draft |

#### REQ-BR-005 — Inter-Branch Transfer Coordination

| Field | Detail |
|-------|--------|
| Description | The system shall coordinate transfer requests/approvals between branches with batch-level manifests and cost allocation, closing balanced (FR-BR-02, BR-STK-06). |
| Actors | UC-07, UC-03, UC-05 |
| Preconditions | ≥ 2 branches; policy authorizes. |
| Postconditions | Transfer closed balanced; allocation journal posted. |
| Main Flow | 1. Request transfer. 2. Approve (qty/cost). 3. Ship manifest. 4. Receive. 5. Close balanced. |
| Alternative Flows | 5a. Variance → handled + audited. |
| Business Rules | BR-STK-06, BR-AUTH-01 |
| Validation Rules | Source decrease = destination increase at close. |
| Error Conditions | ERR-BR-005-01: Unbalanced close → blocked. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-INV-008 |
| Acceptance Criteria | **AC-REQ-BR-005-01:** Transfers balanced and audited (FR-BR-02). |
| Status | Draft |

---

## 3.13 MOD-13 — Users

### 3.13.1 Module Overview

| Attribute | Detail |
|-----------|--------|
| Module Name | Users |
| Business Goal | Provide named, uniquely-identified user accounts with lifecycle management, authentication policies, and least-privilege defaults; prohibit shared logins (BRD P14, FR-USR-01..03, BR-SEC-01/04). |
| Description | User registry with identity, account state (active/disabled/suspended/locked), branch scope, role assignments, authentication (password/2FA/session), and lifecycle events feeding audit. |
| Business Value | Named-user accountability (P-08); compliance posture; audit trail for regulators. |
| Target Users | UC-08, UC-10 |
| Dependencies | ROL, AUD, TEN |
| Priority | Must |
| Source / Trace | BRD FR-USR-01..03, P14, BR-SEC-01..04, BR-AUD-01 |

### 3.13.2 Requirements Catalog

| ID | Requirement | Priority | Estimate | Dependencies | BRD Trace |
|----|-------------|----------|----------|--------------|-----------|
| REQ-USR-001 | Named User Account Lifecycle | Must | M | ROL, TEN | FR-USR-01, BR-SEC-01 |
| REQ-USR-002 | Authentication Policies (password/2FA/session/lockout) | Must | L | USR-001, SEC | FR-USR-02, BR-SEC-04 |
| REQ-USR-003 | User Branch Scope Assignment | Must | M | USR-001, BR | FR-USR-01, BR-SEC-02 |
| REQ-USR-004 | User Lifecycle Events → Audit | Must | S | USR-001, AUD | BR-AUD-01, FR-USR-03 |
| REQ-USR-005 | Password & Credential Management | Must | M | USR-002 | BR-SEC-04, SEC requirements |

### 3.13.3 Detailed Requirements

#### REQ-USR-001 — Named User Account Lifecycle

| Field | Detail |
|-------|--------|
| Description | The system shall manage named user accounts (create, enable, disable, suspend, revoke) with unique identity; shared logins prohibited by configuration enforcement (BR-SEC-01). |
| Actors | UC-08, UC-10 |
| Preconditions | Tenant provisioned. |
| Postconditions | Account state managed; changes immediate. |
| Main Flow | 1. Create user. 2. Assign role/branch scope. 3. Activate. 4. Lifecycle events (join/leave/role change). 5. Revoke. |
| Alternative Flows | 4a. Departing staff → immediate revoke with audit. |
| Business Rules | BR-SEC-01, BR-SEC-02 |
| Validation Rules | Unique named accounts; no shared logins. |
| Error Conditions | ERR-USR-001-01: Duplicate identity → rejected. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-ROL-001, REQ-TEN-001 |
| Acceptance Criteria | **AC-REQ-USR-001-01:** Every user has unique named account (BR-SEC-01). **AC-REQ-USR-001-02:** Grant/revoke effective immediately (FR-USR-01). |
| Status | Draft |

#### REQ-USR-002 — Authentication Policies

| Field | Detail |
|-------|--------|
| Description | The system shall enforce centrally configured authentication policies: password policy, 2FA for admin/privileged actions, session timeout, and lockout thresholds (FR-USR-02, BR-SEC-04). |
| Actors | UC-08 (config), UC-10 |
| Preconditions | Policy configured. |
| Postconditions | Policy enforced centrally on all sign-in and privileged actions. |
| Main Flow | 1. Configure policy. 2. Enforce at login/session. 3. Enforce 2FA for privileged actions (BR-SEC-03). |
| Alternative Flows | 3a. 2FA failure → action blocked. |
| Business Rules | BR-SEC-04, BR-SEC-03 |
| Validation Rules | Policy enforced centrally; lockout after threshold. |
| Error Conditions | ERR-USR-002-01: Exceeded attempts → lockout. |
| Priority / Estimate | Must / L |
| Dependencies | REQ-USR-001, SEC-requirements |
| Acceptance Criteria | **AC-REQ-USR-002-01:** Policies enforced centrally (BR-SEC-04). **AC-REQ-USR-002-02:** 2FA available for admin/privileged actions. |
| Status | Draft |

#### REQ-USR-003 — User Branch Scope Assignment

| Field | Detail |
|-------|--------|
| Description | The system shall assign users a branch scope so access is limited to authorized branches; least-privilege default (FR-USR-01, BR-SEC-02). |
| Actors | UC-08 |
| Preconditions | Branches exist. |
| Postconditions | User access scoped. |
| Main Flow | 1. Assign scope. 2. Enforce on all requests. |
| Alternative Flows | 2a. Unauthorized branch → denied. |
| Business Rules | BR-SEC-02 |
| Validation Rules | Access enforced per role + branch scope. |
| Error Conditions | ERR-USR-003-01: Scope violation → 403 + audit. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-BR-001 |
| Acceptance Criteria | **AC-REQ-USR-003-01:** Access limited to assigned branch scope. |
| Status | Draft |

#### REQ-USR-004 — User Lifecycle Events → Audit

| Field | Detail |
|-------|--------|
| Description | All user lifecycle and access events shall be recorded immutably with user, timestamp, before/after, and IP/device (BR-AUD-01, FR-USR-03). |
| Actors | System |
| Preconditions | Events occur. |
| Postconditions | Audit complete. |
| Main Flow | 1. Event occurs. 2. Audit record written. 3. Exportable. |
| Alternative Flows | None. |
| Business Rules | BR-AUD-01 |
| Validation Rules | 100% mandated events logged. |
| Error Conditions | ERR-USR-004-01: Audit write failure → alert (NFR observability). |
| Priority / Estimate | Must / S |
| Dependencies | REQ-AUD-001 |
| Acceptance Criteria | **AC-REQ-USR-004-01:** All lifecycle events audited. |
| Status | Draft |

#### REQ-USR-005 — Password & Credential Management

| Field | Detail |
|-------|--------|
| Description | The system shall support password setup/reset/expiry, MFA enrollment, and credential revocation per policy (BR-SEC-04). |
| Actors | UC-08, all users |
| Preconditions | Account exists. |
| Postconditions | Credentials managed securely. |
| Main Flow | 1. Set/reset. 2. Enroll MFA. 3. Enforce expiry. 4. Revoke. |
| Alternative Flows | 4a. Lost device → recovery flow with verification. |
| Business Rules | BR-SEC-04 |
| Validation Rules | Password policy enforced. |
| Error Conditions | ERR-USR-005-01: Weak password → rejected. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-USR-002 |
| Acceptance Criteria | **AC-REQ-USR-005-01:** Password/2FA lifecycle per policy. |
| Status | Draft |

---

## 3.14 MOD-14 — Roles & Permissions

### 3.14.1 Module Overview

| Attribute | Detail |
|-----------|--------|
| Module Name | Roles & Permissions |
| Business Goal | Provide RBAC with roles defining module/action permissions and branch scope; grant/revoke effective immediately; least-privilege default (BRD P14, FR-USR-01, BR-SEC-01/02). |
| Description | Role catalog (predefined + custom), permission matrix (module × action × scope), role assignment, and enforcement at every API and UI boundary. |
| Business Value | Proves who did what (P-08); reduces insider risk; satisfies regulatory access expectations. |
| Target Users | UC-08, UC-10 |
| Dependencies | USR, AUD, TEN |
| Priority | Must |
| Source / Trace | BRD FR-USR-01/02, P14, BR-SEC-01/02/03 |

### 3.14.2 Requirements Catalog

| ID | Requirement | Priority | Estimate | Dependencies | BRD Trace |
|----|-------------|----------|----------|--------------|-----------|
| REQ-ROL-001 | Role Catalog (predefined + custom) | Must | M | TEN | FR-USR-01, BR-SEC-02 |
| REQ-ROL-002 | Permission Matrix (module × action × scope) | Must | M | ROL-001 | BR-SEC-02 |
| REQ-ROL-003 | Runtime Enforcement | Must | L | ROL-002 | BR-SEC-01/02 |
| REQ-ROL-004 | Privileged Action Controls (approval/2FA) | Must | M | ROL-003 | BR-SEC-03 |
| REQ-ROL-005 | Role Change Audit & Review | Must | S | ROL-001, AUD | BR-AUD-01, P14 |

### 3.14.3 Detailed Requirements

#### REQ-ROL-001 — Role Catalog

| Field | Detail |
|-------|--------|
| Description | The system shall provide a role catalog (predefined roles for persona classes + custom roles) configurable per tenant (BR-SEC-02). |
| Actors | UC-08 |
| Preconditions | Tenant configured. |
| Postconditions | Roles available for assignment. |
| Main Flow | 1. View predefined roles. 2. Create custom role. 3. Configure permissions. |
| Alternative Flows | 2a. Clone existing role. |
| Business Rules | BR-SEC-02 |
| Validation Rules | Role names unique; permissions scoped. |
| Error Conditions | ERR-ROL-001-01: Duplicate role → rejected. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-TEN-001 |
| Acceptance Criteria | **AC-REQ-ROL-001-01:** Predefined + custom roles configurable per tenant. |
| Status | Draft |

#### REQ-ROL-002 — Permission Matrix

| Field | Detail |
|-------|--------|
| Description | The system shall define permissions as module × action (create/read/update/delete/approve/override) × branch scope, assigned to roles (BR-SEC-02). |
| Actors | UC-08 |
| Preconditions | Roles exist. |
| Postconditions | Matrix stored and versioned. |
| Main Flow | 1. Configure matrix. 2. Assign to role. 3. Version. |
| Alternative Flows | None. |
| Business Rules | BR-SEC-02, BR-TEN-03 |
| Validation Rules | Least-privilege default enforced. |
| Error Conditions | ERR-ROL-002-01: Invalid permission → rejected. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-ROL-001 |
| Acceptance Criteria | **AC-REQ-ROL-002-01:** Role assignment effective immediately (FR-USR-01). |
| Status | Draft |

#### REQ-ROL-003 — Runtime Enforcement

| Field | Detail |
|-------|--------|
| Description | The system shall enforce RBAC at every API and UI boundary at runtime; denied access logged (BR-SEC-01/02). |
| Actors | System |
| Preconditions | User authenticated. |
| Postconditions | Requests authorized or denied. |
| Main Flow | 1. Request. 2. Resolve role + scope. 3. Allow/deny. 4. Log. |
| Alternative Flows | 3a. Deny → 403 + audit. |
| Business Rules | BR-SEC-01/02 |
| Validation Rules | Enforcement server-side, never client-side only. |
| Error Conditions | ERR-ROL-003-01: Denied → 403. |
| Priority / Estimate | Must / L |
| Dependencies | REQ-ROL-002 |
| Acceptance Criteria | **AC-REQ-ROL-003-01:** Enforcement at all boundaries; denials logged. |
| Status | Draft |

#### REQ-ROL-004 — Privileged Action Controls

| Field | Detail |
|-------|--------|
| Description | Privileged actions (price overrides, refunds above threshold, voids, adjustments, role changes) shall require approval or 2FA per policy (BR-SEC-03). |
| Actors | UC-08, UC-10, privileged roles |
| Preconditions | Privileged action attempted. |
| Postconditions | Action completed only after approval/2FA. |
| Main Flow | 1. Attempt. 2. Policy check. 3. Approval/2FA. 4. Complete. |
| Alternative Flows | 3a. Rejected → blocked + audit. |
| Business Rules | BR-SEC-03 |
| Validation Rules | Approval/2FA recorded. |
| Error Conditions | ERR-ROL-004-01: Missing approval → blocked. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-ROL-003 |
| Acceptance Criteria | **AC-REQ-ROL-004-01:** Privileged actions require approval/2FA per policy (BR-SEC-03). |
| Status | Draft |

#### REQ-ROL-005 — Role Change Audit & Review

| Field | Detail |
|-------|--------|
| Description | Role changes shall be audited; the system shall support periodic access review and forensic audit on request (BR-AUD-01, P14). |
| Actors | UC-08, UC-10 |
| Preconditions | Role changes occur. |
| Postconditions | Audit complete; review report available. |
| Main Flow | 1. Change role. 2. Audit. 3. Review report. |
| Alternative Flows | None. |
| Business Rules | BR-AUD-01 |
| Validation Rules | 100% role changes logged. |
| Error Conditions | ERR-ROL-005-01: None. |
| Priority / Estimate | Must / S |
| Dependencies | REQ-AUD-001 |
| Acceptance Criteria | **AC-REQ-ROL-005-01:** Role changes audited; review reports generated. |
| Status | Draft |

---

## 3.15 MOD-15 — Notifications

### 3.15.1 Module Overview

| Attribute | Detail |
|-----------|--------|
| Module Name | Notifications |
| Business Goal | Deliver timely, channel-appropriate notifications (in-app, email, SMS) for operational, billing, compliance, and health events, with preference management and audit (BRD P13, FR-TEN-03, FR-SUB-02). |
| Description | Notification service covering alerts (expiry, recall, low stock, quota, billing, day-close variances, health) with tenant preference configuration and delivery via EXT-EMAIL / EXT-SMS. |
| Business Value | Prevents missed safety/expiry/recall events; drives billing hygiene; supports CS health actions (P-10). |
| Target Users | All users (receivers), UC-08 (config), UC-10 |
| Dependencies | INV, POS, SUB, TEN, EXT-EMAIL, EXT-SMS |
| Priority | Must |
| Source / Trace | BRD FR-SUB-02, FR-TEN-03, P08/P13, BR-SUB-02, BR-RECALL-01 |

### 3.15.2 Requirements Catalog

| ID | Requirement | Priority | Estimate | Dependencies | BRD Trace |
|----|-------------|----------|----------|--------------|-----------|
| REQ-NOT-001 | In-App Notification Center | Must | M | All modules | FR-TEN-03 |
| REQ-NOT-002 | Automated Alerts (expiry/recall/quota/billing/variance) | Must | M | INV, SUB, SAL | BR-STK-04, BR-RECALL-01, BR-SUB-02 |
| REQ-NOT-003 | Recall/Customer Notification | Must | S | INV-009, CUS | BRD P08 |
| REQ-NOT-004 | Notification Preference Management | Must | S | NOT-001 | FR-TEN-02, NFR-N-06 |
| REQ-NOT-005 | Delivery Channels (Email/SMS) | Must | M | EXT-EMAIL, EXT-SMS | FR-SUB-02, FR-REP-03 |

### 3.15.3 Detailed Requirements

#### REQ-NOT-001 — In-App Notification Center

| Field | Detail |
|-------|--------|
| Description | The system shall provide an in-app notification center listing unread/read alerts per user with priority and navigation targets (FR-TEN-03). |
| Actors | All users |
| Preconditions | User authenticated. |
| Postconditions | Notifications visible; read state tracked. |
| Main Flow | 1. Event triggers notification. 2. Center lists. 3. User opens/navigates. |
| Alternative Flows | 2a. Quiet hours per preference → delayed. |
| Business Rules | FR-TEN-03 |
| Validation Rules | Notification generation auditable. |
| Error Conditions | ERR-NOT-001-01: None. |
| Priority / Estimate | Must / M |
| Dependencies | None |
| Acceptance Criteria | **AC-REQ-NOT-001-01:** Notifications delivered in-app with priority + navigation. |
| Status | Draft |

#### REQ-NOT-002 — Automated Alerts

| Field | Detail |
|-------|--------|
| Description | The system shall automatically generate alerts for expiry watchlist thresholds, recall, low stock/reorder, quota usage (80/90/100%), billing overdue, day-close variance, and tenant health anomalies (BR-STK-04, BR-RECALL-01, BR-SUB-01/02). |
| Actors | System, receivers |
| Preconditions | Trigger conditions met. |
| Postconditions | Alerts generated/delivered per preference. |
| Main Flow | 1. Condition detected. 2. Generate alert. 3. Deliver per preference. 4. Log. |
| Alternative Flows | 3a. Channel failure → fallback channel + retry. |
| Business Rules | BR-SUB-01/02, BR-STK-04, BR-RECALL-01 |
| Validation Rules | Alerts at 80/90/100% quota (BR-SUB-01). |
| Error Conditions | ERR-NOT-002-01: Delivery failure → fallback + audit. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-INV-003, REQ-SUB-001, REQ-SAL-006 |
| Acceptance Criteria | **AC-REQ-NOT-002-01:** Quota alerts at 80/90/100% (BR-SUB-01). **AC-REQ-NOT-002-02:** Recall/expiry alerts per thresholds. |
| Status | Draft |

#### REQ-NOT-003 — Recall / Customer Notification

| Field | Detail |
|-------|--------|
| Description | Where traceable customer records exist, the system shall notify affected customers of a recall in accordance with privacy/consent (BRD P08, BR-PRIV-01). |
| Actors | UC-02, UC-05 |
| Preconditions | Recall executed (REQ-INV-009); consent recorded. |
| Postconditions | Notified customers logged; consent respected. |
| Main Flow | 1. Recall created. 2. Trace purchasers. 3. Notify consented customers. 4. Log. |
| Alternative Flows | 3a. No consent → skip with record. |
| Business Rules | BR-PRIV-01, NFR-N-06 |
| Validation Rules | Notification only to consented customers. |
| Error Conditions | ERR-NOT-003-01: None. |
| Priority / Estimate | Must / S |
| Dependencies | REQ-INV-009, REQ-CUS-006 |
| Acceptance Criteria | **AC-REQ-NOT-003-01:** Consented customers notified; logs retained. |
| Status | Draft |

#### REQ-NOT-004 — Notification Preference Management

| Field | Detail |
|-------|--------|
| Description | The system shall allow tenants/users to configure notification preferences (type, channel, quiet hours) (FR-TEN-02, NFR-N-06). |
| Actors | UC-08, users |
| Preconditions | Notification service active. |
| Postconditions | Preferences applied. |
| Main Flow | 1. Configure preferences. 2. Service applies. |
| Alternative Flows | None. |
| Business Rules | NFR-N-06 |
| Validation Rules | Preferences versioned/audited. |
| Error Conditions | ERR-NOT-004-01: None. |
| Priority / Estimate | Must / S |
| Dependencies | REQ-NOT-001 |
| Acceptance Criteria | **AC-REQ-NOT-004-01:** Preferences applied and audited. |
| Status | Draft |

#### REQ-NOT-005 — Delivery Channels (Email/SMS)

| Field | Detail |
|-------|--------|
| Description | The system shall deliver notifications via email and SMS through provider abstractions (EXT-EMAIL, EXT-SMS), with retry and audit (FR-SUB-02, FR-REP-03). |
| Actors | System |
| Preconditions | Provider configured; consent per channel. |
| Postconditions | Delivery attempted with audit. |
| Main Flow | 1. Dispatch. 2. Retry on failure. 3. Log. |
| Alternative Flows | 2a. Persistent failure → alert + manual queue. |
| Business Rules | NFR-N-06 |
| Validation Rules | Delivery logged per channel. |
| Error Conditions | ERR-NOT-005-01: Failure → retry/log. |
| Priority / Estimate | Must / M |
| Dependencies | EXT-EMAIL, EXT-SMS |
| Acceptance Criteria | **AC-REQ-NOT-005-01:** Email/SMS delivery with retry + audit. |
| Status | Draft |

---

## 3.16 MOD-16 — Subscriptions & Billing

### 3.16.1 Module Overview

| Attribute | Detail |
|-----------|--------|
| Module Name | Subscriptions & Billing |
| Business Goal | Manage subscription plans, entitlements, add-ons, invoicing, payments, reminders, suspension/reinstatement, and tenant self-service — the commercial engine of the SaaS model (BRD P13, FR-SUB-01..04). |
| Description | Subscription lifecycle per BR-SUB-01..06: plans/limits, entitlements, invoicing on committed schedule, payment reminders, soft-limit → suspension with data-export preservation, proration on change. |
| Business Value | Recurring revenue (BO-02); retention/NRR (KPI-04/05); predictable billing; compliance with tenant expectations (BR-SUB-06). |
| Target Users | UC-08, UC-09, UC-10, UC-06 (finance) |
| Dependencies | TEN, NOT, EXT-PAY, EXT-EMAIL |
| Priority | Must |
| Source / Trace | BRD FR-SUB-01..04, P13, BR-SUB-01..06, DEC-06 |

### 3.16.2 Requirements Catalog

| ID | Requirement | Priority | Estimate | Dependencies | BRD Trace |
|----|-------------|----------|----------|--------------|-----------|
| REQ-SUB-001 | Subscription Plans, Entitlements & Licensed Limits | Must | L | TEN | FR-SUB-01, BR-SUB-01 |
| REQ-SUB-002 | Invoicing & Payment Processing | Must | L | SUB-001, EXT-PAY | FR-SUB-02, BR-SUB-02 |
| REQ-SUB-003 | Reminders, Suspension & Reinstatement | Must | L | SUB-002, NOT | FR-SUB-02, BR-SUB-02/06 |
| REQ-SUB-004 | Plan Change with Proration | Must | M | SUB-001 | FR-SUB-03, BR-SUB-03 |
| REQ-SUB-005 | Tenant Self-Service (billing history, add-ons) | Should | M | SUB-002 | FR-SUB-04, BR-SUB-05 |
| REQ-SUB-006 | Trial Lifecycle & Conversion | Must | M | SUB-001 | BR-SUB-04 |
| REQ-SUB-007 | Billing Audit & History | Must | M | SUB-002, AUD | BR-SUB-05 |

### 3.16.3 Detailed Requirements

#### REQ-SUB-001 — Subscription Plans, Entitlements & Licensed Limits

| Field | Detail |
|-------|--------|
| Description | The system shall manage plans, entitlements, add-ons, and licensed limits (users, branches, transactions, storage); limits enforced at runtime with warnings at 80/90/100% usage (FR-SUB-01, BR-SUB-01). |
| Actors | UC-08, UC-10 |
| Preconditions | Plan catalog configured. |
| Postconditions | Entitlements enforced; limits tracked. |
| Main Flow | 1. Define plans/add-ons. 2. Assign tenant plan. 3. Enforce at runtime. 4. Warn at 80/90/100%. |
| Alternative Flows | 3a. Feature not in plan → unavailable + upgrade path flagged (BR-TEN-02). |
| Business Rules | BR-SUB-01, BR-TEN-02 |
| Validation Rules | Runtime enforcement of entitlements. |
| Error Conditions | ERR-SUB-001-01: Exceeded limit → enforcement + warning. |
| Priority / Estimate | Must / L |
| Dependencies | REQ-TEN-001 |
| Acceptance Criteria | **AC-REQ-SUB-001-01:** Entitlements enforced at runtime (FR-SUB-01). **AC-REQ-SUB-001-02:** 80/90/100% warnings (BR-SUB-01). |
| Status | Draft |

#### REQ-SUB-002 — Invoicing & Payment Processing

| Field | Detail |
|-------|--------|
| Description | The system shall generate invoices on a committed schedule and process payments via selected gateway (DEC-06), with accurate billing cycle (FR-SUB-02). |
| Actors | UC-08, UC-10, System |
| Preconditions | Plan assigned; gateway configured. |
| Postconditions | Invoices generated; payments recorded. |
| Main Flow | 1. Schedule invoice. 2. Generate. 3. Charge (gateway). 4. Record. |
| Alternative Flows | 3a. Payment failure → reminder flow (REQ-SUB-003). |
| Business Rules | BR-SUB-02 |
| Validation Rules | Billing cycle accurate; payment audit. |
| Error Conditions | ERR-SUB-002-01: Charge failure → retry + reminder. |
| Priority / Estimate | Must / L |
| Dependencies | REQ-SUB-001, EXT-PAY |
| Acceptance Criteria | **AC-REQ-SUB-002-01:** Invoicing on committed schedule; payments recorded (FR-SUB-02). |
| Status | Draft |

#### REQ-SUB-003 — Reminders, Suspension & Reinstatement

| Field | Detail |
|-------|--------|
| Description | Late payment shall trigger reminder flow, then soft limit, then suspension per policy; suspended tenants retain full data access for export during grace period; suspension never deletes data without documented offboarding (BR-SUB-02/06). |
| Actors | UC-10, UC-09, System |
| Preconditions | Payment overdue. |
| Postconditions | Reminder/suspension sequence enforced; data preserved. |
| Main Flow | 1. Overdue → reminders. 2. Soft limits. 3. Suspension (data retained, export available). 4. Payment → reinstatement. |
| Alternative Flows | 4a. Offboarding → documented data export/deletion policy (BR-SUB-06). |
| Business Rules | BR-SUB-02, BR-SUB-06 |
| Validation Rules | Suspension preserves data export access (BR-SUB-06). |
| Error Conditions | ERR-SUB-003-01: None. |
| Priority / Estimate | Must / L |
| Dependencies | REQ-SUB-002, REQ-NOT-002 |
| Acceptance Criteria | **AC-REQ-SUB-003-01:** Reminder → soft-limit → suspension sequence (BR-SUB-02). **AC-REQ-SUB-003-02:** Suspended tenant retains export access (BR-SUB-06). |
| Status | Draft |

#### REQ-SUB-004 — Plan Change with Proration

| Field | Detail |
|-------|--------|
| Description | Plan upgrade shall be immediate and prorated; downgrade effective next billing period with entitlement validation (FR-SUB-03, BR-SUB-03). |
| Actors | UC-08, UC-10 |
| Preconditions | Current plan active. |
| Postconditions | Change applied with proration. |
| Main Flow | 1. Request change. 2. Upgrade → immediate + prorated. 3. Downgrade → next period + validation. |
| Alternative Flows | 3a. Downgrade conflict (usage exceeds new limits) → warning/block. |
| Business Rules | BR-SUB-03 |
| Validation Rules | Proration correct; entitlement validated. |
| Error Conditions | ERR-SUB-004-01: Downgrade conflict → blocked with explanation. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-SUB-001 |
| Acceptance Criteria | **AC-REQ-SUB-004-01:** Upgrade immediate + prorated; downgrade next period (BR-SUB-03). |
| Status | Draft |

#### REQ-SUB-005 — Tenant Self-Service

| Field | Detail |
|-------|--------|
| Description | The system shall provide tenant self-service for subscription and billing history; self-service changes audited (FR-SUB-04, BR-SUB-05). |
| Actors | UC-08 |
| Preconditions | Tenant active. |
| Postconditions | Self-service available. |
| Main Flow | 1. View plan/billing. 2. Request change/payment. 3. Audit. |
| Alternative Flows | None. |
| Business Rules | BR-SUB-05 |
| Validation Rules | Changes audited. |
| Error Conditions | ERR-SUB-005-01: None. |
| Priority / Estimate | Should / M |
| Dependencies | REQ-SUB-002 |
| Acceptance Criteria | **AC-REQ-SUB-005-01:** Self-service changes audited (FR-SUB-04). |
| Status | Draft |

#### REQ-SUB-006 — Trial Lifecycle & Conversion

| Field | Detail |
|-------|--------|
| Description | Trial tenants shall convert or be suspended; trial data exportable at any time before and during grace period (BR-SUB-04). |
| Actors | UC-09, UC-10 |
| Preconditions | Trial created. |
| Postconditions | Conversion/suspension enforced; export available. |
| Main Flow | 1. Trial start. 2. Expiry. 3. Convert or suspend. 4. Export available. |
| Alternative Flows | 3a. Convert → plan assigned. |
| Business Rules | BR-SUB-04 |
| Validation Rules | Export available during trial + grace. |
| Error Conditions | ERR-SUB-006-01: None. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-SUB-001, REQ-TEN-001 |
| Acceptance Criteria | **AC-REQ-SUB-006-01:** Trial data exportable at any time (BR-SUB-04). |
| Status | Draft |

#### REQ-SUB-007 — Billing Audit & History

| Field | Detail |
|-------|--------|
| Description | All subscription and billing changes shall be auditable and reflected in tenant invoice history (BR-SUB-05). |
| Actors | System |
| Preconditions | Billing events occur. |
| Postconditions | History complete. |
| Main Flow | 1. Event. 2. Audit. 3. History view. |
| Alternative Flows | None. |
| Business Rules | BR-SUB-05, BR-AUD-01 |
| Validation Rules | 100% changes audited. |
| Error Conditions | ERR-SUB-007-01: None. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-AUD-001 |
| Acceptance Criteria | **AC-REQ-SUB-007-01:** Billing changes in audit + invoice history. |
| Status | Draft |

---

## 3.17 MOD-17 — Tenant Management

### 3.17.1 Module Overview

| Attribute | Detail |
|-----------|--------|
| Module Name | Tenant Management |
| Business Goal | Automate tenant lifecycle (provisioning, configuration, health, export, offboarding) with isolated data spaces and versioned, auditable configuration (BRD P13, FR-TEN-01..04). |
| Description | The platform-side management of tenants: provisioning with isolation, configuration layer, health dashboard (see DASH-004), data export on request/offboarding, feature flags. |
| Business Value | Fast time-to-value (KPI-08, tenant live < 15 min); operational efficiency; retention via export guarantees (no data hostage — NFR-N-15). |
| Target Users | UC-09, UC-10 |
| Dependencies | SUB, CMP, USR |
| Priority | Must |
| Source / Trace | BRD FR-TEN-01..04, P13, BR-TEN-01..03, BR-SUB-06 |

### 3.17.2 Requirements Catalog

| ID | Requirement | Priority | Estimate | Dependencies | BRD Trace |
|----|-------------|----------|----------|--------------|-----------|
| REQ-TEN-001 | Tenant Provisioning (isolated, < 15 min) | Must | L | CMP, USR | FR-TEN-01, BR-TEN-01 |
| REQ-TEN-002 | Tenant Configuration Layer (versioned/audited) | Must | M | TEN-001 | FR-TEN-02, BR-TEN-03 |
| REQ-TEN-003 | Tenant Health Dashboard & Scoring | Must | M | TEN-001, SUB | FR-TEN-03, KPI-04 |
| REQ-TEN-004 | Tenant Data Export (on request/offboarding) | Must | L | TEN-001, AUD | FR-TEN-04, BR-SUB-06, NFR-N-15 |
| REQ-TEN-005 | Feature Flags per Tenant/Plan | Must | M | TEN-002 | FR-AI-03, BR-TEN-02 |
| REQ-TEN-006 | Market-Pack Activation per Tenant | Must | M | CMP-001 | BR-LOC-02, P17 |

### 3.17.3 Detailed Requirements

#### REQ-TEN-001 — Tenant Provisioning

| Field | Detail |
|-------|--------|
| Description | The system shall provision tenants automatically with isolated data space and configuration defaults, live in < 15 min via wizard (FR-TEN-01, BR-TEN-01). |
| Actors | UC-09, UC-10 |
| Preconditions | Signup/trial created. |
| Postconditions | Tenant live with isolation. |
| Main Flow | 1. Signup. 2. Provision isolated space. 3. Apply defaults (pack, currency, language). 4. Wizard config. 5. Live. |
| Alternative Flows | 4a. Wizard interrupted → resume. |
| Business Rules | BR-TEN-01 |
| Validation Rules | Isolation enforced at data layer (BR-TEN-01). |
| Error Conditions | ERR-TEN-001-01: Provisioning failure → rollback + alert. |
| Priority / Estimate | Must / L |
| Dependencies | REQ-CMP-001, REQ-USR-001 |
| Acceptance Criteria | **AC-REQ-TEN-001-01:** Tenant live < 15 min (FR-TEN-01). **AC-REQ-TEN-001-02:** Data isolation enforced (BR-TEN-01). |
| Status | Draft |

#### REQ-TEN-002 — Tenant Configuration Layer

| Field | Detail |
|-------|--------|
| Description | The system shall support tenant-level configuration (tax, currency, units, language, policies) via a versioned, auditable configuration layer (FR-TEN-02, BR-TEN-03). |
| Actors | UC-08, UC-10 |
| Preconditions | Tenant provisioned. |
| Postconditions | Config versioned/audited. |
| Main Flow | 1. Change config. 2. Version. 3. Audit. 4. Apply. |
| Alternative Flows | 2a. Invalid config → rejected. |
| Business Rules | BR-TEN-03 |
| Validation Rules | Config changes versioned + audited. |
| Error Conditions | ERR-TEN-002-01: Invalid → rejected. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-TEN-001 |
| Acceptance Criteria | **AC-REQ-TEN-002-01:** Config versioned/auditable (BR-TEN-03). |
| Status | Draft |

#### REQ-TEN-003 — Tenant Health Dashboard & Scoring

| Field | Detail |
|-------|--------|
| Description | The system shall compute a tenant health score daily (usage, errors, license, billing health) with configurable alerts (FR-TEN-03; see REQ-DASH-004). |
| Actors | UC-09, UC-10 |
| Preconditions | Tenant active. |
| Postconditions | Score stored; alerts raised. |
| Main Flow | 1. Collect telemetry. 2. Score. 3. Alert. |
| Alternative Flows | 2a. Insufficient data → "insufficient data" mark. |
| Business Rules | FR-TEN-03, BR-SUB-01 |
| Validation Rules | Deterministic scoring inputs. |
| Error Conditions | ERR-TEN-003-01: None. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-SUB-001 |
| Acceptance Criteria | **AC-REQ-TEN-003-01:** Daily health score stored; alerts configured (FR-TEN-03). |
| Status | Draft |

#### REQ-TEN-004 — Tenant Data Export

| Field | Detail |
|-------|--------|
| Description | The system shall export full tenant data on request and at offboarding within 24 h in a documented format (FR-TEN-04, BR-SUB-06, NFR-N-15). |
| Actors | UC-09, UC-10 |
| Preconditions | Tenant data exists. |
| Postconditions | Export delivered. |
| Main Flow | 1. Request. 2. Generate. 3. Deliver (≤ 24 h). |
| Alternative Flows | 3a. Large tenant → staged/async with notification. |
| Business Rules | BR-SUB-06, NFR-N-15 |
| Validation Rules | Export complete + documented format. |
| Error Conditions | ERR-TEN-004-01: Failure → retry + alert. |
| Priority / Estimate | Must / L |
| Dependencies | REQ-AUD-001 |
| Acceptance Criteria | **AC-REQ-TEN-004-01:** Full export ≤ 24 h (FR-TEN-04, KPI-21). |
| Status | Draft |

#### REQ-TEN-005 — Feature Flags per Tenant/Plan

| Field | Detail |
|-------|--------|
| Description | The system shall support feature flags enabling capabilities per tenant/plan without release (FR-AI-03, BR-TEN-02). |
| Actors | UC-10 |
| Preconditions | Flag infrastructure. |
| Postconditions | Flags applied. |
| Main Flow | 1. Define flag. 2. Assign to tenant/plan. 3. Enforce. |
| Alternative Flows | 3a. Rollback → flag off immediately. |
| Business Rules | BR-TEN-02, FR-AI-03 |
| Validation Rules | Entitlement + flag enforced. |
| Error Conditions | ERR-TEN-005-01: None. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-TEN-002 |
| Acceptance Criteria | **AC-REQ-TEN-005-01:** Capability rollout via flags without release (FR-AI-03). |
| Status | Draft |

#### REQ-TEN-006 — Market-Pack Activation per Tenant

| Field | Detail |
|-------|--------|
| Description | A tenant shall have at least one active market pack before live transactions; mixing packs requires explicit approval; activation audited (BR-LOC-02, P17). |
| Actors | UC-10, UC-08 |
| Preconditions | Pack validated (REQ-CMP-001). |
| Postconditions | Pack active; transactions permitted. |
| Main Flow | 1. Select pack. 2. Validate. 3. Apply defaults. 4. Activate (audited). |
| Alternative Flows | 4a. Mixed packs → explicit approval (BR-LOC-02). |
| Business Rules | BR-LOC-02, BR-PLUG-02 |
| Validation Rules | No live transactions without active pack (BR-LOC-02). |
| Error Conditions | ERR-TEN-006-01: No pack → live transactions blocked. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-CMP-001 |
| Acceptance Criteria | **AC-REQ-TEN-006-01:** Live transactions require active pack (BR-LOC-02). **AC-REQ-TEN-006-02:** Activation audited. |
| Status | Draft |

---

## 3.18 MOD-18 — Marketplace Readiness

### 3.18.1 Module Overview

| Attribute | Detail |
|-----------|--------|
| Module Name | Marketplace Readiness |
| Business Goal | Design the platform for ecosystem revenue (B2B ordering hub, add-on catalog, partner API + sandbox) with zero core rework when Marketplace launches (BRD Phase 6, FR-MKT-01/02). |
| Description | Readiness foundations: documented partner API, sandbox environment, add-on catalog lifecycle, and B2B ordering hooks. Active productization is Phase 6. |
| Business Value | Ecosystem revenue (BO-08, KPI-06/07 expansion); third-party app ecosystem (STK-21). |
| Target Users | UC-10 (platform), future ISV partners |
| Dependencies | API-requirements, SUB (add-on purchase), AI (data products) |
| Priority | Won't-now (product), Must (design-in) |
| Source / Trace | BRD FR-MKT-01/02, Roadmap Phase 6, OP-05 |

### 3.18.2 Requirements Catalog

| ID | Requirement | Priority | Estimate | Dependencies | BRD Trace |
|----|-------------|----------|----------|--------------|-----------|
| REQ-MKT-001 | Partner API & Sandbox (design-in) | Must | L | API standards | FR-MKT-01 |
| REQ-MKT-002 | Add-On Catalog Lifecycle | Should | M | SUB-001 | FR-MKT-02, FR-SUB-01 |
| REQ-MKT-003 | B2B Ordering Hooks (design-in) | Should | M | PUR, SUP | OP-05, Roadmap Phase 6 |
| REQ-MKT-004 | API Versioning & Governance | Must | M | MKT-001 | API-requirements, FR-MKT-01 |

### 3.18.3 Detailed Requirements

#### REQ-MKT-001 — Partner API & Sandbox

| Field | Detail |
|-------|--------|
| Description | The system shall expose a documented partner API and sandbox environment for third-party add-ons and B2B ordering; contract versioned; sandbox self-service by Phase 6 (FR-MKT-01). |
| Actors | UC-10, external ISVs |
| Preconditions | API gateway + sandbox exist. |
| Postconditions | Partners develop against versioned contract. |
| Main Flow | 1. Publish contract. 2. Provision sandbox. 3. Partner integrates. |
| Alternative Flows | 2a. Sandbox quota → enforced. |
| Business Rules | FR-MKT-01 |
| Validation Rules | Contract versioned; sandbox isolated. |
| Error Conditions | ERR-MKT-001-01: None. |
| Priority / Estimate | Must / L |
| Dependencies | Section 7 API requirements |
| Acceptance Criteria | **AC-REQ-MKT-001-01:** Documented versioned API + sandbox (FR-MKT-01). |
| Status | Draft |

#### REQ-MKT-002 — Add-On Catalog Lifecycle

| Field | Detail |
|-------|--------|
| Description | The system shall support a catalog of add-ons purchasable within subscription, with lifecycle tied to plans (FR-MKT-02, FR-SUB-01). |
| Actors | UC-08, UC-10 |
| Preconditions | Add-ons defined. |
| Postconditions | Add-ons purchased/enforced. |
| Main Flow | 1. Define add-on. 2. Publish. 3. Purchase. 4. Enforce. |
| Alternative Flows | 3a. Not in plan → upgrade path. |
| Business Rules | FR-MKT-02, BR-TEN-02 |
| Validation Rules | Add-on lifecycle via subscription entitlement. |
| Error Conditions | ERR-MKT-002-01: None. |
| Priority / Estimate | Should / M |
| Dependencies | REQ-SUB-001 |
| Acceptance Criteria | **AC-REQ-MKT-002-01:** Add-on purchase/enforcement via subscription (FR-MKT-02). |
| Status | Draft |

#### REQ-MKT-003 — B2B Ordering Hooks

| Field | Detail |
|-------|--------|
| Description | (Design-in) The system shall model supplier-customer ordering relationships to enable the B2B ordering hub without rework (OP-05, Phase 6). |
| Actors | UC-10 |
| Preconditions | Supplier/customer models exist. |
| Postconditions | B2B flow buildable. |
| Main Flow | 1. Design-in ordering relations. 2. Phase 6 productizes. |
| Alternative Flows | None. |
| Business Rules | FR-MKT-01 |
| Validation Rules | Data model supports ordering relationships. |
| Error Conditions | ERR-MKT-003-01: None. |
| Priority / Estimate | Should / M |
| Dependencies | REQ-PUR-001, REQ-SUP-001 |
| Acceptance Criteria | **AC-REQ-MKT-003-01:** Data model supports B2B ordering (design-in). |
| Status | Draft |

#### REQ-MKT-004 — API Versioning & Governance

| Field | Detail |
|-------|--------|
| Description | The system shall maintain versioned API contracts with deprecation policy and governance (Section 7; FR-MKT-01). |
| Actors | UC-10 |
| Preconditions | API published. |
| Postconditions | Contract stable per version. |
| Main Flow | 1. Version. 2. Deprecate. 3. Govern. |
| Alternative Flows | None. |
| Business Rules | API-requirements |
| Validation Rules | Backward compatibility per policy. |
| Error Conditions | ERR-MKT-004-01: None. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-MKT-001 |
| Acceptance Criteria | **AC-REQ-MKT-004-01:** Versioned contracts with deprecation policy. |
| Status | Draft |

---

## 3.19 MOD-19 — AI Readiness

### 3.19.1 Module Overview

| Attribute | Detail |
|-----------|--------|
| Module Name | AI Readiness |
| Business Goal | Persist data in an append-only, analytics-ready model and expose demand/price/margin signals so intelligence products (forecasting, anomaly detection, insights) can be added without re-architecture (BRD FR-AI-01..03, Phase 5). |
| Description | Data-model and API foundations: no destructive updates, structured analytics-ready persistence, demand/price/margin history APIs, and feature-flagged AI rollout. |
| Business Value | Expansion revenue (OP-04); differentiated value; measured improvements in stock availability/margin (Phase 5 gate). |
| Target Users | UC-10, future data science |
| Dependencies | All transactional modules, DB requirements |
| Priority | Must (foundations), Won't-now (products) |
| Source / Trace | BRD FR-AI-01..03, FR-AI-02, Phase 5, OP-04 |

### 3.19.2 Requirements Catalog

| ID | Requirement | Priority | Estimate | Dependencies | BRD Trace |
|----|-------------|----------|----------|--------------|-----------|
| REQ-AI-001 | Append-Only Analytics-Ready Data Model | Must | L | DB requirements | FR-AI-01, BR-AUD-01 |
| REQ-AI-002 | Demand/Price/Margin History APIs | Must | M | AI-001 | FR-AI-02 |
| REQ-AI-003 | Feature-Flagged AI Rollout | Must | M | TEN-005 | FR-AI-03 |
| REQ-AI-004 | Demand-Signal Persistence (sales velocity, seasonality) | Must | M | AI-001 | FR-INV-03, Phase 5 |
| REQ-AI-005 | AI Product Roadmap Interfaces | Should | M | AI-002..004 | Phase 5, OP-04 |

### 3.19.3 Detailed Requirements

#### REQ-AI-001 — Append-Only Analytics-Ready Data Model

| Field | Detail |
|-------|--------|
| Description | The system shall persist all transaction and master data in a structured, analytics-ready model with no destructive updates (append/audit); no data loss on update; history preserved (FR-AI-01). |
| Actors | System |
| Preconditions | Transaction data exists. |
| Postconditions | History immutable; analytics queries possible. |
| Main Flow | 1. Write events append-only. 2. Version states. 3. Preserve history. |
| Alternative Flows | 2a. Correction → new event, never overwrite (BR-ACC-03 pattern). |
| Business Rules | FR-AI-01, BR-AUD-01 |
| Validation Rules | No destructive updates. |
| Error Conditions | ERR-AI-001-01: Overwrite attempt → rejected. |
| Priority / Estimate | Must / L |
| Dependencies | Section 10 DB requirements |
| Acceptance Criteria | **AC-REQ-AI-001-01:** No data loss on update; history preserved (FR-AI-01). |
| Status | Draft |

#### REQ-AI-002 — Demand/Price/Margin History APIs

| Field | Detail |
|-------|--------|
| Description | The system shall expose demand and price/margin history APIs suitable for forecasting and insight modules; contract documented by Phase 5 (FR-AI-02). |
| Actors | UC-10, data science |
| Preconditions | Data present. |
| Postconditions | API available. |
| Main Flow | 1. Expose. 2. Document. 3. Consume. |
| Alternative Flows | None. |
| Business Rules | FR-AI-02 |
| Validation Rules | Contract documented. |
| Error Conditions | ERR-AI-002-01: None. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-AI-001 |
| Acceptance Criteria | **AC-REQ-AI-002-01:** API contract documented by Phase 5 (FR-AI-02). |
| Status | Draft |

#### REQ-AI-003 — Feature-Flagged AI Rollout

| Field | Detail |
|-------|--------|
| Description | AI capabilities shall roll out per tenant/plan via feature flags without release (FR-AI-03; REQ-TEN-005). |
| Actors | UC-10 |
| Preconditions | Flags infrastructure. |
| Postconditions | AI features gated. |
| Main Flow | 1. Flag AI feature. 2. Enable per tenant/plan. 3. Enforce. |
| Alternative Flows | 3a. Disable → rollback. |
| Business Rules | FR-AI-03 |
| Validation Rules | Flag enforced. |
| Error Conditions | ERR-AI-003-01: None. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-TEN-005 |
| Acceptance Criteria | **AC-REQ-AI-003-01:** AI rollout via flags without release (FR-AI-03). |
| Status | Draft |

#### REQ-AI-004 — Demand-Signal Persistence

| Field | Detail |
|-------|--------|
| Description | The system shall persist demand signals (sales velocity, seasonality, min/max) in structured form for forecasting use (FR-INV-03, Phase 5). |
| Actors | System |
| Preconditions | Sales data present. |
| Postconditions | Signals persisted. |
| Main Flow | 1. Compute signals. 2. Persist. 3. Consume. |
| Alternative Flows | None. |
| Business Rules | FR-INV-03 |
| Validation Rules | Signals derived from posted data. |
| Error Conditions | ERR-AI-004-01: None. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-AI-001 |
| Acceptance Criteria | **AC-REQ-AI-004-01:** Demand signals persisted and available. |
| Status | Draft |

#### REQ-AI-005 — AI Product Roadmap Interfaces

| Field | Detail |
|-------|--------|
| Description | (Should) The system shall provide interfaces for Phase 5 AI products: demand forecasting with confidence, expiry-write-off prediction, anomaly detection, optimization recommendations, natural-language dashboards (BRD Phase 5). |
| Actors | UC-10, data science |
| Preconditions | Phase 5. |
| Postconditions | AI products implementable. |
| Main Flow | 1. Interface contracts. 2. Models. 3. Rollout. |
| Alternative Flows | None. |
| Business Rules | Phase 5 gates |
| Validation Rules | ≥ 30% tenant AI usage at Phase 5 gate. |
| Error Conditions | ERR-AI-005-01: None. |
| Priority / Estimate | Should / M |
| Dependencies | REQ-AI-002..004 |
| Acceptance Criteria | **AC-REQ-AI-005-01 (Phase 5):** AI interfaces support Phase 5 deliverables. |
| Status | Deferred |

---

## 3.20 MOD-20 — Compliance & Market Packs

### 3.20.1 Module Overview

| Attribute | Detail |
|-----------|--------|
| Module Name | Compliance & Market Packs |
| Business Goal | Deliver all market-specific regulatory/tax/commercial behavior via versioned, isolated, sandbox-validated market packs on a country-neutral core (BRD P17, FR-LOC-01/05..07, BR-LOC/PLUG/TAX). |
| Description | The plugin framework is the compliance backbone: packs define tax, e-invoicing, currency, language, calendar, drug reference, Rx mode, controlled-substance registers, and health-authority reports. Packs cannot modify core or access other packs (BR-PLUG-01/02). |
| Business Value | One core, many markets (OP-11); contains regulatory risk (RK-15/16/19); converts compliance into a selling point (OP-01). |
| Target Users | UC-10, UC-08 |
| Dependencies | TEN, CMP infrastructure, AUD |
| Priority | Must |
| Source / Trace | BRD FR-LOC-01/05..07, P17, BR-LOC-01..04, BR-PLUG-01/02, BR-CUR-01/02, BR-TAX-03, NFR-N-19 |

### 3.20.2 Requirements Catalog

| ID | Requirement | Priority | Estimate | Dependencies | BRD Trace |
|----|-------------|----------|----------|--------------|-----------|
| REQ-CMP-001 | Market Pack Framework (country-neutral core) | Must | XL | TEN | FR-LOC-01, BR-LOC-01 |
| REQ-CMP-002 | Pack Isolation & Versioned Activation | Must | L | CMP-001 | BR-PLUG-01/02, NFR-N-19 |
| REQ-CMP-003 | Tax Engine & E-Invoicing via Pack | Must | XL | CMP-001 | FR-ACC-05, BR-TAX-03, FR-LOC-05 |
| REQ-CMP-004 | Privacy Regime per Market | Must | L | CMP-001 | BR-PRIV-01, NFR-N-06 |
| REQ-CMP-005 | Rx Mode Adapters (paper/digital) | Must | M | CMP-001 | FR-RX-05, BR-LOC-01 |
| REQ-CMP-006 | National Drug Reference & Barcode Mapping | Must | L | CMP-001 | FR-LOC-06 |
| REQ-CMP-007 | Controlled-Substance Register & Health-Authority Reports | Must | L | CMP-001 | FR-LOC-07, BR-CTL-01, FR-REP-04 |
| REQ-CMP-008 | Market-Pack Readiness Reporting | Must | M | CMP-001 | KPI-23, BRD §16 |

### 3.20.3 Detailed Requirements

#### REQ-CMP-001 — Market Pack Framework

| Field | Detail |
|-------|--------|
| Description | The system shall provide a localization & compliance plugin framework where each market pack defines tax, e-invoicing, currency, language, calendar, drug reference, Rx mode, and health-authority reporting; two packs (GCC, Yemen) activate without core changes (FR-LOC-01, BR-LOC-01). |
| Actors | UC-10 |
| Preconditions | Framework exists; pack built. |
| Postconditions | Pack activates; market behavior delivered. |
| Main Flow | 1. Build pack. 2. Validate in sandbox. 3. Activate per tenant. 4. Deliver market behavior. |
| Alternative Flows | 2a. Validation failure → activation blocked. |
| Business Rules | BR-LOC-01, BR-PLUG-02 |
| Validation Rules | Core stays country-neutral; pack delivers all market behavior. |
| Error Conditions | ERR-CMP-001-01: Pack requires core change → rejected by design. |
| Priority / Estimate | Must / XL |
| Dependencies | REQ-TEN-001 |
| Acceptance Criteria | **AC-REQ-CMP-001-01:** Two packs (GCC, Yemen) activate with no core changes (FR-LOC-01). **AC-REQ-CMP-001-02:** Zero country-specific core code (BR-LOC-01). |
| Status | Draft |

#### REQ-CMP-002 — Pack Isolation & Versioned Activation

| Field | Detail |
|-------|--------|
| Description | A market pack shall not access another pack's configuration/data; isolation enforced at runtime; pack updates versioned, sandbox-validated, and audited before activation; a pack change shall not alter the core (BR-PLUG-01/02, NFR-N-19). |
| Actors | UC-10 |
| Preconditions | Pack exists. |
| Postconditions | Isolation verified; updates governed. |
| Main Flow | 1. Version pack. 2. Sandbox validation. 3. Audit activation. 4. Run isolated. |
| Alternative Flows | 3a. Failed validation → blocked. |
| Business Rules | BR-PLUG-01, BR-PLUG-02 |
| Validation Rules | Isolation tests pass; compromised pack cannot access others (NFR-N-19). |
| Error Conditions | ERR-CMP-002-01: Isolation breach → pack disabled + alert. |
| Priority / Estimate | Must / L |
| Dependencies | REQ-CMP-001 |
| Acceptance Criteria | **AC-REQ-CMP-002-01:** Pack isolation enforced at runtime (BR-PLUG-01). **AC-REQ-CMP-002-02:** Updates versioned + audited (BR-PLUG-02). |
| Status | Draft |

#### REQ-CMP-003 — Tax Engine & E-Invoicing via Pack

| Field | Detail |
|-------|--------|
| Description | The active market pack shall provide the tax engine (rates, exemptions, computation) and e-invoicing adapter (e.g., ZATCA Phase 2); invoice issued only after validated transmission (FR-ACC-05, FR-LOC-05, BR-TAX-03). |
| Actors | UC-10, UC-06 |
| Preconditions | Pack active. |
| Postconditions | Tax computed per pack; e-invoicing enforced. |
| Main Flow | 1. Pack supplies rates. 2. POS/ACC compute. 3. E-invoice validated + transmitted. 4. Issue. |
| Alternative Flows | 4a. Transmission failure → block issue (BR-TAX-03). |
| Business Rules | BR-TAX-01, BR-TAX-03, BR-LOC-01 |
| Validation Rules | Rate engine from pack; e-invoice per pack spec. |
| Error Conditions | ERR-CMP-003-01: E-invoice failure → blocked (BR-TAX-03). |
| Priority / Estimate | Must / XL |
| Dependencies | REQ-CMP-001 |
| Acceptance Criteria | **AC-REQ-CMP-003-01:** Tax rates from active pack. **AC-REQ-CMP-003-02:** E-invoicing enforced where required (BR-TAX-03). |
| Status | Draft |

#### REQ-CMP-004 — Privacy Regime per Market

| Field | Detail |
|-------|--------|
| Description | The system shall handle patient-linked data per the configured privacy regime of the active market, with consent records (BR-PRIV-01, NFR-N-06). |
| Actors | UC-10 |
| Preconditions | Pack defines regime. |
| Postconditions | Privacy controls enforced. |
| Main Flow | 1. Pack defines regime. 2. System enforces. 3. Consent recorded. |
| Alternative Flows | 2a. Cross-border rules → hosting flag. |
| Business Rules | BR-PRIV-01, NFR-N-06 |
| Validation Rules | Access + export consent-scoped. |
| Error Conditions | ERR-CMP-004-01: Violation → blocked + alert. |
| Priority / Estimate | Must / L |
| Dependencies | REQ-CMP-001 |
| Acceptance Criteria | **AC-REQ-CMP-004-01:** Privacy regime enforced per market (BR-PRIV-01). |
| Status | Draft |

#### REQ-CMP-005 — Rx Mode Adapters

| Field | Detail |
|-------|--------|
| Description | The system shall support paper and digital prescription modes through adapters per market pack (FR-RX-05, BR-LOC-01). |
| Actors | UC-10 |
| Preconditions | Pack defines mode. |
| Postconditions | Rx module supports market mode. |
| Main Flow | 1. Pack adapter. 2. Rx uses. 3. Validate. |
| Alternative Flows | 2a. Adapter stub → interface documented (FR-RX-05). |
| Business Rules | FR-RX-05, BR-LOC-01 |
| Validation Rules | No core change for new Rx mode. |
| Error Conditions | ERR-CMP-005-01: None. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-CMP-001 |
| Acceptance Criteria | **AC-REQ-CMP-005-01:** Rx modes via pack adapters (FR-RX-05). |
| Status | Draft |

#### REQ-CMP-006 — National Drug Reference & Barcode Mapping

| Field | Detail |
|-------|--------|
| Description | The active pack shall map national drug-registration codes and GS1/SFDA-aligned barcodes; national code captured/searchable; barcode scan resolves per pack (FR-LOC-06). |
| Actors | UC-10 |
| Preconditions | Pack reference data available. |
| Postconditions | Codes/barcodes resolve per market. |
| Main Flow | 1. Pack provides reference schema/data. 2. Products mapped. 3. Scans resolve. |
| Alternative Flows | 2a. Reference import (REQ-MED-007). |
| Business Rules | FR-LOC-06, BR-LOC-01 |
| Validation Rules | Resolution per active pack. |
| Error Conditions | ERR-CMP-006-01: Unresolved code → prompt. |
| Priority / Estimate | Must / L |
| Dependencies | REQ-CMP-001, REQ-MED-006 |
| Acceptance Criteria | **AC-REQ-CMP-006-01:** National code capture/searchable; barcodes resolve per pack (FR-LOC-06). |
| Status | Draft |

#### REQ-CMP-007 — Controlled-Substance Register & Health-Authority Reports

| Field | Detail |
|-------|--------|
| Description | The active pack shall provide the controlled-substance register schema and health-authority report adapters; exports validated against pack spec (FR-LOC-07, BR-CTL-01, FR-REP-04). |
| Actors | UC-10, UC-02 |
| Preconditions | Pack active. |
| Postconditions | Register/reports per market. |
| Main Flow | 1. Pack schema. 2. Register maintained. 3. Reports exported per spec. |
| Alternative Flows | 3a. Format change → pack update (versioned). |
| Business Rules | FR-LOC-07, BR-CTL-01, BR-PLUG-02 |
| Validation Rules | Export validated against pack spec. |
| Error Conditions | ERR-CMP-007-01: Invalid export → blocked. |
| Priority / Estimate | Must / L |
| Dependencies | REQ-CMP-001 |
| Acceptance Criteria | **AC-REQ-CMP-007-01:** Register/report formats per pack (FR-LOC-07). |
| Status | Draft |

#### REQ-CMP-008 — Market-Pack Readiness Reporting

| Field | Detail |
|-------|--------|
| Description | The system shall report market-pack readiness: 100% of pack controls mapped, validated, and tested before that market's go-live (KPI-23). |
| Actors | UC-10 |
| Preconditions | Pack in validation. |
| Postconditions | Readiness score computed. |
| Main Flow | 1. Map controls. 2. Validate. 3. Test. 4. Score. |
| Alternative Flows | 3a. Failures → list. |
| Business Rules | KPI-23 |
| Validation Rules | 100% readiness required before go-live. |
| Error Conditions | ERR-CMP-008-01: None. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-CMP-001 |
| Acceptance Criteria | **AC-REQ-CMP-008-01:** Readiness = 100% before go-live (KPI-23). |
| Status | Draft |

---

## 3.21 MOD-21 — Settings & Configuration

### 3.21.1 Module Overview

| Attribute | Detail |
|-----------|--------|
| Module Name | Settings & Configuration |
| Business Goal | Centralize tenant configuration (language, currency, calendar, numbering, policies, thresholds, devices) with versioned, audited changes (BRD FR-TEN-02, FR-LOC-02..04, BR-LOC/CUR). |
| Description | Configuration layer surfacing tenant and market-pack settings to authorized users; feeds all modules (policies, thresholds, defaults, formats). |
| Business Value | Configuration-over-customization (OOS-11); localization correctness; policy enforcement. |
| Target Users | UC-08, UC-10 |
| Dependencies | TEN, CMP |
| Priority | Must |
| Source / Trace | BRD FR-TEN-02, FR-LOC-02..04, BR-LOC-02..04, BR-CUR-01/02, BR-TEN-03 |

### 3.21.2 Requirements Catalog

| ID | Requirement | Priority | Estimate | Dependencies | BRD Trace |
|----|-------------|----------|----------|--------------|-----------|
| REQ-SET-001 | Language & Locale Settings (AR RTL / EN) | Must | M | CMP-001 | FR-LOC-02, BR-LOC-03 |
| REQ-SET-002 | Calendar Display Settings (Gregorian/Hijri) | Must | S | SET-001 | FR-LOC-04, BR-LOC-04 |
| REQ-SET-003 | Currency & Numbering Settings | Must | M | CMP-003 | FR-LOC-03, BR-CUR-01/02 |
| REQ-SET-004 | Policy & Threshold Configuration | Must | M | TEN-002 | BR-SAL-02, BR-STK-04, BR-AUTH-01 |
| REQ-SET-005 | Operational Targets & Preferences | Should | S | SET-004 | DASH-003, FR-TEN-02 |
| REQ-SET-006 | Device & Peripheral Configuration | Must | M | SET-004 | BRD CN-05, NFR-N-10 |

### 3.21.3 Detailed Requirements

#### REQ-SET-001 — Language & Locale Settings

| Field | Detail |
|-------|--------|
| Description | The system shall support Arabic (RTL) and English interfaces with correct mixed-script rendering (Latin drug names in Arabic UI); language switch without code change (FR-LOC-02, BR-LOC-03, NFR-N-17). |
| Actors | UC-08, users |
| Preconditions | Packs active. |
| Postconditions | UI renders correctly in chosen language. |
| Main Flow | 1. Choose language. 2. System renders. 3. Mixed-script correct. |
| Alternative Flows | 2a. New language → pack (NFR-N-11). |
| Business Rules | BR-LOC-03 |
| Validation Rules | Arabic RTL + English LTR; mixed-script tests pass. |
| Error Conditions | ERR-SET-001-01: Rendering defect → QA bound (RK-18). |
| Priority / Estimate | Must / M |
| Dependencies | REQ-CMP-001 |
| Acceptance Criteria | **AC-REQ-SET-001-01:** All core screens render correctly in both languages (BR-LOC-03). |
| Status | Draft |

#### REQ-SET-002 — Calendar Display Settings

| Field | Detail |
|-------|--------|
| Description | Business dates stored canonically; display Gregorian or Hijri per tenant preference without altering business logic (FR-LOC-04, BR-LOC-04). |
| Actors | UC-08 |
| Preconditions | Dates stored canonically. |
| Postconditions | Display calendars supported. |
| Main Flow | 1. Choose calendar. 2. Render. 3. Rules use canonical dates. |
| Alternative Flows | None. |
| Business Rules | BR-LOC-04 |
| Validation Rules | Date-based rules use canonical dates. |
| Error Conditions | ERR-SET-002-01: None. |
| Priority / Estimate | Must / S |
| Dependencies | REQ-SET-001 |
| Acceptance Criteria | **AC-REQ-SET-002-01:** Both calendars render; rules use canonical dates (BR-LOC-04). |
| Status | Draft |

#### REQ-SET-003 — Currency & Numbering Settings

| Field | Detail |
|-------|--------|
| Description | The system shall set tenant base currency and optional secondary currency (USD), capture rates, revalue consistently, and audit rates (FR-LOC-03, BR-CUR-01/02). |
| Actors | UC-08 |
| Preconditions | Tenant configured. |
| Postconditions | Multi-currency supported. |
| Main Flow | 1. Set base currency. 2. Set secondary. 3. Rates captured. 4. Reporting. |
| Alternative Flows | 3a. Volatile rate (Yemen) → rate audit + revaluation policy (RK-17). |
| Business Rules | BR-CUR-01/02 |
| Validation Rules | Transactions in base; rates audited. |
| Error Conditions | ERR-SET-003-01: Missing rate → blocked. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-CMP-003 |
| Acceptance Criteria | **AC-REQ-SET-003-01:** Base + secondary currency reporting consistent (BR-CUR-02). |
| Status | Draft |

#### REQ-SET-004 — Policy & Threshold Configuration

| Field | Detail |
|-------|--------|
| Description | The system shall allow configuration of operational policies and thresholds (discount max, approval thresholds, expiry thresholds, authorization limits) per tenant/branch (BR-SAL-02, BR-STK-04, BR-AUTH-01, BR-TEN-03). |
| Actors | UC-08, UC-07 |
| Preconditions | Tenant configured. |
| Postconditions | Policies enforced. |
| Main Flow | 1. Configure. 2. Version. 3. Enforce. |
| Alternative Flows | 2a. Invalid range → rejected. |
| Business Rules | BR-SAL-02, BR-STK-04, BR-AUTH-01 |
| Validation Rules | Config versioned/audited (BR-TEN-03). |
| Error Conditions | ERR-SET-004-01: Invalid → rejected. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-TEN-002 |
| Acceptance Criteria | **AC-REQ-SET-004-01:** Policies/thresholds configurable + enforced. |
| Status | Draft |

#### REQ-SET-005 — Operational Targets & Preferences

| Field | Detail |
|-------|--------|
| Description | The system shall allow configuration of operational targets (sales targets, comparison baselines) for head-office dashboards (DASH-003, FR-TEN-02). |
| Actors | UC-07, UC-08 |
| Preconditions | Chain tenant. |
| Postconditions | Targets used in comparisons. |
| Main Flow | 1. Set targets. 2. Compare. |
| Alternative Flows | None. |
| Business Rules | FR-TEN-02 |
| Validation Rules | Targets optional. |
| Error Conditions | ERR-SET-005-01: None. |
| Priority / Estimate | Should / S |
| Dependencies | REQ-SET-004 |
| Acceptance Criteria | **AC-REQ-SET-005-01:** Targets drive head-office comparisons. |
| Status | Draft |

#### REQ-SET-006 — Device & Peripheral Configuration

| Field | Detail |
|-------|--------|
| Description | The system shall support device/peripheral configuration (receipt printer, scanner, cash drawer, QR) via a device abstraction layer (BRD CN-05, NFR-N-10). |
| Actors | UC-08 |
| Preconditions | Devices certified. |
| Postconditions | Devices operational. |
| Main Flow | 1. Register device. 2. Configure. 3. Use in POS. |
| Alternative Flows | 2a. Uncertified device → warning. |
| Business Rules | NFR-N-10 |
| Validation Rules | Peripheral abstraction enforced. |
| Error Conditions | ERR-SET-006-01: Device failure → fallback. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-POS-005 |
| Acceptance Criteria | **AC-REQ-SET-006-01:** Certified devices integrate via abstraction layer (NFR-N-10). |
| Status | Draft |

---

## 3.22 MOD-22 — Audit Log

### 3.22.1 Module Overview

| Attribute | Detail |
|-----------|--------|
| Module Name | Audit Log |
| Business Goal | Record every create/update/delete and privileged action of financial, stock, prescription, controlled-substance, and permission data immutably, with export for forensic review (BRD FR-USR-03, BR-AUD-01). |
| Description | Immutable audit service: captures user, timestamp, before/after values, IP/device; supports query, export (< 60 s for 90-day scope), and retention per policy. |
| Business Value | Regulatory trust (BO-07); forensic capability; feeds AI-readiness (FR-AI-01). |
| Target Users | UC-08, UC-10, UC-02 (view) |
| Dependencies | All modules |
| Priority | Must |
| Source / Trace | BRD FR-USR-03, BR-AUD-01, BR-SEC-03, P14, NFR-N-07, KPI-13 |

### 3.22.2 Requirements Catalog

| ID | Requirement | Priority | Estimate | Dependencies | BRD Trace |
|----|-------------|----------|----------|--------------|-----------|
| REQ-AUD-001 | Immutable Audit Capture | Must | L | All modules | BR-AUD-01, KPI-13 |
| REQ-AUD-002 | Audit Query & Forensic Export | Must | M | AUD-001 | FR-USR-03, NFR-N-07 |
| REQ-AUD-003 | Audit Retention & Archiving | Must | M | AUD-001 | NFR-N-14 |
| REQ-AUD-004 | Audit Integrity & Tamper-Evidence | Must | M | AUD-001 | NFR-N-07, BR-AUD-01 |
| REQ-AUD-005 | Audit Event Taxonomy & Correlation | Must | M | AUD-001 | BR-AUD-01 |

### 3.22.3 Detailed Requirements

#### REQ-AUD-001 — Immutable Audit Capture

| Field | Detail |
|-------|--------|
| Description | All create/update/delete of financial, stock, prescription, controlled-substance, and permission data shall be recorded immutably with user, timestamp, before/after values, and IP/device (BR-AUD-01); 100% mandated events captured (KPI-13). |
| Actors | System |
| Preconditions | Event occurs. |
| Postconditions | Audit record immutable. |
| Main Flow | 1. Event. 2. Capture. 3. Write immutable. 4. Verify. |
| Alternative Flows | 2a. Capture failure → blocking alert (no silent loss). |
| Business Rules | BR-AUD-01 |
| Validation Rules | 100% capture of mandated events. |
| Error Conditions | ERR-AUD-001-01: Capture failure → alert. |
| Priority / Estimate | Must / L |
| Dependencies | All modules |
| Acceptance Criteria | **AC-REQ-AUD-001-01:** 100% mandated events logged (KPI-13). **AC-REQ-AUD-001-02:** Records immutable (BR-AUD-01). |
| Status | Draft |

#### REQ-AUD-002 — Audit Query & Forensic Export

| Field | Detail |
|-------|--------|
| Description | The system shall support audit query and forensic export with before/after values; export < 60 s for 90-day scope (FR-USR-03, NFR-N-07). |
| Actors | UC-08, UC-10 |
| Preconditions | Audit data present. |
| Postconditions | Export delivered. |
| Main Flow | 1. Query. 2. Filter. 3. Export. |
| Alternative Flows | 2a. Large scope → async. |
| Business Rules | BR-AUD-01 |
| Validation Rules | Export complete + time-stamped. |
| Error Conditions | ERR-AUD-002-01: Export > 60 s → bound. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-AUD-001 |
| Acceptance Criteria | **AC-REQ-AUD-002-01:** Export < 60 s for 90-day scope (NFR-N-07). |
| Status | Draft |

#### REQ-AUD-003 — Audit Retention & Archiving

| Field | Detail |
|-------|--------|
| Description | Audit records retained per regulatory/tenant policy with export capability (NFR-N-14); archiving preserves integrity. |
| Actors | UC-10 |
| Preconditions | Records exist. |
| Postconditions | Retention enforced. |
| Main Flow | 1. Retention schedule. 2. Archive. 3. Purge per policy. |
| Alternative Flows | 3a. Legal hold → excluded from purge. |
| Business Rules | NFR-N-14 |
| Validation Rules | Controlled/Rx records per legal minimum. |
| Error Conditions | ERR-AUD-003-01: None. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-AUD-001 |
| Acceptance Criteria | **AC-REQ-AUD-003-01:** Retention enforced; legal hold respected. |
| Status | Draft |

#### REQ-AUD-004 — Audit Integrity & Tamper-Evidence

| Field | Detail |
|-------|--------|
| Description | Audit records shall be tamper-evident (append-only with integrity checks); detection of tampering raises alerts (NFR-N-07, BR-AUD-01). |
| Actors | System |
| Preconditions | Audit active. |
| Postconditions | Integrity verified. |
| Main Flow | 1. Write. 2. Integrity chain. 3. Periodic verify. 4. Detect. |
| Alternative Flows | 4a. Tampering detected → alert + quarantine. |
| Business Rules | BR-AUD-01 |
| Validation Rules | Tamper-evidence verified. |
| Error Conditions | ERR-AUD-004-01: Integrity failure → alert. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-AUD-001 |
| Acceptance Criteria | **AC-REQ-AUD-004-01:** Audit tamper-evident; tampering detected. |
| Status | Draft |

#### REQ-AUD-005 — Audit Event Taxonomy & Correlation

| Field | Detail |
|-------|--------|
| Description | The system shall classify audit events (domain, action, severity) and support correlation (transaction → audit trail) for forensic analysis (BR-AUD-01). |
| Actors | UC-10 |
| Preconditions | Events exist. |
| Postconditions | Events classifiable/correlatable. |
| Main Flow | 1. Classify. 2. Correlate. 3. Analyze. |
| Alternative Flows | None. |
| Business Rules | BR-AUD-01 |
| Validation Rules | Taxonomy consistent. |
| Error Conditions | ERR-AUD-005-01: None. |
| Priority / Estimate | Must / M |
| Dependencies | REQ-AUD-001 |
| Acceptance Criteria | **AC-REQ-AUD-005-01:** Events classified + correlated. |
| Status | Draft |

---

# 4. Non-Functional Requirements

Non-functional requirements are binding quality commitments carried from BRD §12 and §16. Each NFR has a measurable target and maps to the BRD NFR/quality source. "Shall" statements here are contract-level and verified by QA/DevOps.

## 4.1 Performance (NFR-PERF)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-PERF-01 | Core transaction response (checkout, stock lookup, day-close). | Checkout < 2 s; stock/branch queries < 2 s at 100k stock lines; day-close < 10 s (p95). [BRD NFR-N-02] |
| NFR-PERF-02 | POS scan-to-cart latency. | < 1 s p95. [FR-POS-01] |
| NFR-PERF-03 | Product/customer search latency. | < 2 s p95. [FR-POS-01, FR-CUST-01] |
| NFR-PERF-04 | Report generation for 90-day data at tenant scale. | < 10 s p95. [FR-REP-01] |
| NFR-PERF-05 | Receipt generation. | < 3 s. [FR-POS-03] |
| NFR-PERF-06 | Dashboard render for 90 days of data. | ≤ 3 s p95. [REQ-DASH-001/002] |
| NFR-PERF-07 | Audit export for 90-day scope. | < 60 s. [NFR-N-07] |
| NFR-PERF-08 | No degradation > 10% at target concurrent load. | See NFR-SCAL-01. [NFR-N-03] |

## 4.2 Availability (NFR-AVAIL)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-AVAIL-01 | Platform availability during pharmacy operating windows. | ≥ 99.5% monthly. [BRD NFR-N-01, KPI-10] |
| NFR-AVAIL-02 | No scheduled maintenance during high-traffic hours. | Maintenance ≤ 4 h/month, outside 08:00–22:00 local. [BRD NFR-N-01, CN-03] |
| NFR-AVAIL-03 | Graceful degradation of non-critical features under load. | Read-only features available during partial failure; POS/stock always prioritized. |
| NFR-AVAIL-04 | Planned failover must not interrupt an active POS transaction. | Session continuity on failover. [NFR-N-08] |

## 4.3 Scalability (NFR-SCAL)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-SCAL-01 | Peak concurrent terminals per region. | ≥ 1,500 concurrent terminals/region with no degradation > 10%. [BRD NFR-N-03] |
| NFR-SCAL-02 | Horizontal scaling without per-tenant engineering. | Adding tenants/branches requires no code change; cost curve declining. [BRD NFR-N-04] |
| NFR-SCAL-03 | Data-volume scaling (100k+ stock lines, multi-branch). | Query targets in NFR-PERF hold at target scale. |
| NFR-SCAL-04 | Tenant growth economics. | Gross margin per tenant ≥ 70% at target scale. [BRD NFR-N-16, KPI-06] |

## 4.4 Reliability & Resilience (NFR-RELI)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-RELI-01 | Active transaction resilience. | Active sale survives 30 s connectivity loss; completes on reconnect; no silent data loss. [BRD NFR-N-08, FR-PH-05] |
| NFR-RELI-02 | No silent data loss in any transaction flow. | All writes acknowledged or explicitly failed; no partial commits outside transaction. |
| NFR-RELI-03 | Idempotency of retries. | Retried operations produce identical outcomes (idempotency keys). |
| NFR-RELI-04 | Processing integrity of background jobs (reports, billing, notifications). | Jobs retryable, resumable, and audited; no double-processing. |

## 4.5 Security (NFR-SEC)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-SEC-01 | Protection of tenant and patient data per market regime. | Encryption in transit (TLS ≥ 1.2) and at rest; RBAC enforced; penetration-tested before launch. [BRD NFR-N-05] |
| NFR-SEC-02 | Least-privilege access. | Default deny; explicit grant; enforced at server. [BRD NFR-N-05] |
| NFR-SEC-03 | OWASP ASVS compliance. | ASVS Level 1 baseline; Level 2 for auth/data handling. (Section 8) |
| NFR-SEC-04 | Plugin isolation security. | A compromised market pack cannot access other packs/tenants (isolation tests). [BRD NFR-N-19] |

## 4.6 Maintainability (NFR-MAINT)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-MAINT-01 | Configurability over customization. | No per-tenant custom code; all variation via configuration/packs. [BRD OOS-11, CN-01] |
| NFR-MAINT-02 | Module independence. | Module changes isolated; plugin framework does not modify core. [BRD BR-PLUG-02] |
| NFR-MAINT-03 | Standards-based code and API contract. | OpenAPI 3.1 contracts; documented conventions; CI quality gates. |

## 4.7 Portability (NFR-PORT)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-PORT-01 | Browser portability. | Evergreen Chrome, Edge, Firefox, Safari on desktop/tablet. |
| NFR-PORT-02 | Language portability. | New languages added via pack without code change. [BRD NFR-N-11/17, OOS-10] |
| NFR-PORT-03 | Data portability. | Full tenant export ≤ 24 h; documented format; no data-hostage model. [BRD NFR-N-15, KPI-21] |
| NFR-PORT-04 | Cloud portability. | Cloud-agnostic abstractions where feasible; no proprietary lock-in. |

## 4.8 Accessibility (NFR-ACC)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-ACC-01 | Keyboard operability. | All core functions reachable via keyboard. |
| NFR-ACC-02 | Screen-reader compatibility. | WCAG 2.1 AA for core flows (ARIA labels, contrast, focus states). |
| NFR-ACC-03 | Touch-first POS. | Touch targets ≥ 44×44 px on POS; reduced motion respected. |

## 4.9 Localization (NFR-LOC)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-LOC-01 | Arabic (RTL) and English support. | 100% core screens render correctly in both, incl. mixed-script Latin drug names in Arabic UI. [BRD BR-LOC-03, NFR-N-17] |
| NFR-LOC-02 | Canonical business dates with Gregorian/Hijri display. | Date rules use canonical dates; display switchable. [BRD BR-LOC-04] |
| NFR-LOC-03 | Multi-currency. | Base + secondary currency reporting; rate audit. [BRD BR-CUR-01/02, NFR-N-18] |
| NFR-LOC-04 | Number/date/format conventions per locale. | Per-pack formatting; no hard-coded formats in core. |
| NFR-LOC-05 | Arabic-first QA matrix. | Native-speaker UX review; bilingual test cases. [BRD RK-18, ST-13] |

## 4.10 Auditability (NFR-AUDIT)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-AUDIT-01 | Immutability and completeness of audit. | 100% mandated events captured; tamper-evident. [BRD BR-AUD-01, KPI-13] |
| NFR-AUDIT-02 | Audit export. | 90-day scope export < 60 s. [BRD NFR-N-07] |
| NFR-AUDIT-03 | Audit retention. | Configurable; controlled/Rx records at legal minimum. [BRD NFR-N-14] |

## 4.11 Observability, Logging, Monitoring (NFR-OBS)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-OBS-01 | Structured application logging. | Machine-parseable logs with correlation IDs; no sensitive data logged. |
| NFR-OBS-02 | Metrics and tracing. | Request traces, business metrics (sales rate, error rate, latency histograms), health probes. |
| NFR-OBS-03 | Alerting. | Alerts on SLO breaches (availability, latency), error spikes, tenant anomalies. |
| NFR-OBS-04 | Tenant telemetry for health scoring. | Usage/entitlement/error telemetry per tenant (feeds REQ-DASH-004). |
| NFR-OBS-05 | Log retention. | Operational logs retained per policy; audit logs per NFR-AUDIT-03. |

## 4.12 Data Integrity (NFR-DINT)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-DINT-01 | No negative stock from normal transactions. | Invariant enforced; corrections manager-approved. [BRD BR-STK-07] |
| NFR-DINT-02 | Balanced postings only. | Zero unbalanced double-entry postings. [BRD BR-ACC-01] |
| NFR-DINT-03 | Ledger–subledger reconciliation. | 0 unexplained variance after day-close. [BRD BR-ACC-02, KPI-14] |
| NFR-DINT-04 | Append-only history. | No destructive updates; corrections via reversing events. [BRD FR-AI-01, BR-ACC-03] |
| NFR-DINT-05 | Tenant isolation integrity. | No cross-tenant data access (tested). [BRD BR-TEN-01] |

## 4.13 Privacy (NFR-PRIV)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-PRIV-01 | Patient-data privacy per regime. | Consent records; role-scoped identity access; consent-scoped exports. [BRD BR-PRIV-01, NFR-N-06] |
| NFR-PRIV-02 | Data minimization. | Only pharmacy-scope patient data collected. [BRD OOS-08, AS-10] |
| NFR-PRIV-03 | Cross-border data flows. | Hosting/residency per market decision (DEC-05). [BRD CN-06] |

## 4.14 Compliance (NFR-CMP)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-CMP-01 | Rule enforcement completeness. | 100% of BR rules enforced in production code (BR compliance score). [BRD KPI-12] |
| NFR-CMP-02 | Market compliance readiness. | 100% pack controls mapped, validated, tested before go-live. [BRD KPI-23] |
| NFR-CMP-03 | Regulatory report completeness. | Compliance exports complete, time-stamped, per pack. [BRD FR-REP-04] |

## 4.15 Backup (NFR-BACK)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-BACK-01 | Scheduled backups. | Daily backups; RPO ≤ 24 h. [BRD NFR-N-12] |
| NFR-BACK-02 | Restore verification. | Restore tested quarterly; RTO ≤ 4 h business time. [BRD NFR-N-12, KPI-22] |
| NFR-BACK-03 | Backup integrity. | Restore tests documented; backups immutable against tampering. |

## 4.16 Disaster Recovery (NFR-DR)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-DR-01 | Recovery time objective. | RTO ≤ 4 h business time. [BRD NFR-N-12] |
| NFR-DR-02 | Recovery point objective. | RPO ≤ 24 h. [BRD NFR-N-12] |
| NFR-DR-03 | DR runbook and tests. | Documented DR plan; annual exercises; test evidence archived. |
| NFR-DR-04 | Data survivability. | No tenant data loss on regional incident; recovery audited. |

## 4.17 Cloud Infrastructure (NFR-CLOUD)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-CLOUD-01 | Cloud-native architecture. | Containers, managed services, immutable infrastructure, autoscaling. |
| NFR-CLOUD-02 | Cost efficiency. | Gross margin per tenant ≥ 70% at scale. [BRD NFR-N-16] |
| NFR-CLOUD-03 | Multi-zone resilience. | Application spans ≥ 2 availability zones in the launch region. |
| NFR-CLOUD-04 | Residency. | Single-region at MVP (GCC preferred); multi-region in Enterprise. [BRD AS-06, DEC-05, OOS-12] |

## 4.18 Caching (NFR-CACH)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-CACH-01 | Read cache for hot data (prices, product master, reference data). | Cache hit ratio ≥ 90% for reference reads; invalidation < 60 s. |
| NFR-CACH-02 | Cache consistency. | No stale price/stock displayed at POS (stock/price reads bypass or validate cache). |
| NFR-CACH-03 | Session resilience. | Cache failures degrade to source-of-truth reads; no transaction failure. |

## 4.19 API Performance (NFR-APIP)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-APIP-01 | API p95 latency for reads. | < 300 ms for list/get; < 2 s for heavy aggregates (per resource class). |
| NFR-APIP-02 | API throughput. | Supports NFR-SCAL-01 concurrency without degraded latency. |
| NFR-APIP-03 | Bulk operations. | Imports/exports within documented size/time envelopes (10k rows ≤ 10 min). |

## 4.20 Database Performance (NFR-DBP)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-DBP-01 | Transactional write latency. | Commit for core transactions < 2 s p95 incl. business-rule validation. |
| NFR-DBP-02 | Query performance at scale. | Stock/branch queries < 2 s at 100k stock lines; audit query < 60 s for 90-day scope. |
| NFR-DBP-03 | Indexing and partitioning. | Read-heavy tables partitioned/indexed per workload; documented query plans. |
| NFR-DBP-04 | Concurrency control. | No lost updates; optimistic/transactional control per DB requirements. |

---

# 5. External Interface Requirements

This section specifies the behavioral requirements of every external interface. Each interface is a contract boundary; the exact vendor/protocol is an Architecture/DevOps decision unless a market spec mandates otherwise (e.g., ZATCA). All interfaces must be testable with a stub/simulator.

## 5.1 REST API Interfaces (EXT-REST)

| ID | Requirement |
|----|-------------|
| EXT-REST-01 | The system shall expose all functions as versioned REST APIs per Section 7; no UI-only functionality. |
| EXT-REST-02 | The API shall enforce tenant, user, role, and branch scope on every request (server-side). |
| EXT-REST-03 | The API shall return structured errors with machine-readable codes (Section 7.9). |
| EXT-REST-04 | The API shall support pagination, filtering, sorting, and searching per Section 7.4–7.7. |
| EXT-REST-05 | The API contract shall be published as OpenAPI 3.1; breaking changes require new major version. |

## 5.2 Authentication & Identity Interfaces (EXT-AUTH)

| ID | Requirement |
|----|-------------|
| EXT-AUTH-01 | The system shall support password-based authentication with MFA (TOTP) and optional SSO per tenant policy. |
| EXT-AUTH-02 | The system shall issue short-lived access tokens and refresh tokens per Section 8.3. |
| EXT-AUTH-03 | Authentication events (success, failure, lockout, 2FA) shall be audited (BR-AUD-01). |
| EXT-AUTH-04 | Session timeout and lockout thresholds per tenant policy (BR-SEC-04). |
| EXT-AUTH-05 | Identity provider abstraction shall allow future SSO (SAML/OIDC) without core change. |

## 5.3 Barcode Scanner Interface (EXT-BAR)

| ID | Requirement |
|----|-------------|
| EXT-BAR-01 | The system shall support USB/HID and Bluetooth barcode scanners via a device abstraction (keyboard-wedge or SDK) (BRD CN-05, NFR-N-10). |
| EXT-BAR-02 | Scan resolution: scan → product resolution < 1 s; unresolved codes prompt for product selection. |
| EXT-BAR-03 | The system shall support GS1/EAN/UPC and national codes per active pack (FR-LOC-06). |
| EXT-BAR-04 | Scans shall not require focus on a specific field; system shall route scans contextually. |

## 5.4 Receipt Printer Interface (EXT-RCP)

| ID | Requirement |
|----|-------------|
| EXT-RCP-01 | The system shall support thermal receipt printing (ESC/POS) via device abstraction. |
| EXT-RCP-02 | Receipt templates per market pack (legal footer, tax lines) (FR-POS-03, BR-TAX-01). |
| EXT-RCP-03 | Printing failures shall not lose the sale; fallback to email/QR receipt. |
| EXT-RCP-04 | Reprint capability with audit of reprints. |

## 5.5 QR Scanner / QR Code Interface (EXT-QR)

| ID | Requirement |
|----|-------------|
| EXT-QR-01 | The system shall support QR-code scanning (payment QR, digital Rx QR, receipt QR) via camera/reader. |
| EXT-QR-02 | The system shall render QR receipts and QR-based payment payloads per market. |
| EXT-QR-03 | QR payloads shall be validated before acceptance (payment reference, Rx reference). |

## 5.6 Payment Gateway Interface (EXT-PAY)

| ID | Requirement |
|----|-------------|
| EXT-PAY-01 | The system shall integrate in-store payment capture (card terminals, QR) via a payment abstraction (BRD AS-08, DEC-06). |
| EXT-PAY-02 | Payment authorization states (approved/declined/pending/failed) shall be recorded per sale. |
| EXT-PAY-03 | Card/QR transaction references shall be stored and linked to sales for reconciliation (BR-CASH-01). |
| EXT-PAY-04 | Subscription billing payments (recurring) shall use the selected gateway (FR-SUB-02, DEC-06). |
| EXT-PAY-05 | Payment failures shall follow retry/alert flows; no silent loss of payment intent. |

## 5.7 SMS Gateway Interface (EXT-SMS)

| ID | Requirement |
|----|-------------|
| EXT-SMS-01 | The system shall send SMS notifications (expiry, recall, billing, OTP) via an SMS provider abstraction. |
| EXT-SMS-02 | SMS sends shall be consent-respecting and channel-logged (NFR-N-06). |
| EXT-SMS-03 | Delivery failures shall be retried and logged; provider outage does not affect core transactions. |

## 5.8 Email Service Interface (EXT-EMAIL)

| ID | Requirement |
|----|-------------|
| EXT-EMAIL-01 | The system shall send email (receipts, reports, notifications, invoices, statements) via an email service abstraction. |
| EXT-EMAIL-02 | Email deliveries shall be audited with recipient, template, and timestamp. |
| EXT-EMAIL-03 | Report/invoice email attachments shall be generated from posted data. |

## 5.9 Object Storage Interface (EXT-OBJ)

| ID | Requirement |
|----|-------------|
| EXT-OBJ-01 | The system shall store binary objects (Rx attachments ≤ 5 MB, receipt images, import/export files, audit archives) in object storage. |
| EXT-OBJ-02 | Object access shall be permissioned and audited; objects tenant-isolated. |
| EXT-OBJ-03 | Retention/purging of objects per policy (NFR-N-14). |

## 5.10 Notification Service Interface (EXT-NOT)

| ID | Requirement |
|----|-------------|
| EXT-NOT-01 | The system shall dispatch notifications (in-app, email, SMS) via a notification service abstraction. |
| EXT-NOT-02 | Notification delivery and preferences per REQ-NOT-001..005. |
| EXT-NOT-03 | The service shall support quiet hours, throttling, and channel fallback. |

## 5.11 Cloud Services Interfaces (EXT-CLOUD)

| ID | Requirement |
|----|-------------|
| EXT-CLOUD-01 | Managed services (compute, DB, object storage, queues, secret manager, observability) shall be consumed via abstractions to preserve portability (NFR-PORT-04). |
| EXT-CLOUD-02 | Autoscaling and capacity automation shall support NFR-SCAL targets. |
| EXT-CLOUD-03 | Cloud service failures shall degrade gracefully (NFR-RELI). |

## 5.12 Future OCR Service Interface (EXT-OCR)

| ID | Requirement |
|----|-------------|
| EXT-OCR-01 | (Future) The system shall provide an OCR service interface for paper-prescription intake (image → structured Rx data) to reduce manual entry. |
| EXT-OCR-02 | OCR output shall always require human pharmacist verification before fulfillment (BR-RX-04). |
| EXT-OCR-03 | OCR confidence scoring; low-confidence results routed for manual entry. |

## 5.13 Future AI Services Interface (EXT-AI)

| ID | Requirement |
|----|-------------|
| EXT-AI-01 | (Future) The system shall provide AI service interfaces for forecasting, anomaly detection, and insight products (Phase 5) consuming the analytics-ready data core (FR-AI-01/02). |
| EXT-AI-02 | AI outputs shall be advisory, never decision-enforcing, until validated per market. |
| EXT-AI-03 | AI feature access shall be feature-flagged per tenant/plan (FR-AI-03). |

---

# 6. User Interface Requirements

UI requirements are behavior and quality requirements. Visual design (colors, spacing, typography) is the UI/UX phase's responsibility; these requirements constrain behavior, layout logic, and accessibility. Each UI requirement supports measurable usability targets (BRD NFR-N-09: new staff productive in < 30 min; zero-training checkout for trained staff; ≤ 3 steps to scan-and-sell).

## 6.1 Responsive Design (UI-001..UI-005)

| ID | Requirement |
|----|-------------|
| UI-001 | The system shall provide responsive web UIs for desktop (≥ 1280×800) and tablet (≥ 768×1024). |
| UI-002 | POS layouts shall adapt to screen size without hiding critical actions (pay, void, return). |
| UI-003 | Admin/back-office UIs shall be fully usable on desktop; critical flows usable on tablet. |
| UI-004 | Layouts shall reflow correctly in both LTR and RTL without layout breakage. |
| UI-005 | No horizontal scrolling on supported viewports for core screens. |

## 6.2 Dark Mode / Light Mode (UI-006..UI-008)

| ID | Requirement |
|----|-------------|
| UI-006 | The system shall support light and dark themes; theme per user preference with tenant default. |
| UI-007 | Theme switching shall preserve contrast accessibility (WCAG 2.1 AA) in both modes. |
| UI-008 | RTL and theme changes shall not require reload or data loss. |

## 6.3 RTL / LTR (UI-009..UI-012)

| ID | Requirement |
|----|-------------|
| UI-009 | All screens shall render correctly in Arabic (RTL) and English (LTR) (BR-LOC-03). |
| UI-010 | Mixed-script content (Latin drug names, codes, barcodes inside Arabic UI) shall render with correct directionality and alignment. |
| UI-011 | Numbers, prices, and dates shall follow locale formatting from the active pack. |
| UI-012 | RTL layout is not a mirror-hack: navigation, icons, charts, and tables must reorder semantically. |

## 6.4 Accessibility (UI-013..UI-017)

| ID | Requirement |
|----|-------------|
| UI-013 | Core flows shall be keyboard-operable (NFR-ACC-01). |
| UI-014 | WCAG 2.1 AA: contrast, focus states, ARIA labels, form errors announced. |
| UI-015 | POS touch targets ≥ 44×44 px; actions reachable without precision pointing. |
| UI-016 | Color shall not be the sole indicator (status, errors) — icon + text + color. |
| UI-017 | Screen readers shall navigate tables, forms, and dashboard widgets meaningfully. |

## 6.5 Navigation (UI-018..UI-022)

| ID | Requirement |
|----|-------------|
| UI-018 | The system shall provide role-aware navigation showing only entitled modules (BR-TEN-02, BR-SEC-02). |
| UI-019 | Global navigation shall support module switching, current-branch/tenant context, and quick-search. |
| UI-020 | POS shall present a distinct, minimal navigation surface for speed (P-04). |
| UI-021 | Breadcrumbs/context indicators for deep flows (PO, Rx, transfers). |
| UI-022 | Navigation state shall be RTL/LTR correct and persisted. |

## 6.6 Dashboard (UI-023..UI-027)

| ID | Requirement |
|----|-------------|
| UI-023 | Dashboard widgets shall render within performance targets (REQ-DASH-001..009). |
| UI-024 | Every widget shall show data-currency timestamp and empty/stale states (BR-REP-01). |
| UI-025 | Widgets shall be composable per REQ-DASH-007 with persistence. |
| UI-026 | Charts (sales trend, branch comparison) shall be readable in both themes and scripts. |
| UI-027 | Widget content shall not rely on color alone; include labels/values. |

## 6.7 Forms (UI-028..UI-033)

| ID | Requirement |
|----|-------------|
| UI-028 | Forms shall validate inline with clear, localized error messages (Section 7.8 semantics). |
| UI-029 | Mandatory vs optional fields shall be clearly marked. |
| UI-030 | High-frequency forms (product create, PO, Rx) shall support save-draft and resume. |
| UI-031 | Approvals (discounts, overrides, refunds, adjustments) shall present reason fields and approver confirmation (BR-SEC-03). |
| UI-032 | Numeric/currency inputs shall follow locale formatting; barcode fields shall auto-focus-ready. |
| UI-033 | Forms shall be accessible (labels, focus order, error announcements). |

## 6.8 Tables (UI-034..UI-039)

| ID | Requirement |
|----|-------------|
| UI-034 | Tables shall support sortable columns, pagination, and row actions. |
| UI-035 | Row-level status (void/return/quarantine/recalled) shown with text + icon (not color only). |
| UI-036 | Long lists (products, stock, journal) shall meet search/filter performance targets. |
| UI-037 | Table exports shall preserve current filters (REQ-RPT-005). |
| UI-038 | Tables shall be RTL-aware (column order, alignment, scrolling). |
| UI-039 | Selection-based bulk actions (transfer, adjust, return) shall confirm before commit. |

## 6.9 Filtering (UI-040..UI-043)

| ID | Requirement |
|----|-------------|
| UI-040 | Reports and lists shall support date, branch, status, category, and free-text filters. |
| UI-041 | Filter state shall be shareable via URL for support/debug. |
| UI-042 | Date filters shall respect canonical dates with calendar display per tenant (BR-LOC-04). |
| UI-043 | Filters shall be applied server-side (Section 7.5), not client-side. |

## 6.10 Searching (UI-044..UI-047)

| ID | Requirement |
|----|-------------|
| UI-044 | Global and module search (products, customers, suppliers, Rx, sales) < 2 s p95. |
| UI-045 | POS search with autocorrect and mixed-script tolerance (REQ-POS-002). |
| UI-046 | Search results shall show key identity fields and status. |
| UI-047 | Barcode/national-code scans shall route to search seamlessly. |

## 6.11 Exporting (UI-048..UI-051)

| ID | Requirement |
|----|-------------|
| UI-048 | Exports (PDF/Excel/CSV) shall match on-screen filters and totals (REQ-RPT-005). |
| UI-049 | Export actions shall be permission-gated and audited (BR-AUD-01). |
| UI-050 | Large exports shall run async with notification (REQ-NOT-002). |
| UI-051 | Compliance exports shall follow pack templates (FR-LOC-07). |

## 6.12 Printing (UI-052..UI-055)

| ID | Requirement |
|----|-------------|
| UI-052 | Receipt printing shall not block the sale; failure falls back to email/QR (EXT-RCP-03). |
| UI-053 | Print templates (receipts, POs, reports, statements) per market pack. |
| UI-054 | Reprints logged with operator + reason. |
| UI-055 | Print preview accurate in RTL/LTR and both themes. |

## 6.13 Notifications (UI-056..UI-059)

| ID | Requirement |
|----|-------------|
| UI-056 | In-app notification center per REQ-NOT-001 with read/unread and priority. |
| UI-057 | Notifications shall navigate to the relevant record/action. |
| UI-058 | Notification preferences accessible in UI (REQ-NOT-004). |
| UI-059 | Notifications shall not interrupt an active POS transaction. |

---

# 7. API Requirements

## 7.1 REST Standards (API-001..API-005)

| ID | Requirement |
|----|-------------|
| API-001 | The system shall expose a RESTful API following resource-oriented design (nouns, HTTP verbs, status codes). |
| API-002 | All API interactions shall be stateless; server-side authorization on every call. |
| API-003 | The API shall be versioned in the URI path (e.g., `/api/v1/...`). |
| API-004 | The API shall use JSON with `application/json`; UTF-8; content negotiation honored. |
| API-005 | Idempotency keys shall be supported for state-changing operations where retries are possible (payments, POs, imports). |

## 7.2 OpenAPI 3.1 (API-006..API-010)

| ID | Requirement |
|----|-------------|
| API-006 | Every public endpoint shall be described in an OpenAPI 3.1 document. |
| API-007 | The contract shall be the source of truth for generated clients/tests. |
| API-008 | Schemas shall define types, required fields, enums, formats, and examples. |
| API-009 | The contract shall be validated in CI (lint + diff). |
| API-010 | Sandbox and documentation portals shall render from the contract (FR-MKT-01). |

## 7.3 Versioning (API-011..API-014)

| ID | Requirement |
|----|-------------|
| API-011 | Breaking changes require a new major version; additive changes may ship in the same major. |
| API-012 | Deprecated versions shall be supported for ≥ 2 release cycles with deprecation headers/warnings. |
| API-013 | Version changelogs shall be published. |
| API-014 | Client capability negotiation via version header/URI per API-003. |

## 7.4 Pagination (API-015..API-018)

| ID | Requirement |
|----|-------------|
| API-015 | List endpoints shall support cursor or offset pagination with a documented default page size. |
| API-016 | Page size shall be bounded (default documented, max enforced). |
| API-017 | Pagination metadata (next cursor, total) returned in a consistent envelope. |
| API-018 | Pagination must be stable across concurrent data changes (no skipped/duplicated records). |

## 7.5 Filtering (API-019..API-022)

| ID | Requirement |
|----|-------------|
| API-019 | List endpoints shall support filtering on defined fields via query parameters. |
| API-020 | Filters shall be server-side and permission-scoped (tenant/branch/user). |
| API-021 | Filter operators (eq, neq, gt, lt, in, between) documented per endpoint. |
| API-022 | Unsupported filter fields shall return a clear validation error. |

## 7.6 Sorting (API-023..API-025)

| ID | Requirement |
|----|-------------|
| API-023 | List endpoints shall support sorting on documented fields with asc/desc. |
| API-024 | Sort keys shall be validated against an allow-list. |
| API-025 | Default sort order documented per endpoint. |

## 7.7 Searching (API-026..API-028)

| ID | Requirement |
|----|-------------|
| API-026 | Search-capable endpoints (products, customers, suppliers, Rx, sales) shall accept free-text search. |
| API-027 | Search shall be case-insensitive and script-tolerant (Arabic/Latin). |
| API-028 | Search results shall be ranked and paginated; performance per NFR-PERF-03. |

## 7.8 Validation (API-029..API-033)

| ID | Requirement |
|----|-------------|
| API-029 | All inputs shall be validated server-side (types, lengths, ranges, formats, enums). |
| API-030 | Validation errors shall identify the field and reason in a machine-readable structure. |
| API-031 | Business-rule validation (BR rules) shall be enforced in the service layer, not the UI. |
| API-032 | Cross-field invariants (e.g., batch+expiry, balance) validated before commit. |
| API-033 | Unknown/unsafe payloads rejected (strict schemas; no silent coercion). |

## 7.9 Error Codes (API-034..API-038)

| ID | Requirement |
|----|-------------|
| API-034 | Errors shall use proper HTTP status semantics (400, 401, 403, 404, 409, 422, 429, 500, 503). |
| API-035 | Error bodies shall include: machine code, message (localized), field, trace/request ID. |
| API-036 | Business-rule failures shall map to stable error codes (e.g., `INSUFFICIENT_STOCK`, `EXPIRED_RX`, `UNBALANCED_POST`). |
| API-037 | Error codes shall be documented in the OpenAPI contract. |
| API-038 | No sensitive data (tokens, PII) in error messages or logs. |

## 7.10 Rate Limits (API-039..API-042)

| ID | Requirement |
|----|-------------|
| API-039 | Public/partner API shall enforce rate limits per tenant/API key (NFR-SCAL protection). |
| API-040 | Rate-limit responses shall use 429 with `Retry-After` header. |
| API-041 | Internal service calls shall have documented capacity/quota limits (BR-SUB-01). |
| API-042 | Abuse patterns shall be detected and throttled (OWASP). |

## 7.11 Authentication / Authorization (API-043..API-047)

| ID | Requirement |
|----|-------------|
| API-043 | Public API shall require authentication (bearer tokens per Section 8.3). |
| API-044 | Authorization (RBAC + branch scope) enforced on every endpoint (REQ-ROL-003). |
| API-045 | Partner API keys shall be scoped, revocable, and rate-limited (REQ-MKT-001). |
| API-046 | Sensitive endpoints (patient data) shall require elevated permission (BR-PRIV-01). |
| API-047 | AuthN/AuthZ failures shall be audited (BR-AUD-01). |

---

# 8. Security Requirements

Security requirements implement BRD BR-SEC-01..04, BR-PRIV-01, BR-AUD-01, NFR-N-05/06, and OWASP ASVS 4.0. Baseline: ASVS Level 1; Level 2 for authentication, patient data, and payment-adjacent flows.

## 8.1 Authentication (SEC-001..SEC-006)

| ID | Requirement |
|----|-------------|
| SEC-001 | The system shall authenticate every user with a unique named account; shared logins prohibited (BR-SEC-01). |
| SEC-002 | The system shall support password + MFA (TOTP) authentication; MFA required for admin and privileged roles. |
| SEC-003 | The system shall support optional SSO per tenant policy (future-ready via identity abstraction, EXT-AUTH-05). |
| SEC-004 | Failed login attempts shall increment lockout counters per policy (BR-SEC-04). |
| SEC-005 | Authentication events shall be audited (success, failure, lockout, unlock) (BR-AUD-01). |
| SEC-006 | Session identifiers shall be cryptographically random, HTTP-only, and bound to the user/device. |

## 8.2 Authorization & RBAC (SEC-007..SEC-010)

| ID | Requirement |
|----|-------------|
| SEC-007 | Authorization shall be enforced server-side on every request: role permission + branch scope + tenant context (BR-SEC-02). |
| SEC-008 | Least-privilege default; no implicit access beyond granted role/scope. |
| SEC-009 | Privileged actions (price overrides, refunds > threshold, voids, adjustments, role changes) require approval or 2FA per policy (BR-SEC-03). |
| SEC-010 | Denied requests shall be audited and, for repeated abuse, throttled (API-042). |

## 8.3 JWT & Refresh Tokens (SEC-011..SEC-016)

| ID | Requirement |
|----|-------------|
| SEC-011 | Access tokens shall be short-lived JWTs (documented TTL ≤ 15 min) signed with a strong algorithm (RS256/ES256). |
| SEC-012 | Refresh tokens shall be long-lived, rotation-enabled, and revocable; reuse detection invalidates the session. |
| SEC-013 | Tokens shall carry claims: subject, tenant, roles, session ID, issued/expiry — no PII. |
| SEC-014 | Token validation shall occur at every protected endpoint (issuer, audience, signature, expiry). |
| SEC-015 | Token signing keys shall be rotated; leaked-key revocation runbook documented. |
| SEC-016 | Refresh token rotation shall be audited. |

## 8.4 MFA / OTP (SEC-017..SEC-020)

| ID | Requirement |
|----|-------------|
| SEC-017 | The system shall support TOTP-based MFA enrollment with recovery codes. |
| SEC-018 | MFA shall be enforced for admin, tenant-admin, and privileged actions (BR-SEC-03). |
| SEC-019 | OTP attempts shall be rate-limited; brute-force protection applied. |
| SEC-020 | MFA enrollment/reset shall be audited and gated by additional verification. |

## 8.5 Password Policy (SEC-021..SEC-024)

| ID | Requirement |
|----|-------------|
| SEC-021 | Password policy (length, complexity, history, expiry) configurable per tenant and enforced centrally (BR-SEC-04). |
| SEC-022 | Passwords shall be stored only as salted, iterated hashes (e.g., bcrypt/argon2); never plaintext or reversible. |
| SEC-023 | Password reset shall require verification and invalidate active sessions. |
| SEC-024 | Default/initial passwords must be changed on first login. |

## 8.6 Session Management (SEC-025..SEC-028)

| ID | Requirement |
|----|-------------|
| SEC-025 | Session timeout configurable per tenant and enforced (BR-SEC-04). |
| SEC-026 | Logout shall invalidate tokens and sessions immediately. |
| SEC-027 | Concurrent-session policy (limit) configurable; sessions listable by user. |
| SEC-028 | Session fixation/reset on privilege changes. |

## 8.7 Encryption (SEC-029..SEC-033)

| ID | Requirement |
|----|-------------|
| SEC-029 | All data in transit encrypted (TLS ≥ 1.2, HSTS). |
| SEC-030 | All sensitive data at rest encrypted (disk/DB/object storage); keys managed via KMS (EXT-CLOUD). |
| SEC-031 | Patient-identity and payment data shall be additionally protected (field-level encryption or tokenization where required). |
| SEC-032 | Key lifecycle: rotation, separation of duties, least-privilege key access (NFR-SEC-01). |
| SEC-033 | Encryption downgrade/disabling shall not be possible via tenant configuration. |

## 8.8 Audit Logging (SEC-034..SEC-036)

| ID | Requirement |
|----|-------------|
| SEC-034 | All create/update/delete of financial, stock, Rx, controlled-substance, and permission data audited immutably (BR-AUD-01, REQ-AUD-001). |
| SEC-035 | Audit records include user, timestamp, before/after, IP/device; tamper-evident (REQ-AUD-004). |
| SEC-036 | Audit access itself restricted; read of audit data logged. |

## 8.9 Data Privacy (SEC-037..SEC-040)

| ID | Requirement |
|----|-------------|
| SEC-037 | Patient data handled per market privacy regime with consent records (BR-PRIV-01, NFR-N-06). |
| SEC-038 | Only role-authorized staff view prescription-linked identity; exports consent-scoped (BR-PRIV-01). |
| SEC-039 | Data minimization: pharmacy-scope only; no EHR scope (OOS-08). |
| SEC-040 | Deletion/destruction per documented offboarding policy; never silent (BR-SUB-06). |

## 8.10 OWASP / ASVS (SEC-041..SEC-045)

| ID | Requirement |
|----|-------------|
| SEC-041 | ASVS Level 1 baseline achieved; Level 2 for auth/data/payment flows. |
| SEC-042 | OWASP Top 10 controls: injection, XSS, CSRF, SSRF, IDOR, auth failures — mitigated and tested. |
| SEC-043 | Tenant/branch IDOR protection: cross-tenant/branch access returns 403/404 without data leak (BR-TEN-01). |
| SEC-044 | Security testing: SAST, DAST, dependency scanning, and penetration test before launch (NFR-N-05). |
| SEC-045 | Incident response runbook documented and exercised. |

## 8.11 Rate Limiting (SEC-046..SEC-049)

| ID | Requirement |
|----|-------------|
| SEC-046 | Login, OTP, and sensitive endpoints rate-limited (per user/IP). |
| SEC-047 | Partner API rate limits per API-039. |
| SEC-048 | Abuse detection: unusual patterns (bulk export, scan frequency) flagged/alerts. |
| SEC-049 | Rate limits not bypassable by tenant configuration. |

## 8.12 Input Validation (SEC-050..SEC-052)

| ID | Requirement |
|----|-------------|
| SEC-050 | All inputs validated server-side (types, length, range, format) (API-029). |
| SEC-051 | Output encoding to prevent stored/reflected XSS; context-aware escaping. |
| SEC-052 | File uploads (Rx attachments, imports) validated by type, size, and content; executed nowhere (EXT-OBJ). |

## 8.13 Secrets Management (SEC-053..SEC-056)

| ID | Requirement |
|----|-------------|
| SEC-053 | All secrets (keys, credentials, API tokens) stored in a secrets manager; never in code/repo/logs. |
| SEC-054 | Secret access least-privileged and audited. |
| SEC-055 | No secrets in client bundles or configuration exposed to browsers. |
| SEC-056 | Rotation and revocation procedures documented for every secret class. |

## 8.14 Tenant Isolation (SEC-057..SEC-059)

| ID | Requirement |
|----|-------------|
| SEC-057 | Tenant data isolated at the data layer; cross-tenant access architecturally prevented and access-controlled (BR-TEN-01). |
| SEC-058 | Isolation verified by automated tests (cross-tenant probe) in CI. |
| SEC-059 | Market packs execute in isolation without cross-pack/tenant access (BR-PLUG-01, NFR-N-19). |

---

# 9. Multi-Tenant Requirements

## 9.1 Tenant Lifecycle (MT-001..MT-005)

| ID | Requirement |
|----|-------------|
| MT-001 | The system shall support tenant lifecycle states: trial, active, suspended, offboarding, archived (BR-SUB-02/04/06). |
| MT-002 | Provisioning shall create an isolated tenant data space with configuration defaults in < 15 min (FR-TEN-01). |
| MT-003 | Suspension shall preserve data and export access; no deletion without documented, approved offboarding (BR-SUB-06). |
| MT-004 | Offboarding shall follow the documented export-and-delete policy with audit. |
| MT-005 | All lifecycle transitions shall be versioned and audited (BR-TEN-03). |

## 9.2 Tenant Isolation (MT-006..MT-009)

| ID | Requirement |
|----|-------------|
| MT-006 | Tenant data shall be isolated at the data layer; cross-tenant access prohibited and enforced by architecture + access controls (BR-TEN-01). |
| MT-007 | All queries shall be tenant-scoped at the persistence boundary (defense in depth). |
| MT-008 | Isolation shall be verified by automated cross-tenant tests in CI (SEC-058). |
| MT-009 | Resource isolation (noisy neighbor) managed via quotas (MT-014). |

## 9.3 Configuration (MT-010..MT-012)

| ID | Requirement |
|----|-------------|
| MT-010 | Tenant-level configuration (tax, currency, units, language, policies, thresholds) via versioned configuration layer (FR-TEN-02, BR-TEN-03). |
| MT-011 | Configuration changes shall be audited with before/after values. |
| MT-012 | Configuration-over-customization: no per-tenant code (OOS-11, CN-01). |

## 9.4 Feature Flags (MT-013)

| ID | Requirement |
|----|-------------|
| MT-013 | Capabilities shall be controllable per tenant/plan via feature flags without release (FR-AI-03, REQ-TEN-005); rollback immediate. |

## 9.5 Subscription Limits & Licensing (MT-014..MT-017)

| ID | Requirement |
|----|-------------|
| MT-014 | Licensed limits (users, branches, transactions, storage) enforced at runtime with warnings at 80/90/100% (BR-SUB-01). |
| MT-015 | Entitlements enforced per plan; unavailable features flagged with upgrade path (BR-TEN-02). |
| MT-016 | Quotas enforced to prevent noisy-neighbor resource abuse (MT-009). |
| MT-017 | Plan changes prorated/validated (BR-SUB-03). |

## 9.6 Storage Isolation (MT-018..MT-019)

| ID | Requirement |
|----|-------------|
| MT-018 | Object storage (attachments, exports, archives) isolated per tenant (EXT-OBJ-02). |
| MT-019 | Storage quotas tracked against plan limits (MT-014). |

## 9.7 Data Isolation (MT-020..MT-021)

| ID | Requirement |
|----|-------------|
| MT-020 | Tenant data (transactions, masters, audit) isolated at the data layer; corrections never cross tenant boundaries. |
| MT-021 | Export/import operations strictly tenant-scoped. |

## 9.8 Cross-Tenant Protection (MT-022..MT-024)

| ID | Requirement |
|----|-------------|
| MT-022 | Cross-tenant/branch access attempts return 403/404 without data disclosure (SEC-043). |
| MT-023 | Tenant identifiers validated from authenticated context, never trusted from client input. |
| MT-024 | Automated probes test cross-tenant isolation in every CI gate. |

---

# 10. Database Requirements (Logical)

This section defines logical data requirements only. Physical schema design (tables, indexes, partitioning) is the Database Architect's responsibility and must satisfy these requirements.

## 10.1 Data Consistency (DB-001..DB-004)

| ID | Requirement |
|----|-------------|
| DB-001 | Data shall be transactionally consistent across business aggregates (stock ↔ ledger, register ↔ stock). |
| DB-002 | Every business invariant (balance, non-negative stock, single branch attribution) enforced at the persistence layer (NFR-DINT). |
| DB-003 | Master data references shall be validated (foreign-key integrity at logical level). |
| DB-004 | Cross-tenant consistency prevented by mandatory tenant scoping (MT-007). |

## 10.2 Transactions (DB-005..DB-007)

| ID | Requirement |
|----|-------------|
| DB-005 | Multi-entity business operations (sale = stock + journal + cash + loyalty) shall be atomic (all-or-nothing). |
| DB-006 | Long-running/batch operations (imports, exports, reports) shall use transactional batching with resumability (NFR-RELI-04). |
| DB-007 | Payment and financial events shall be transactional with idempotency (NFR-RELI-03). |

## 10.3 Concurrency (DB-008..DB-011)

| ID | Requirement |
|----|-------------|
| DB-008 | Concurrent stock/sale operations shall not lose updates (row/version locking, optimistic control). |
| DB-009 | Sale of the same last unit from two terminals shall resolve to a single successful finalization (BR-STK-02). |
| DB-010 | Day-close concurrency: single close per day enforced at the data layer (BR-CASH-02). |
| DB-011 | Audit writes shall not be lost under concurrency (append-only). |

## 10.4 Soft Delete (DB-012..DB-014)

| ID | Requirement |
|----|-------------|
| DB-012 | Transactional data shall never be physically deleted in normal operation; soft-delete/tombstone pattern used (FR-AI-01, BR-AUD-01). |
| DB-013 | Product/supplier deactivation is a state change, not deletion (REQ-MED-011). |
| DB-014 | Void/return/voided-sale records preserved and marked (BR-SAL-04). |

## 10.5 Audit Fields (DB-015..DB-018)

| ID | Requirement |
|----|-------------|
| DB-015 | Every mutable record shall carry created-by/at and updated-by/at fields. |
| DB-016 | State changes shall carry before/after values to the audit store (BR-AUD-01). |
| DB-017 | Tenant, branch, and user attribution fields mandatory on all transactional records. |
| DB-018 | Version/change counters for optimistic concurrency (DB-008). |

## 10.6 Versioning (DB-019..DB-021)

| ID | Requirement |
|----|-------------|
| DB-019 | Configuration and master-data changes versioned (BR-TEN-03). |
| DB-020 | Market-pack state versioned; activation/changes audited (BR-PLUG-02). |
| DB-021 | Accounting corrections via reversing entries, never edits (BR-ACC-03). |

## 10.7 Data Retention (DB-022..DB-024)

| ID | Requirement |
|----|-------------|
| DB-022 | Retention configurable per record class per regulatory/tenant policy (NFR-N-14). |
| DB-023 | Controlled-substance, Rx, and financial records retained at legal minimum (NFR-N-14). |
| DB-024 | Legal hold excludes records from purge (REQ-AUD-003). |

## 10.8 Archiving (DB-025..DB-028)

| ID | Requirement |
|----|-------------|
| DB-025 | Archived data shall remain queryable/exportable within defined SLAs. |
| DB-026 | Archiving shall not break referential integrity or reconciliation. |
| DB-027 | Archive process resumable and audited. |
| DB-028 | Audit archives tamper-evident (REQ-AUD-004). |

## 10.9 Master Data (DB-029..DB-031)

| ID | Requirement |
|----|-------------|
| DB-029 | Master data (products, suppliers, customers, branches, accounts, price lists) shall have authoritative references used by all modules. |
| DB-030 | Master data changes versioned and audited. |
| DB-031 | Duplicate detection (barcode, national code, supplier tax id) at the data layer (REQ-MED-012). |

## 10.10 Reference Data (DB-032..DB-034)

| ID | Requirement |
|----|-------------|
| DB-032 | Reference data (categories, reason codes, statuses, tax rates, calendars, currencies) driven by market packs and tenant config. |
| DB-033 | Reason-code taxonomies (adjustment, return, void, variance) standardized and extendable per tenant. |
| DB-034 | Reference data changes versioned to avoid breaking historical interpretation. |

---

# 11. Compliance Requirements

Compliance requirements are carried from BRD §7.3/§7.4, BR-LOC/PLUG/CTL/TAX/PRIV, and NFR-N-06/14. **Note:** legal validation of every market pack is an SRS-phase activity (BRD AS-02, OI-02); nothing in this section is a legal conclusion. The system shall implement the configuration framework such that validated market rules can be enforced without core changes.

## 11.1 Healthcare Regulations (CMP-001..CMP-005)

| ID | Requirement |
|----|-------------|
| CMP-001 | The system shall support market-specific pharmacy licensing/tax-registration profiles per branch (FR-PH-01). |
| CMP-002 | The system shall provide health-authority report adapters per active market pack (FR-LOC-07, FR-REP-04). |
| CMP-003 | The system shall map national drug-registration codes and GS1/SFDA-aligned barcodes per pack (FR-LOC-06). |
| CMP-004 | Market regulatory changes shall be delivered as versioned pack updates without core changes (BR-PLUG-02). |
| CMP-005 | Compliance readiness per market reported at 100% before go-live (KPI-23, REQ-CMP-008). |

## 11.2 Tax Rules (CMP-006..CMP-010)

| ID | Requirement |
|----|-------------|
| CMP-006 | Tax rates/treatments driven by the active market pack (BR-TAX-01, REQ-CMP-003). |
| CMP-007 | Tax computed per product treatment on every taxable line; reported per rate (FR-ACC-03). |
| CMP-008 | Tax exports reconcile to posted sales with 0 drift (BR-TAX-02). |
| CMP-009 | E-invoicing per pack (e.g., ZATCA FATOORAH Phase 2 in KSA): invoice issued only after validated transmission (BR-TAX-03, FR-LOC-05). |
| CMP-010 | Cross-GCC variance (5%/15%) and Yemen local sales-tax arrangements handled purely by pack configuration (BRD §7.3). |

## 11.3 Prescription Rules (CMP-011..CMP-015)

| ID | Requirement |
|----|-------------|
| CMP-011 | Rx validity window (default 90 days), over-quantity, and refill limits enforced (BR-RX-02/03/05). |
| CMP-012 | Dispense signature (pharmacist identity + timestamp) mandatory (BR-RX-04). |
| CMP-013 | Controlled Rx requires valid issuer reference and documentation (BR-RX-06). |
| CMP-014 | Rx mode (paper/digital) per pack adapter (FR-RX-05). |
| CMP-015 | Rx archive and retention per policy (FR-RX-04, NFR-N-14). |

## 11.4 Controlled Medicines (CMP-016..CMP-020)

| ID | Requirement |
|----|-------------|
| CMP-016 | Immutable register entry for every controlled transaction (receive/sell/transfer/adjust/destroy) (BR-CTL-01). |
| CMP-017 | Controlled stock not sold without purchaser/requisition reference where required (BR-CTL-02). |
| CMP-018 | Register↔stock reconciliation at any time; variance triggers documented review and (above threshold) compliance notification (BR-CTL-03). |
| CMP-019 | Witnessed, documented destruction before stock removal (BR-CTL-04). |
| CMP-020 | Controlled-substance schedule/register schema per market pack (FR-LOC-07). |

## 11.5 Audit Trails (CMP-021..CMP-024)

| ID | Requirement |
|----|-------------|
| CMP-021 | Immutable audit for financial, stock, Rx, controlled, and permission data (BR-AUD-01). |
| CMP-022 | Audit export on regulatory request < 60 s for 90-day scope (NFR-N-07). |
| CMP-023 | Retention per legal minimum with export capability (NFR-N-14). |
| CMP-024 | Tamper-evidence and integrity verification (REQ-AUD-004). |

## 11.6 Localization (CMP-025..CMP-029)

| ID | Requirement |
|----|-------------|
| CMP-025 | Country-neutral core; all market behavior via packs (BR-LOC-01). |
| CMP-026 | Tenant requires ≥ 1 active pack before live transactions; mixing requires explicit approval (BR-LOC-02). |
| CMP-027 | Arabic RTL + English with correct mixed-script rendering (BR-LOC-03). |
| CMP-028 | Canonical dates; Gregorian/Hijri display (BR-LOC-04). |
| CMP-029 | Multi-currency base + secondary with rate audit (BR-CUR-01/02). |

## 11.7 Privacy (CMP-030..CMP-033)

| ID | Requirement |
|----|-------------|
| CMP-030 | Patient data per configured privacy regime with consent records (BR-PRIV-01, NFR-N-06). |
| CMP-031 | Role-scoped access to prescription-linked identity; consent-scoped exports (BR-PRIV-01). |
| CMP-032 | Data minimization; pharmacy-scope only (OOS-08). |
| CMP-033 | Cross-border residency decision enforced per market (CN-06, DEC-05). |

## 11.8 Future Regulatory Plugins (CMP-034..CMP-037)

| ID | Requirement |
|----|-------------|
| CMP-034 | Adding a new market requires a new validated pack, not core rework (BR-LOC-01, OP-11). |
| CMP-035 | Pack updates versioned, sandbox-validated, audited before activation (BR-PLUG-02). |
| CMP-036 | Pack isolation prevents cross-pack data access (BR-PLUG-01, NFR-N-19). |
| CMP-037 | The framework supports future regulations (insurance/TPA, new e-invoicing specs, digital health) via new adapters (OOS-05 revisit path, Phase 3). |

---

# 12. Business Rules Mapping

Every BRD business rule (BR-* — 70+ atomic rules) is mapped to the SRS requirement(s) that enforce it. This table is the QA contract for rule enforcement (KPI-12: 100% of BR rules enforced in production code).

## 12.1 Stock & Inventory (BR-STK)

| BRD Rule | SRS Requirements | Module |
|----------|------------------|--------|
| BR-STK-01 | REQ-MED-003, REQ-PUR-002, REQ-INV-001 | MED, PUR, INV |
| BR-STK-02 | REQ-POS-001, REQ-INV-001, REQ-INV-007, REQ-RX-003 | POS, INV, RX |
| BR-STK-03 | REQ-INV-005, REQ-INV-006 | INV |
| BR-STK-04 | REQ-INV-002, REQ-INV-003, REQ-DASH-005, REQ-NOT-002 | INV, DASH, NOT |
| BR-STK-05 | REQ-PUR-002, REQ-PUR-007 | PUR |
| BR-STK-06 | REQ-INV-008, REQ-BR-005 | INV, BR |
| BR-STK-07 | REQ-INV-006, REQ-INV-007, NFR-DINT-01 | INV |

## 12.2 Sales & POS (BR-SAL)

| BRD Rule | SRS Requirements | Module |
|----------|------------------|--------|
| BR-SAL-01 | REQ-POS-001 | POS |
| BR-SAL-02 | REQ-POS-003, REQ-SET-004 | POS, SET |
| BR-SAL-03 | REQ-POS-006, REQ-SAL-005 | POS, SAL |
| BR-SAL-04 | REQ-POS-007 | POS |
| BR-SAL-05 | REQ-POS-006 | POS |
| BR-SAL-06 | REQ-MED-008, REQ-POS-009 | MED, POS |

## 12.3 Prescriptions (BR-RX)

| BRD Rule | SRS Requirements | Module |
|----------|------------------|--------|
| BR-RX-01 | REQ-RX-001 | RX |
| BR-RX-02 | REQ-RX-002 | RX |
| BR-RX-03 | REQ-RX-002 | RX |
| BR-RX-04 | REQ-RX-003 | RX |
| BR-RX-05 | REQ-RX-002, REQ-RX-007 | RX |
| BR-RX-06 | REQ-RX-003, REQ-MED-009 | RX, MED |

## 12.4 Controlled Substances (BR-CTL)

| BRD Rule | SRS Requirements | Module |
|----------|------------------|--------|
| BR-CTL-01 | REQ-MED-009, REQ-RX-004, REQ-CMP-007 | MED, RX, CMP |
| BR-CTL-02 | REQ-RX-004, REQ-CMP-007 | RX, CMP |
| BR-CTL-03 | REQ-RX-004 | RX |
| BR-CTL-04 | REQ-INV-010, REQ-CMP-007 | INV, CMP |

## 12.5 Pricing (BR-PRC)

| BRD Rule | SRS Requirements | Module |
|----------|------------------|--------|
| BR-PRC-01 | REQ-MED-005, REQ-POS-008 | MED, POS |
| BR-PRC-02 | REQ-MED-005, REQ-BR-002 | MED, BR |
| BR-PRC-03 | REQ-MED-001, REQ-MED-005 | MED |

## 12.6 Purchasing & Suppliers (BR-PUR / BR-SUP)

| BRD Rule | SRS Requirements | Module |
|----------|------------------|--------|
| BR-PUR-01 | REQ-PUR-001 | PUR |
| BR-PUR-02 | REQ-PUR-002 | PUR |
| BR-PUR-03 | REQ-PUR-001 | PUR |
| BR-PUR-04 | REQ-INV-004, REQ-PUR-004, REQ-DASH-006 | INV, PUR, DASH |
| BR-PUR-05 | REQ-PUR-002 | PUR |
| BR-SUP-01 | REQ-SUP-001, REQ-PUR-001 | SUP, PUR |
| BR-SUP-02 | REQ-SUP-003 | SUP |
| BR-SUP-03 | REQ-PUR-003, REQ-SUP-006 | PUR, SUP |
| BR-SUP-04 | REQ-SUP-002 | SUP |
| BR-SUP-05 | REQ-PUR-003, REQ-SUP-004 | PUR, SUP |

## 12.7 Customers, Credit & Loyalty (BR-CUST / BR-LOY)

| BRD Rule | SRS Requirements | Module |
|----------|------------------|--------|
| BR-CUST-01 | REQ-POS-010, REQ-CUS-002 | POS, CUS |
| BR-CUST-02 | REQ-CUS-002 | CUS |
| BR-CUST-03 | REQ-CUS-004 | CUS |
| BR-LOY-01 | REQ-CUS-003 | CUS |

## 12.8 Cash & Accounting (BR-CASH / BR-ACC / BR-TAX)

| BRD Rule | SRS Requirements | Module |
|----------|------------------|--------|
| BR-CASH-01 | REQ-POS-004, REQ-SAL-006, REQ-POS-011 | POS, SAL |
| BR-CASH-02 | REQ-SAL-006, REQ-ACC-005 | SAL, ACC |
| BR-ACC-01 | REQ-ACC-001, REQ-POS-006 | ACC, POS |
| BR-ACC-02 | REQ-ACC-007 | ACC |
| BR-ACC-03 | REQ-ACC-005, REQ-AI-001 | ACC, AI |
| BR-ACC-04 | REQ-INV-011, REQ-ACC-003, REQ-SAL-002 | INV, ACC, SAL |
| BR-TAX-01 | REQ-MED-004, REQ-ACC-004, REQ-POS-005 | MED, ACC, POS |
| BR-TAX-02 | REQ-ACC-004 | ACC |
| BR-TAX-03 | REQ-ACC-006, REQ-CMP-003, REQ-POS-005 | ACC, CMP, POS |

## 12.9 Branch & Multi-Branch (BR-BRANCH)

| BRD Rule | SRS Requirements | Module |
|----------|------------------|--------|
| BR-BRANCH-01 | REQ-BR-001, REQ-BR-004, REQ-RPT-002 | BR, RPT |
| BR-BRANCH-02 | REQ-BR-002, REQ-DASH-003 | BR, DASH |

## 12.10 Security, Privacy & Audit (BR-SEC / BR-PRIV / BR-AUD)

| BRD Rule | SRS Requirements | Module |
|----------|------------------|--------|
| BR-SEC-01 | REQ-USR-001, REQ-ROL-003, SEC-001 | USR, ROL |
| BR-SEC-02 | REQ-USR-003, REQ-ROL-001..003, SEC-007 | USR, ROL |
| BR-SEC-03 | REQ-ROL-004, REQ-POS-008, REQ-POS-009, SEC-009 | ROL, POS |
| BR-SEC-04 | REQ-USR-002, REQ-USR-005, SEC-021 | USR |
| BR-PRIV-01 | REQ-CUS-001, REQ-CUS-005, REQ-CUS-006, REQ-CMP-004, SEC-037..039 | CUS, CMP |
| BR-AUD-01 | REQ-AUD-001..005, REQ-USR-004, REQ-ROL-005, REQ-SUB-007, SEC-034..036 | AUD, USR, ROL, SUB |

## 12.11 Multi-Tenancy & Subscription (BR-TEN / BR-SUB)

| BRD Rule | SRS Requirements | Module |
|----------|------------------|--------|
| BR-TEN-01 | REQ-TEN-001, MT-006, SEC-057 | TEN |
| BR-TEN-02 | REQ-TEN-005, REQ-SUB-001, MT-015 | TEN, SUB |
| BR-TEN-03 | REQ-TEN-002, MT-010, REQ-SET-004 | TEN, SET |
| BR-SUB-01 | REQ-SUB-001, REQ-DASH-004, REQ-NOT-002 | SUB, DASH, NOT |
| BR-SUB-02 | REQ-SUB-002, REQ-SUB-003 | SUB |
| BR-SUB-03 | REQ-SUB-004 | SUB |
| BR-SUB-04 | REQ-SUB-006 | SUB |
| BR-SUB-05 | REQ-SUB-005, REQ-SUB-007 | SUB |
| BR-SUB-06 | REQ-SUB-003, REQ-TEN-004 | SUB, TEN |

## 12.12 Reporting (BR-REP)

| BRD Rule | SRS Requirements | Module |
|----------|------------------|--------|
| BR-REP-01 | REQ-RPT-001, REQ-RPT-006, REQ-DASH-001, REQ-DASH-009 | RPT, DASH |
| BR-REP-02 | REQ-RPT-002, REQ-DASH-002 | RPT, DASH |

## 12.13 Recall (BR-RECALL)

| BRD Rule | SRS Requirements | Module |
|----------|------------------|--------|
| BR-RECALL-01 | REQ-INV-009, REQ-NOT-002 | INV, NOT |

## 12.14 Localization, Currency & Plugin (BR-LOC / BR-CUR / BR-PLUG)

| BRD Rule | SRS Requirements | Module |
|----------|------------------|--------|
| BR-LOC-01 | REQ-CMP-001, REQ-CMP-003, REQ-CMP-005, CMP-025 | CMP |
| BR-LOC-02 | REQ-TEN-006, CMP-026 | TEN, CMP |
| BR-LOC-03 | REQ-SET-001, UI-009..012, NFR-LOC-01 | SET, UI |
| BR-LOC-04 | REQ-SET-002, NFR-LOC-02 | SET |
| BR-CUR-01 | REQ-SET-003, REQ-POS-004 | SET, POS |
| BR-CUR-02 | REQ-SET-003 | SET |
| BR-PLUG-01 | REQ-CMP-002, SEC-059 | CMP |
| BR-PLUG-02 | REQ-CMP-002, REQ-CMP-001, NFR-MAINT-02 | CMP |

---

# 13. Traceability Matrix

## 13.1 BRD Functional Requirements → SRS Requirements

| BRD FR | SRS Requirements |
|--------|------------------|
| FR-PH-01 | REQ-BR-001, CMP-001 |
| FR-PH-02 | REQ-SAL-006 |
| FR-PH-03 | REQ-POS-011 |
| FR-PH-04 | REQ-POS-001, NFR-PERF-02 |
| FR-PH-05 | REQ-POS-012, NFR-RELI-01 |
| FR-INV-01 | REQ-MED-001..002, REQ-MED-012, REQ-MED-010 |
| FR-INV-02 | REQ-INV-001, REQ-INV-002 |
| FR-INV-03 | REQ-INV-004, REQ-AI-004 |
| FR-INV-04 | REQ-INV-005 |
| FR-INV-05 | REQ-INV-006, REQ-INV-008 |
| FR-INV-06 | REQ-INV-003, REQ-DASH-005 |
| FR-INV-07 | REQ-INV-009 |
| FR-POS-01 | REQ-POS-001, REQ-POS-002 |
| FR-POS-02 | REQ-POS-004 |
| FR-POS-03 | REQ-POS-005 |
| FR-POS-04 | REQ-POS-006 |
| FR-POS-05 | REQ-POS-007, REQ-POS-008 |
| FR-POS-06 | REQ-POS-009 |
| FR-POS-07 | REQ-POS-010, REQ-SAL-003 |
| FR-PUR-01 | REQ-PUR-001 |
| FR-PUR-02 | REQ-PUR-002 |
| FR-PUR-03 | REQ-PUR-003 |
| FR-PUR-04 | REQ-SUP-003 |
| FR-PUR-05 | REQ-SUP-001 |
| FR-CUST-01 | REQ-CUS-001, REQ-CUS-006 |
| FR-CUST-02 | REQ-CUS-002, REQ-CUS-004 |
| FR-CUST-03 | REQ-CUS-003 |
| FR-RX-01 | REQ-RX-001, REQ-CUS-005 |
| FR-RX-02 | REQ-RX-002, REQ-RX-003 |
| FR-RX-03 | REQ-RX-004 |
| FR-RX-04 | REQ-RX-005 |
| FR-RX-05 | REQ-RX-006, REQ-CMP-005 |
| FR-ACC-01 | REQ-ACC-001 |
| FR-ACC-02 | REQ-ACC-002, REQ-ACC-003, REQ-ACC-008 |
| FR-ACC-03 | REQ-ACC-004 |
| FR-ACC-04 | REQ-ACC-005 |
| FR-ACC-05 | REQ-ACC-006, REQ-CMP-003 |
| FR-REP-01 | REQ-RPT-001, REQ-SAL-002, REQ-DASH-001 |
| FR-REP-02 | REQ-RPT-002 |
| FR-REP-03 | REQ-RPT-003, REQ-RPT-005 |
| FR-REP-04 | REQ-RPT-004, REQ-CMP-007 |
| FR-BR-01 | REQ-BR-002 |
| FR-BR-02 | REQ-BR-005 |
| FR-BR-03 | REQ-BR-003 |
| FR-USR-01 | REQ-USR-001, REQ-USR-003, REQ-ROL-002 |
| FR-USR-02 | REQ-USR-002 |
| FR-USR-03 | REQ-AUD-002, REQ-USR-004 |
| FR-SUB-01 | REQ-SUB-001, REQ-MKT-002 |
| FR-SUB-02 | REQ-SUB-002, REQ-SUB-003 |
| FR-SUB-03 | REQ-SUB-004 |
| FR-SUB-04 | REQ-SUB-005 |
| FR-TEN-01 | REQ-TEN-001 |
| FR-TEN-02 | REQ-TEN-002, REQ-SET-004, REQ-SET-005 |
| FR-TEN-03 | REQ-TEN-003, REQ-DASH-004, REQ-NOT-001 |
| FR-TEN-04 | REQ-TEN-004, REQ-MED-007 |
| FR-AI-01 | REQ-AI-001 |
| FR-AI-02 | REQ-AI-002 |
| FR-AI-03 | REQ-AI-003, REQ-TEN-005 |
| FR-MKT-01 | REQ-MKT-001, REQ-MKT-004, API-010 |
| FR-MKT-02 | REQ-MKT-002 |
| FR-LOC-01 | REQ-CMP-001 |
| FR-LOC-02 | REQ-SET-001 |
| FR-LOC-03 | REQ-SET-003 |
| FR-LOC-04 | REQ-SET-002 |
| FR-LOC-05 | REQ-CMP-003, REQ-ACC-006 |
| FR-LOC-06 | REQ-MED-006, REQ-CMP-006 |
| FR-LOC-07 | REQ-CMP-007, REQ-RPT-004 |

## 13.2 BRD Processes → SRS Requirements

| BRD Process | SRS Requirements |
|-------------|------------------|
| P01 Sales & Dispensing | REQ-POS-001..009, REQ-POS-011, REQ-SAL-001 |
| P02 Prescription Fulfillment | REQ-RX-001..007, REQ-CUS-005 |
| P03 Sales Returns | REQ-POS-006, REQ-SAL-005 |
| P04 Purchasing & Procurement | REQ-PUR-001, REQ-PUR-004..006, REQ-INV-004 |
| P05 Goods Receipt & QC | REQ-PUR-002 |
| P06 Supplier Returns & Claims | REQ-PUR-003, REQ-SUP-004, REQ-SUP-006 |
| P07 Inventory Adjust/Count/Transfer | REQ-INV-005..008 |
| P08 Expiry & Recall | REQ-INV-003, REQ-INV-009, REQ-INV-010, REQ-NOT-002/003 |
| P09 Cash & Day-Close | REQ-POS-011, REQ-SAL-006 |
| P10 Accounting Posting & Tax | REQ-ACC-001..008 |
| P11 Inter-Branch Transfer | REQ-INV-008, REQ-BR-005 |
| P12 Distribution Dispatch (Warehouse) | REQ-PUR-002 (foundation), REQ-MKT-003 (design-in) |
| P13 Tenant Onboarding & Subscription | REQ-TEN-001..006, REQ-SUB-001..007 |
| P14 User/Role & Access | REQ-USR-001..005, REQ-ROL-001..005 |
| P15 Reporting & Compliance | REQ-RPT-001..007, REQ-DASH-001 |
| P16 Customer Credit & Loyalty | REQ-CUS-002, REQ-CUS-003, REQ-CUS-004 |
| P17 Localization & Compliance Config | REQ-CMP-001..008, REQ-TEN-006, REQ-SET-001..003 |

## 13.3 BRD NFRs → SRS NFRs

| BRD NFR | SRS NFR |
|---------|---------|
| NFR-N-01 | NFR-AVAIL-01/02 |
| NFR-N-02 | NFR-PERF-01 |
| NFR-N-03 | NFR-SCAL-01 |
| NFR-N-04 | NFR-SCAL-02 |
| NFR-N-05 | NFR-SEC-01/02, SEC-044 |
| NFR-N-06 | NFR-PRIV-01, SEC-037, REQ-CMP-004 |
| NFR-N-07 | NFR-AUDIT-02, REQ-AUD-002 |
| NFR-N-08 | NFR-RELI-01, REQ-POS-012 |
| NFR-N-09 | NFR-ACC-03, UI-015, BRD NFR-N-09 |
| NFR-N-10 | EXT-BAR/RCP/QR, REQ-SET-006 |
| NFR-N-11 | NFR-PORT-02, REQ-SET-001 |
| NFR-N-12 | NFR-BACK-01/02, NFR-DR-01/02 |
| NFR-N-13 | NFR-AVAIL (support tiers), NFR-OBS-03 |
| NFR-N-14 | NFR-AUDIT-03, REQ-AUD-003, DB-022..024 |
| NFR-N-15 | NFR-PORT-03, REQ-TEN-004 |
| NFR-N-16 | NFR-SCAL-04, NFR-CLOUD-02 |
| NFR-N-17 | NFR-LOC-01, NFR-PORT-02 |
| NFR-N-18 | NFR-LOC-03 |
| NFR-N-19 | NFR-SEC-04, SEC-059, REQ-CMP-002 |

## 13.4 BRD KPIs → SRS Artifacts

| BRD KPI | SRS Artifacts |
|---------|---------------|
| KPI-10 (availability) | NFR-AVAIL-01 |
| KPI-11 (transaction response) | NFR-PERF-01..03 |
| KPI-12 (rule enforcement) | Section 12 mapping, REQ-CMP-001 |
| KPI-13 (audit capture) | REQ-AUD-001 |
| KPI-14 (reconciliation) | NFR-DINT-03, REQ-ACC-007, REQ-SAL-006 |
| KPI-15/16 (expiry/stockout reduction) | REQ-INV-003, REQ-INV-004, REQ-DASH-005 |
| KPI-17 (sales capture) | REQ-SAL-006 |
| KPI-21 (data export ≤ 24 h) | REQ-TEN-004 |
| KPI-22 (RTO ≤ 4 h) | NFR-DR-01 |
| KPI-23 (market-pack readiness) | REQ-CMP-008 |

---

# 14. Risks

Technical/engineering risks are derived from the BRD business risk register (RK-01..19) and translated to the engineering context. Likelihood (L) and Impact (I): H/M/L. Reassessed at architecture review and quarterly.

| ID | Risk | L | I | Engineering Mitigation |
|----|------|---|---|------------------------|
| RK-E01 | Multi-tenant isolation defect exposing tenant/patient data (RK-06/10) | M | H | Isolation-by-design (MT-006..009); automated cross-tenant probes in CI (MT-024, SEC-058); penetration testing before launch (SEC-044). |
| RK-E02 | Market-pack isolation breach or pack defect undermines "one core, many markets" (RK-19) | M | H | Runtime isolation (REQ-CMP-002, SEC-059); sandbox validation + versioned activation (BR-PLUG-02); pack regression suite. |
| RK-E03 | ZATCA e-invoicing misimplementation blocks KSA go-live / penalty exposure (RK-16) | H | H | Dedicated e-invoicing workstream (REQ-ACC-006); sandbox validation with authority; external tax expert review (BRD ST-14); early start. |
| RK-E04 | Performance targets missed at scale (checkout, queries at 100k+ lines) (RK-06) | M | H | Load testing to NFR-SCAL-01; indexed/partitioned reads (NFR-DBP); caching strategy (NFR-CACH); early performance budgets in CI. |
| RK-E05 | Data-integrity failure (negative stock, unbalanced postings, audit gaps) (RK-07) | M | H | Persistence-layer invariants (NFR-DINT); transactionality (DB-005); reconciliation jobs; immutable append-only audit (REQ-AUD-001/004). |
| RK-E06 | Arabic RTL / mixed-script defects erode trust (RK-18) | M | H | Arabic-first QA matrix (NFR-LOC-05); native-speaker UX review; bilingual test cases in CI. |
| RK-E07 | Scope creep into AI/Marketplace/patient app during MVP (RK-11) | M | H | MoSCoW discipline; roadmap gates (BRD §18); change control on OOS list; design-in only for AI/Marketplace. |
| RK-E08 | Migration failure/loss from incumbent systems (RK-04) | H | H | Structured migration toolkit; dry-run + validation reports + rollback (REQ-MED-007, REQ-TEN-004); support during switch-over. |
| RK-E09 | Payment/billing integration dependency delays launch (RK-12, DEC-06) | M | M | Payment abstraction (EXT-PAY); fallback manual billing path; early integration. |
| RK-E10 | Observability gap hides tenant issues (RK-05 retention) | M | M | Structured logs/metrics/tracing (NFR-OBS); tenant health scoring (REQ-TEN-003); alerting on SLO breaches. |
| RK-E11 | Key-personnel dependency in delivery (RK-13) | M | M | Documentation standards; cross-training; knowledge-continuity plans. |
| RK-E12 | Plugin framework over-engineered vs MVP needs (counter-risk) | M | M | Minimal viable pack interface first; GCC/Yemen packs drive requirements; defer generalization. |
| RK-E13 | Cross-GCC regulatory variance increases pack work (RK-15) | H | M | Pack per state; shared framework; phased market rollout; legal validation per pack (OI-02). |
| RK-E14 | Security breach of patient/financial data (RK-10) | L | H | ASVS L1/L2 (SEC-041); encryption (SEC-029..033); least privilege; incident response (SEC-045). |
| RK-E15 | Concurrency bugs in high-volume POS (oversell races) (RK-07) | M | H | DB-008/009 concurrency controls; race-condition tests; inventory reservation semantics. |

---

# 15. Future Requirements

Future requirements are staged per BRD §18 (Phases 2–6). They are design-in considerations now; activation is gated by phase KPIs.

| ID | Future Requirement | Phase | Design-in Hook |
|----|--------------------|-------|----------------|
| FUT-01 | Warehouse distribution/dispatch module (P12) | V2 | REQ-PUR-002 foundations, REQ-MKT-003 data model |
| FUT-02 | Credit-management maturity (statements, aging, collections) | V2 | REQ-CUS-002/004 |
| FUT-03 | Handheld barcode inventory app | V2 | REQ-INV-012 |
| FUT-04 | Promotions engine | V2 | REQ-SAL-004 |
| FUT-05 | Multi-language packs beyond AR/EN | V2+ | REQ-SET-001, NFR-PORT-02 |
| FUT-06 | Offline-POS resilience review | V2 | REQ-POS-012, NFR-RELI-01 |
| FUT-07 | Deep accounting: fixed assets-light, AR/AP maturity, multi-ledger, financial statements | V3 | REQ-ACC-008 |
| FUT-08 | External accounting package integrations | V3 | EXT interfaces, API section |
| FUT-09 | Insurance/TPA claims module (configurable per market) | V3 | REQ-CMP-037 |
| FUT-10 | Enterprise head-office suite (budgets, margin control, treasury) | Enterprise | REQ-BR-002, REQ-DASH-003 |
| FUT-11 | Multi-region hosting/data residency | Enterprise | NFR-CLOUD-04, MT-006 |
| FUT-12 | AI products: forecasting, expiry prediction, anomaly detection, insights, NL dashboards | Phase 5 | REQ-AI-002..005, REQ-AI-001 |
| FUT-13 | Marketplace: add-on catalog live, B2B ordering hub, partner API + sandbox | Phase 6 | REQ-MKT-001..004 |
| FUT-14 | OCR prescription intake | Phase 5/6 | EXT-OCR |
| FUT-15 | Patient-facing app / online ordering / delivery (add-on) | V2+ add-on | OOS-03 revisit |

---

# 16. Appendices

## 16.1 Validation Checklist

Verification that this SRS meets quality standards (IEEE 29148, ISO 25010, OWASP, OpenAPI best practices) and the BRD commitments.

| # | Check | Status |
|---|-------|--------|
| V-01 | Every BRD business rule mapped to SRS requirement(s). | ✔ Section 12 (all BR-* rules) |
| V-02 | Every BRD functional requirement (FR-*) traced. | ✔ Section 13.1 (FR-PH-01..FR-LOC-07) |
| V-03 | Every BRD process (P01..P17) traced. | ✔ Section 13.2 |
| V-04 | Every BRD NFR (NFR-N-01..19) traced. | ✔ Section 13.3 |
| V-05 | Every requirement has a unique ID. | ✔ REQ-/NFR-/EXT-/UI-/API-/SEC-/MT-/DB-/CMP- schemes |
| V-06 | Every requirement is testable (measurable target or observable behavior). | ✔ Acceptance criteria per functional requirement; measurable NFR targets |
| V-07 | Every requirement has acceptance criteria. | ✔ AC-REQ-* per functional requirement |
| V-08 | Every requirement belongs to a module. | ✔ 22 modules, Section 3 |
| V-09 | No duplicated requirements. | ✔ Reviewed during authoring; module boundaries enforced |
| V-10 | No ambiguity (no undefined qualifiers). | ✔ Measurable targets; glossary (Section 1.3 of front matter) |
| V-11 | Scope discipline (no OOS items implemented). | ✔ BRD §8 respected; design-in only for AI/Marketplace |
| V-12 | Security coverage per OWASP ASVS. | ✔ Section 8 (L1 baseline, L2 for sensitive flows) |
| V-13 | Localization (AR RTL/EN, Hijri/Gregorian, multi-currency) covered. | ✔ FR-LOC trace, NFR-LOC, CMP-025..029 |
| V-14 | Multi-tenant isolation covered. | ✔ Section 9, SEC-057..059 |
| V-15 | NFR coverage across all mandated categories. | ✔ Section 4 (20 categories) |
| V-16 | External interfaces specified. | ✔ Section 5 (13 interfaces) |
| V-17 | API standards specified. | ✔ Section 7 |
| V-18 | Database logical requirements specified (no physical design). | ✔ Section 10 |
| V-19 | Compliance requirements specified. | ✔ Section 11 |
| V-20 | Risks identified with mitigations. | ✔ Section 14 (RK-E01..15) |
| V-21 | Future requirements staged with design-in hooks. | ✔ Section 15 |
| V-22 | Document consistent with approved BRD v1.1. | ✔ No contradictions introduced; traceability maintained |

## 16.2 Open Issues & Decisions

Non-blocking items requiring decisions or validation; inherited from BRD Appendix B plus SRS-specific items.

| ID | Item | Deadline | Impact if unresolved |
|----|------|----------|----------------------|
| OI-01 | PRD artefact alignment: BRD v1.1 and this SRS exist; the PRD (feature catalog/epics/user stories) is referenced as approved but was not present in the workspace. Perform alignment when available. | With PRD delivery | SRS stands alone; traceability to PRD IDs to be added. |
| OI-02 | Legal validation of GCC + Yemen market packs (BRD AS-02). | SRS/launch gate | Pack rules (tax, e-invoicing, Rx, controlled register) pending legal confirmation. |
| OI-03 | Go-live sequencing and primary GCC launch markets (BRD DEC-08/DEC-09). | M3 | ZATCA workstream and pack priorities. |
| OI-04 | Hosting region / data residency at MVP (BRD DEC-05). | M6 | NFR-CLOUD-04, NFR-PRIV-03. |
| OI-05 | Payment gateway selection (BRD DEC-06). | M6 | EXT-PAY implementation detail. |
| OI-06 | Pricing/tier structure and pilot terms (BRD DEC-04). | M6 | SUB plan parameters, KPI baselines. |
| OI-07 | Accounting package integration targets (BRD DEC-07). | M18 | V3 integrations. |
| OI-08 | Yemen commercial model: USD/SAR invoicing vs YER (BRD DEC-10). | M6 | REQ-SET-003 behavior, RK-17. |
| OI-09 | MVP segment prioritization split (BRD DEC-03). | M3 | Onboarding toolkit and chain-feature scope. |

## 16.3 Recommendations

| ID | Recommendation | Owner | Priority |
|----|----------------|-------|----------|
| REC-01 | Baseline this SRS at the Architecture Review Gate and re-issue as v1.1 with architecture decisions. | PM + Architecture | Immediate |
| REC-02 | Build the compliance/market-pack framework first; it is the highest rework risk (BRD ST-03). | Architecture | MVP start |
| REC-03 | Instrument acceptance-criteria-to-test traceability in the QA tooling from sprint 1 (KPI-12/13). | QA | Sprint 1 |
| REC-04 | Run performance and cross-tenant isolation load tests before the 12-month go-live gate (RK-E01/RK-E04). | DevOps/QA | Pre-go-live |
| REC-05 | Treat Arabic RTL as first-class QA (native-speaker matrix) from the first sprint (RK-E06). | QA/UX | Sprint 1 |
| REC-06 | Validate KPI baselines with pilot partners before committing commercial targets (BRD ST-12). | BA + CS | Pilot |
| REC-07 | Freeze the MVP requirement set (MoSCoW Musts in Section 3 marked Must) and route additions through change control (RK-E07). | PM | M3 |
| REC-08 | Start ZATCA e-invoicing workstream early with external tax expertise if KSA is in wave 1 (RK-E03). | PM + Compliance | M3 |
| REC-09 | Adopt idempotency and event-sourcing patterns for transactional flows to support AI-readiness and reliability (REQ-AI-001, NFR-RELI-03). | Architecture | MVP |

## 16.4 Standards and References

- IEEE 29148-2018 — Requirements Engineering
- ISO/IEC/IEEE 12207 — Software Life Cycle Processes
- ISO/IEC 25010 — Quality Model
- OWASP ASVS 4.0 / OWASP Top 10
- OpenAPI Specification 3.1
- BABOK v3
- BPMN 2.0
- BRD v1.1 — PharmaCloud ERP Business Analysis Package (approved, 2026-08-05)
- WCAG 2.1 AA (accessibility)

---

*End of PharmaCloud ERP Software Requirements Specification v1.0 — Draft for review.*

---

## SRS Requirement Inventory (Appendix)

Quick reference of requirement counts by section (for governance):

| Section | ID Range | Count (approx.) |
|---------|----------|-----------------|
| 3.1 Dashboard | REQ-DASH-001..009 | 9 |
| 3.2 Medicines | REQ-MED-001..012 | 12 |
| 3.3 Inventory | REQ-INV-001..012 | 12 |
| 3.4 POS | REQ-POS-001..012 | 12 |
| 3.5 Sales | REQ-SAL-001..006 | 6 |
| 3.6 Purchasing | REQ-PUR-001..007 | 7 |
| 3.7 Suppliers | REQ-SUP-001..006 | 6 |
| 3.8 Customers | REQ-CUS-001..006 | 6 |
| 3.9 Prescriptions | REQ-RX-001..007 | 7 |
| 3.10 Accounting | REQ-ACC-001..008 | 8 |
| 3.11 Reports | REQ-RPT-001..007 | 7 |
| 3.12 Branches | REQ-BR-001..005 | 5 |
| 3.13 Users | REQ-USR-001..005 | 5 |
| 3.14 Roles | REQ-ROL-001..005 | 5 |
| 3.15 Notifications | REQ-NOT-001..005 | 5 |
| 3.16 Subscriptions | REQ-SUB-001..007 | 7 |
| 3.17 Tenant Mgmt | REQ-TEN-001..006 | 6 |
| 3.18 Marketplace | REQ-MKT-001..004 | 4 |
| 3.19 AI Readiness | REQ-AI-001..005 | 5 |
| 3.20 Compliance | REQ-CMP-001..008 | 8 |
| 3.21 Settings | REQ-SET-001..006 | 6 |
| 3.22 Audit Log | REQ-AUD-001..005 | 5 |
| 4 NFR | NFR-PERF..DBP | 60+ |
| 5 External Interfaces | EXT-* | 50+ |
| 6 UI | UI-001..059 | 59 |
| 7 API | API-001..047 | 47 |
| 8 Security | SEC-001..059 | 59 |
| 9 Multi-Tenant | MT-001..024 | 24 |
| 10 Database | DB-001..034 | 34 |
| 11 Compliance | CMP-001..037 | 37 |
| **Total** | — | **≈ 480 requirements** |

*End of document.*
