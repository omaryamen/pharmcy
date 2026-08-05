# PharmaCloud ERP — Business Analysis Package

**Document Version:** 1.1  
**Document Owner:** Business Analysis  
**Document Status:** Approved for SRS Handoff  
**Standards Applied:** BABOK v3 · BPMN 2.0 · IEEE 29148 · ISO 9001 documentation principles  
**Project Type:** Enterprise Multi-Tenant SaaS Pharmacy ERP  
**Prepared For:** Product Manager · Software Architect · Executive Sponsor  

---

## Document Control

| Item | Detail |
|---|---|
| Version | 1.1 |
| Date | 2026-08-05 |
| Status | Baseline — ready for SRS phase |
| Revision | v1.1: launch markets confirmed (Yemen + GCC), Arabic/English languages, country-neutral plugin architecture |
| Change Authority | Product Council (PM + Architecture + Business Analysis) |
| Review Cycle | Quarterly or upon material scope change |
| Related Future Artefacts | Software Requirements Specification (SRS), Business Process Diagrams (BPMN), Feature Catalog, Test Strategy |

---

# Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Business Vision](#2-business-vision)
3. [Product Mission](#3-product-mission)
4. [Stakeholder Matrix](#4-stakeholder-matrix)
5. [User Personas](#5-user-personas)
6. [Business Goals and Objectives](#6-business-goals-and-objectives)
7. [Business Scope](#7-business-scope)
8. [Out-of-Scope Items](#8-out-of-scope-items)
9. [Business Processes (BPMN 2.0)](#9-business-processes-bpmn-20)
10. [Business Rules](#10-business-rules)
11. [Functional Requirements (High-Level)](#11-functional-requirements-high-level)
12. [Non-Functional Requirements (Business-Level)](#12-non-functional-requirements-business-level)
13. [Business Risks](#13-business-risks)
14. [Business Constraints](#14-business-constraints)
15. [Business Assumptions](#15-business-assumptions)
16. [Success Metrics (KPIs)](#16-success-metrics-kpis)
17. [Feature Prioritization (MoSCoW)](#17-feature-prioritization-moscow)
18. [Product Roadmap](#18-product-roadmap)
19. [Business Opportunities](#19-business-opportunities)
20. [Strategic Recommendations](#20-strategic-recommendations)
21. [Final Business Summary](#21-final-business-summary)
22. [Validation Checklist](#22-validation-checklist)
23. [Appendix A — Traceability Matrix (Excerpt)](#23-appendix-a--traceability-matrix-excerpt)
24. [Appendix B — Open Decisions Log](#24-appendix-b--open-decisions-log)

---

# 1. Executive Summary

PharmaCloud ERP is a **cloud-native, multi-tenant SaaS platform** that replaces fragmented, offline, and paper-based pharmacy operations with a single integrated operating system covering point-of-sale, prescription management, inventory control, purchasing, supplier management, accounting, branch management, and reporting.

Independent pharmacies today run on disconnected tools: a cash register, a stock book or spreadsheet, a manual expiry ledger, and paper prescriptions. This produces avoidable losses from **expired stock**, **out-of-stocks**, **pricing errors**, **sale under-reporting**, and **poor supplier terms**. Chains compound the problem with no consolidated view of stock, sales, or cash across branches. The **pharmacy market is heavily regulated**, yet most incumbents treat compliance as an afterthought.

PharmaCloud ERP will:
- Give pharmacy owners **real-time, correct inventory and financial data** on any device.
- Enforce **safety-critical business rules** (expiry, batch traceability, controlled-substance audit trails, prescription validity) automatically.
- Provide **multi-branch consolidation** for chains and distribution visibility for warehouses.
- Generate revenue as a **recurring subscription SaaS** with clear expansion paths (AI insights, marketplace, B2B ordering).

The **first deployment markets are confirmed as Yemen and the GCC** (Saudi Arabia, UAE, Qatar, Kuwait, Bahrain, Oman), with **Arabic (RTL) and English** as the initial languages. The product is built on a **country-neutral core with plugin-based market packs** covering taxation, currency, language, calendar, drug reference, e-prescription, and health-authority reporting — so one core serves every GCC state, Yemen, and any future market without re-architecture.

**Recommended sequencing:** a production-grade **MVP in ~12 months** targeting independent pharmacies and small chains, with paid pilot partners co-designing the product; **V2** adds warehouse distribution, credit management, and advanced chain consolidation; **V3** adds deep accounting, financial reporting, and integrations; **Enterprise** adds large-chain and head-office capabilities, SLA-backed contracts, and custom integrations; **AI layer** delivers demand forecasting, purchase intelligence, and insight automation.

**Key numbers this package commits to (KPI targets):** 99.5% platform availability, <2 s core transaction response, 100% expiry-before-sale enforcement, <30 min end-user onboarding to first sale, and >1,500s (scale) concurrent terminals per region per tenancy model. Detailed targets in Section 16.

**Open decisions** now focus on go-live sequencing and compliance-pack validation (DEC-08…DEC-10); none block the start of the SRS phase.

---

# 2. Business Vision

> **To be the operating system of modern pharmacy — making every pharmacy run on correct data, safe dispensing, and profitable decisions.**

PharmaCloud ERP exists so that pharmacy owners and operators — independent, chain, or warehouse — no longer lose money to expired stock, stockouts, pricing errors, or blind management. Every pharmacy that runs on PharmaCloud will know, at any moment, exactly what it owns, what it owes, what is expiring, what sold, and what to buy next — from any device, in the cloud, under a subscription they can afford.

In five years, PharmaCloud ERP aspires to be the leading cloud pharmacy platform in its launch region, a trusted custodian of regulated pharmacy data, and the natural marketplace where pharmacies buy smarter from suppliers.

---

# 3. Product Mission

**PharmaCloud ERP delivers one integrated, rule-enforcing, multi-tenant cloud platform for pharmacy operations** — covering sales, prescriptions, inventory, purchasing, suppliers, accounting, and branch management — so that pharmacies operate with accurate data, full regulatory traceability, and higher profitability, while PharmaCloud earns recurring revenue through subscription, add-on, and marketplace services.

The mission is measured by three commitments:
1. **Correctness** — the system refuses unsafe or invalid transactions (expired stock, overselling, invalid prescriptions, tax mismatches).
2. **Control** — owners and chain managers see live, consolidated operational and financial truth.
3. **Growth** — the platform grows with the customer from one store to many, and adds intelligence as it matures.

---

# 4. Stakeholder Matrix

Per BABOK v3, stakeholders are identified by role, interest, power, and engagement need.

| ID | Stakeholder | Description | Interest | Power | Engagement Strategy | Primary Needs |
|----|-------------|-------------|----------|-------|---------------------|---------------|
| STK-01 | Executive Sponsor / Board | Funds and owns the product vision, approves roadmap and budget | High | High | Monthly sponsor updates, stage-gate approvals | ROI, market viability, risk transparency, compliance posture |
| STK-02 | Product Manager | Owns backlog, prioritization, commercial decisions | High | High | Continuous collaboration, BA supports requirements | Clear requirements, scope control, roadmap evidence |
| STK-03 | Software Architect | Owns technical design, multi-tenant model, integrations | High | High | Architecture review board, NFR handoff | Complete, unambiguous requirements; traceability |
| STK-04 | Business Analysis | Owns requirements quality, process models, validation | High | Medium | Self | Validated, testable, traceable requirements |
| STK-05 | Engineering / Delivery | Builds, tests, ships | Medium | Medium | Refinement sessions, DoR/DoD | Acceptance criteria, business context |
| STK-06 | QA / Test | Verifies requirements and rules | Medium | Medium | Test strategy alignment | Testable business rules, measurable NFRs |
| STK-07 | Security & Compliance Officer | Guards data privacy, auditability, regulated workflows | High | High | Mandatory review gate | Audit logs, retention, consent, controlled substance handling |
| STK-08 | Sales & Marketing | Acquires customers, positioning, packaging | High | Medium | Pricing/positioning inputs | Differentiators, demo-able features, competitive story |
| STK-09 | Customer Success & Onboarding | Trains and retains customers | Medium | Medium | Feedback loops, onboarding toolkit | Usability, migration tooling, training content |
| STK-10 | Support / Helpdesk | Tier-1/2 support | Medium | Low | Escalation and FAQ inputs | Diagnostics, tenant context, knowledge base |
| STK-11 | Pilot Partner Pharmacies | Co-design MVP, ground-truth requirements | High | High | Structured pilot program, design-partner agreements | Working MVP, migration help, fair pilot terms, real value |
| STK-12 | Pharmacy Owner (SMB customer) | Buyer and user; pays subscription | High | High | Beta program, feedback council | Simple onboarding, no data loss, better margins |
| STK-13 | Pharmacist-in-Charge | Licensed operator; legally accountable for dispensing | High | High | Workflow validation | Safety enforcement, prescription record completeness |
| STK-14 | Pharmacy Staff (cashiers, assistants) | Daily system users | Medium | Medium | UX validation, field observation | Speed, low training burden, minimal errors |
| STK-15 | Chain Regional / Operations Manager | Manages multiple branches | High | Medium | Chain advisory group | Consolidation, inter-branch transfer, policy controls |
| STK-16 | Warehouse / Distribution Manager | Manages bulk stock and B2B supply | Medium | Medium | Process walkthroughs | Batch/expiry at scale, credit, dispatch accuracy |
| STK-17 | Accountant / Finance Officer | Books, tax, reconciliation | Medium | Medium | Accounting domain validation | Day-close accuracy, tax exports, audit trail |
| STK-18 | Health & Tax Authorities (SFDA, MOHAP, NHRA, MOPH, SBDMA; ZATCA and other GCC tax bodies) | Enforce pharmacy licensing, drug registration, e-invoicing, and tax law (indirect users) | Low (indirect) | High | Market-pack compliance mapping; report/e-invoice exports per authority | Traceable records, correct tax treatment, compliant reporting per market |
| STK-19 | Patient / Customer (end consumer) | Indirect beneficiary | Low | High | Journey reviews, anonymized insights | Fast checkout, prescription safety, data privacy |
| STK-20 | Supplier / Wholesaler | Trading partner via purchase & returns | Medium | Medium | Supplier portal (later), B2B pilots | Order accuracy, credit terms, claims handling |
| STK-21 | Integrators / Third-Party ISVs | Future marketplace and API ecosystem | Low | Medium | Partner program (later) | Open APIs, documentation, sandbox |
| STK-22 | Investors / Commercial Partners | Fund future rounds; distribution partnerships | Medium | High | Quarterly commercial reviews | Growth metrics, CAC/LTV, expansion story |

**Stakeholder coverage check:** buyer, user, operator, regulatory, financial, technical, commercial, and ecosystem roles are all represented. No missing category identified (see Validation Checklist).

---

# 5. User Personas

Personas represent the real user groups and their job-to-be-done. Each persona includes their goals, pain points, and success criteria used for requirement validation. All personas operate in a bilingual **Arabic (RTL) / English** environment, reflecting the commercial reality of the GCC and Yemen markets.

## P-01 — "Raj", Independent Pharmacy Owner
- **Profile:** Owns 1–2 pharmacies, 40–55 years old, moderate technical comfort, buys stock personally, checks the ledger at night.
- **Goals:** Know daily sales and profit; stop losing money to expiry; negotiate better supplier terms; minimal time spent on bookkeeping.
- **Pain points:** Stock book mismatches; expired items sitting on shelves; no idea which products actually make money; cash drawer never ties out.
- **Success criteria:** Opens dashboard daily in <1 minute; sees expiry watchlist; day-close reconciles without manual spreadsheet work.

## P-02 — "Dr. Ayesha", Pharmacist-in-Charge (Licensed)
- **Profile:** Professionally licensed, legally accountable for dispensing; manages 3–5 staff; highly risk-averse.
- **Goals:** Every dispense is legally traceable; controlled substances fully recorded; no expired or recalled product leaves the counter; prescriptions validated.
- **Pain points:** Paper Rx archives; no recall visibility; staff shortcuts on documentation.
- **Success criteria:** System blocks invalid sales; audit trail exportable on request; recall workflow clears affected batches in one action.

## P-03 — "Sam", Store Manager (Chain Branch)
- **Profile:** Runs a single branch of a 10-store chain; reports to regional manager; handles staff rostering and daily cash.
- **Goals:** Hit branch sales targets; keep stock healthy; follow head-office policy; accurate end-of-day close.
- **Pain points:** Manually emailing reports to head office; no inter-branch transfer visibility; inconsistent discount policy.
- **Success criteria:** Head office sees branch live; transfers are tracked end-to-end; discount policies enforced centrally.

## P-04 — "Mei", Cashier / Sales Assistant
- **Profile:** Fast-paced counter role, high transaction volume, modest tech skills, staff turnover high.
- **Goals:** Ring sales in <10 seconds; no price lookup errors; handle mixed cash/card/qr payments; print receipts.
- **Pain points:** Slow legacy POS; typing drug names; price disputes; returns are painful.
- **Success criteria:** Barcode-first checkout; fast search with autocorrect; guided refunds; minimal training (<30 min).

## P-05 — "Omar", Purchase / Inventory Manager (Warehouse)
- **Profile:** Manages thousands of SKUs and 20+ suppliers; negotiates terms; tracks expiry across lots.
- **Goals:** Right stock at right cost; low expiry write-offs; high supplier fill-rate; clear batch traceability.
- **Pain points:** Manual reorder spreadsheets; split batches confuse stock; credit notes take weeks; expiry only found at shelf.
- **Success criteria:** Reorder suggestions from live demand; lot-level expiry tracking; supplier performance scorecards.

## P-06 — "Hina", Accounts / Finance Officer
- **Profile:** Bookkeeps for 5+ pharmacies or a chain; reconciles purchases, sales, taxes, and supplier payables.
- **Goals:** Accurate ledgers without re-keying; tax filings prepared in minutes; clean audit trail.
- **Pain points:** POS data doesn't match books; tax exports are manual; supplier credit notes lost.
- **Success criteria:** One-click day-close; tax-return-ready exports; integrated payables register.

## P-07 — "Daniel", Chain Regional Operations Manager
- **Profile:** Oversees 10–40 branches; enforces policy; analyzes performance; plans stock reallocation.
- **Goals:** Live consolidated P&L by branch; enforce pricing/policy centrally; rebalance stock between branches.
- **Pain points:** Weekly manual reports; branches out of policy; dead stock in one branch, stockout in another.
- **Success criteria:** Real-time consolidated dashboards; central policy push; transfer workflow with cost capture.

## P-08 — "Nadia", Tenant Administrator / IT Lead
- **Profile:** Configures the system for the pharmacy or chain; manages users, roles, branches, and subscriptions.
- **Goals:** Grant/revoke access instantly; keep roles compliant; manage subscriptions and add-ons.
- **Pain points:** Uncontrolled shared logins; cannot prove who did what; billing surprises.
- **Success criteria:** Role-based access control (RBAC) with audit trail; self-service subscription changes; named-user accountability.

## P-09 — "Priya", Patient / Customer (End Consumer — indirect)
- **Profile:** Buys OTC and prescription medicine; sensitive to price, safety, and privacy.
- **Goals:** Fast checkout; correct product; confidence that medicine is not expired; privacy respected.
- **Pain points:** Wrong item given; long queues; recalls only discovered at home.
- **Success criteria:** Correct, non-expired product every time; opt-in digital receipts and loyalty; data handled per privacy rules.

## P-10 — "Karim", PharmaCloud Customer Success Lead (Internal)
- **Profile:** Onboards new tenants, trains staff, drives retention and expansion.
- **Goals:** Fast time-to-value; low churn; upsell add-ons; capture feedback.
- **Pain points:** Manual data migration; long training; no in-product health view of tenants.
- **Success criteria:** Self-serve data import; guided onboarding; tenant health scores and usage alerts.

---

# 6. Business Goals and Objectives

## 6.1 Business Vision Statement (one line)
See Section 2.

## 6.2 Product Goals
| ID | Product Goal | Success Measure |
|----|--------------|-----------------|
| PG-01 | Provide a single integrated cloud platform covering all core pharmacy operational domains | Every core domain (Section 9) functional in product; no operational task requires an external tool |
| PG-02 | Enforce safety and regulatory rules automatically rather than by staff discipline | 100% of sales/Rx/expiry/controlled rules enforced at system level (BR rules pass rate) |
| PG-03 | Support independent pharmacies, chains, and warehouses on one architecture | Multi-branch and multi-tenant constructs native from MVP |
| PG-04 | Enable AI-ready intelligence on top of core transaction data | Data model and APIs support forecasting/insight modules by Roadmap Phase 5 |
| PG-05 | Provide an ecosystem for B2B ordering and add-ons (marketplace) | Marketplace roadmap committed post-Enterprise phase |
| PG-06 | Serve the GCC and Yemen from one country-neutral core via market packs | Two market packs (GCC, Yemen) active at MVP; zero country-specific code in the core |

## 6.3 Business Objectives (measured, time-bound)
| ID | Objective | Target | Horizon |
|----|-----------|--------|---------|
| BO-01 | Launch production-grade MVP across GCC and Yemen markets | Go-live with ≥10 pilot partner locations (GCC anchor, Yemen phased per DEC-08) | Month 12 |
| BO-02 | Establish recurring revenue | ≥70% of revenue from subscriptions; annual plan preference >40% | Year 2 |
| BO-03 | Achieve customer retention | Net revenue retention (NRR) ≥110%; logo churn <5%/yr | Year 2 onward |
| BO-04 | Expand to chain segment | ≥15% of active paying tenants are chains (2+ branches) | Year 2 |
| BO-05 | Grow total locations | ≥1,500 active locations by end of Year 3 | Year 3 |
| BO-06 | Demonstrate value to customers | Tenant-reported average of ≥15% reduction in expiry write-offs and stockouts within 6 months of adoption | Ongoing |
| BO-07 | Establish regulatory trust | 100% audit success in pilot partner regulatory reviews | Ongoing |
| BO-08 | Build ecosystem revenue | Marketplace + AI add-ons ≥10% of ARR | Year 4 |

---

# 7. Business Scope

## 7.1 In-Scope Domains (MVP and beyond)

| Domain | Description | MVP |
|--------|-------------|-----|
| **Pharmacy Operations** | Store setup, cash register/drawer management, day-close, counter workflows, patient counter interactions | ✔ |
| **Inventory Management** | Product master (drug + non-drug), batches/lots, expiry, stock levels, adjustments, transfers, cycle counts, reorder logic, recalls | ✔ |
| **Sales & POS** | Barcode checkout, cash/card/Qr/mixed payments, receipts, discounts, returns, voiding with reason capture, layaway | ✔ |
| **Purchasing** | Purchase orders, goods receipt, purchase returns, cost/landed cost, backordering | ✔ |
| **Supplier Management** | Supplier master, credit terms, performance scorecards, claims/credit notes, order history | ✔ (core) |
| **Customers** | Customer master (non-prescription), loyalty, credit customers (chain/warehouse), patient minimal profile (privacy-scoped) | ✔ (core) |
| **Prescription Management** | Rx intake, validation, fulfillment, repeats/refills, controlled substance log, archive, digital Rx interface (configurable) | ✔ (core) |
| **Accounting** | Chart of accounts, ledgers (AR/AP/cash/sales), day-close posting, tax computation and exports, financial reports | Post-MVP (V3) core; MVP tax-ready outputs |
| **Reporting** | Operational dashboards, sales, stock, expiry, profit, supplier, branch, cash, compliance reports | ✔ |
| **Branch Management** | Multi-branch tenancy, branch hierarchy, inter-branch transfers, consolidated reporting, central policy | ✔ (chains) |
| **User & Role Management** | RBAC, named users, permissions, audit trail, password/2FA policies, session control | ✔ |
| **Subscription Management** | Plans, add-ons, billing, invoicing, payments, upgrade/downgrade, suspension/reinstatement | ✔ |
| **Multi-Tenant SaaS Management** | Tenant lifecycle, isolation, onboarding, configuration, tenant health, feature flags, quota enforcement | ✔ |
| **AI Readiness** | Structured transaction data, analytics-ready schema, forecasting-ready demand signals, insight endpoints | Design-in ✔; product Phase 5 |
| **Future Marketplace Integration** | B2B ordering hub, add-on catalog, API ecosystem | Design-in ✔; product Phase 6 |
| **Localization & Compliance Plugin Framework** | Country-neutral core with pluggable market packs (taxation, currency, language, calendar, drug reference, e-prescription, health-authority reporting, e-invoicing) | ✔ (framework + GCC and Yemen packs) |
| **Multi-Currency & Languages** | Multi-currency (SAR, AED, QAR, KWD, BHD, OMR, YER, USD secondary); Arabic (RTL) and English interfaces; Gregorian + Hijri calendars | ✔ |

## 7.2 Scope Boundaries (who is in scope as a user/customer)
- **In scope:** pharmacies (independent, small/medium chain), medical/pharma warehouses/distributors, hospital/clinic pharmacy dispensaries (later phases).
- **In scope as trading parties:** suppliers, wholesalers, credit customers, patients (as privacy-scoped records), regulatory/tax authorities (via exports/reports only — no direct system access).
- **Out of scope as licensed end-users:** patients (no patient-facing portal in MVP), suppliers (no supplier self-service portal in MVP).

## 7.3 Market & Regulatory Context (GCC and Yemen)

The first deployment markets are the **GCC states and Yemen**. Each market requires a **market pack** (Section 7.4) covering its regulatory, tax, and commercial specifics. The table below is a **business-level orientation only — legal validation of every market pack is a required SRS-phase activity, and nothing here is a legal conclusion.**

| Market | Health Regulator (indicative) | Taxation (indicative) | Currency | Prescription Context | Business Notes |
|--------|--------------------------------|------------------------|----------|----------------------|----------------|
| Saudi Arabia | SFDA; ZATCA (tax) | VAT 15%; **ZATCA e-invoicing (FATOORAH Phase 2) mandatory** for VAT-registered businesses | SAR | Digital e-prescription (Wasfaty ecosystem) | Largest GCC pharmacy market; e-invoicing integration is a hard go-live gate for KSA |
| UAE | MOHAP + DHA (Dubai) + DOH (Abu Dhabi) | VAT 5% | AED | Federal and emirate-level e-prescription initiatives | Emirate-level variance requires configurable registers/reports |
| Qatar | Ministry of Public Health (MOPH) | VAT 5% | QAR | National e-health (Qatar Care) alignment | |
| Kuwait | MOH — Drug & Food Control | VAT not yet implemented | KWD | Paper Rx dominant | |
| Bahrain | NHRA | VAT 5% | BHD | Developing e-Rx | |
| Oman | MOH — DGPA | VAT 5% | OMR | Paper + developing e-Rx | |
| Yemen | SBDMA (Supreme Board for Drugs and Medical Appliances) | Local sales-tax arrangements; no unified GCC VAT | YER (USD widely used in trade) | Paper prescriptions; import-led supply chain | Volume/affordability market; currency volatility and payment-rail constraints (RK-17) |

**Business implications (scoping direction, subject to legal validation):**
- **Bilingual from day one:** Arabic (RTL) and English interfaces; mixed-script handling (Latin drug names inside an Arabic UI) is a quality requirement, not a translation task.
- **Tax is pluggable, not hard-coded:** a unified VAT framework with varying rates (5%/15%) plus market-specific e-invoicing (KSA ZATCA Phase 2) requires a pluggable tax engine driven by the active market pack.
- **Drug reference and barcoding vary:** national drug registration codes and GS1-based medicine barcodes (SFDA-aligned in KSA) are mapped per market pack.
- **Controlled substances are scheduled nationally:** registers and required documentation differ per state; the controlled-substance module must be market-configurable.
- **Prescription modes span digital to paper:** from fully digital (KSA) to paper (Yemen); the Rx module must support both through adapters.
- **Calendars:** Gregorian and Hijri display; business dates stored canonically (BR-LOC-04).
- **Multi-currency:** the GCC is multi-currency by nature; Yemen adds volatility and USD-trade practice — requiring base + secondary currency reporting (BR-CUR-01/02).

## 7.4 Localization & Compliance Plugin Framework (Architecture Envelope)

The core is **country-neutral**. All market-specific behavior is delivered as **market packs** — pluggable, versioned modules that define: tax and e-invoicing behavior; currency and localization (language, RTL, calendar, number/date formats); national drug reference codes and barcodes; prescription mode and digital-Rx adapters; controlled-substance registers and health-authority report formats; legal footers and receipt templates.

This is a **business-level requirement envelope, not a technical design** (the SRS/architecture elaborates the plugin mechanism). The business commitments are:
- A market pack can be activated per tenant and cannot modify the core (BR-PLUG-01).
- Market packs are versioned and validated in a sandbox before activation (BR-PLUG-02).
- Language, currency, calendar, and legal defaults come from the active market pack and tenant overrides (BR-LOC, BR-CUR).
- Adding a new market (e.g., another GCC state or a future market) requires a new pack — not core rework.

---

# 8. Out-of-Scope Items

Explicitly excluded. Inclusion requests require formal scope change.

| ID | Excluded Item | Rationale | Revisit |
|----|---------------|-----------|---------|
| OOS-01 | Manufacturing, compounding scheduling, and batch production | Not a manufacturer platform; compounding supported only as prescription-level records | Never for MVP/V2 |
| OOS-02 | Full ERP back-office (HR/payroll, fixed assets, procurement of non-medical) | Defeats focus; integrate rather than build | V3+ via integration |
| OOS-03 | Patient-facing portal/mobile app, online ordering, delivery dispatch | Regulatory and delivery-logistics complexity; separate product line | V2+ as add-on |
| OOS-04 | Telemedicine / e-consultation | Different licensed domain | Not planned in 3-yr roadmap |
| OOS-05 | Prescription insurance/TPA claims adjudication (realtime) | Depends on market/insurers; heavy integration | V3 as configurable module |
| OOS-06 | Hardware (receipt printers, barcode scanners, cash drawers, weighing scales) | Sold/recommended via partners; software interfaces only | Ongoing via device partners |
| OOS-07 | Offline-first POS (disconnected mode) | Adds major complexity; cloud-only with local resilience caching | V2 review |
| OOS-08 | Full clinical EHR / patient medical records | Not an EHR; pharmacy-scope only | Never |
| OOS-09 | Supplier self-service ordering portal | B2B marketplace is a separate roadmap item | V3+ / Marketplace |
| OOS-10 | Language packs beyond Arabic and English | Initial languages AR (RTL) + EN; plugin framework supports more packs | V2+ |
| OOS-11 | Custom per-tenant code or white-label core logic | Conflicts with multi-tenant SaaS economics; configuration over customization | Never (policy) |
| OOS-12 | Data residency across arbitrary geographies at MVP | Single/regional hosting initially (AS-06); residency options later | Enterprise |

---

# 9. Business Processes (BPMN 2.0)

Processes are described in BPMN-style: **Trigger → Actors → Flow → Business Rules → Outputs**. Detailed BPMN diagrams (swimlane pools) are delivered as an artefact with the SRS; the narrative below is the authoritative business-level definition.

**Process map (value chain):**

```
   ┌─────────────────────────────────────────────────────────────────────────────┐
   │ CORE OPERATIONS                                                              │
   │  P01 Sales & Dispensing (OTC)  P02 Prescription Fulfillment  P03 Returns     │
   │  P04 Purchasing & Procurement  P05 Goods Receipt & QC        P06 Supplier     │
   │     Returns & Claims                                                        │
   │  P07 Inventory (adjust/transfer/count)  P08 Expiry & Recall                 │
   │  P09 Cash Management & Day-Close  P10 Accounting Posting & Tax              │
   │  P17 Localization & Compliance Configuration                                │
   ├─────────────────────────────────────────────────────────────────────────────┤
   │ CHAIN / WAREHOUSE  P11 Inter-Branch Transfer  P12 Distribution Dispatch      │
   ├─────────────────────────────────────────────────────────────────────────────┤
   │ COMMERCIAL PLATFORM                                                          │
   │  P13 Tenant Onboarding & Subscription Lifecycle  P14 User/Role & Access     │
   │  P15 Reporting & Compliance  P16 Customer Credit & Loyalty                  │
   └─────────────────────────────────────────────────────────────────────────────┘
```

## P01 — Sales & Dispensing (Walk-in / OTC)
- **Trigger:** Customer presents item(s) at counter.
- **Actors:** Cashier; Pharmacist (for restricted items); Customer.
- **Flow:** Start sale → scan/select items → system validates stock availability, price, expiry, restricted-item flag → apply discounts (per policy) → select payment method(s) → tender & reconcile → print/email receipt → post sale to stock and sales ledger → update customer loyalty (if opted) → close.
- **Business rules:** BR-STK-02, BR-SAL-01, BR-SAL-02, BR-SAL-04, BR-PRC-01, BR-TAX-01, BR-CTL-01.
- **Outputs:** Sale transaction, receipt, stock decrement, sales journal, cash drawer record.

## P02 — Prescription Fulfillment (Rx)
- **Trigger:** Patient presents a prescription (paper or digital).
- **Actors:** Pharmacist-in-Charge; Pharmacy Assistant; Patient.
- **Flow:** Verify prescription validity (issuer, date, dosage, item, quantity) → create Rx record linked to patient profile (privacy-scoped) → check stock & expiry for each line → dispense/fulfill → record pharmacist verification & dispense signature → controlled substances flagged & logged with override workflow → update stock → record charges/payment → archive Rx (paper scan or digital reference) → schedule refill reminders (if applicable).
- **Business rules:** BR-RX-01 … BR-RX-06, BR-CTL-01 … BR-CTL-03, BR-STK-02, BR-PRIV-01.
- **Outputs:** Fulfilled Rx record, dispense log, controlled substance register entry, stock decrement, audit trail.

## P03 — Sales Returns & Refunds
- **Trigger:** Customer returns an item (defective, wrong item, change of mind).
- **Actors:** Cashier; Pharmacist (for medicines); Customer.
- **Flow:** Verify original sale → reason capture → stock re-admittance decision (restock vs quarantine vs destroy per condition and regulations) → compute refund per payment method and policy → approve (above threshold requires manager) → reverse stock & sales → issue credit/refund receipt → post to ledger.
- **Business rules:** BR-SAL-03, BR-SAL-05, BR-STK-02, BR-CTL-04, BR-ACC-01.
- **Outputs:** Return transaction, refund/credit record, stock adjustment, ledger reversal.

## P04 — Purchasing & Procurement
- **Trigger:** Reorder point reached, low-stock report, expiry-driven replenishment, or manual buy decision.
- **Actors:** Purchase/Inventory Manager; Owner; Supplier.
- **Flow:** Demand signals (sales velocity, seasonality, minimums) → generate purchase suggestion list → select supplier (terms, price, lead time) → create purchase order (PO) → approve per authorization limit → send to supplier (print/email/integration) → track PO status → receive against PO.
- **Business rules:** BR-PUR-01 … BR-PUR-06, BR-SUP-01, BR-SUP-04, BR-AUTH-01.
- **Outputs:** Purchase order, supplier commitment, cost commitments, receiving plan.

## P05 — Goods Receipt & Quality Check (GRN)
- **Trigger:** Supplier delivery arrives against an open PO.
- **Actors:** Store/Warehouse staff; Pharmacist (QC); Supplier delivery person.
- **Flow:** Match delivery note to PO → verify quantities, batches/lots, expiry dates, unit packs, pricing → quality/condition check (packaging, cold-chain note) → accept or reject (partial or full) → record batch/expiry onto stock → variance handling (shortage/overage/price change) → update stock value & supplier payable → route damaged/expired items to quarantine.
- **Business rules:** BR-STK-01, BR-STK-02, BR-STK-05, BR-PUR-02, BR-PUR-05, BR-SUP-02, BR-ACC-01.
- **Outputs:** Goods receipt note, batch-level stock, variance records, updated payables, supplier scorecard input.

## P06 — Supplier Returns & Claims (Credit Notes)
- **Trigger:** Expired, damaged, recalled, or wrongly supplied goods need returning to supplier.
- **Actors:** Purchase/Inventory Manager; Accounts; Supplier.
- **Flow:** Identify returnable stock (expiry watchlist, recall, damage) → create supplier return → capture reason and evidence → supplier authorization (if required) → dispatch goods → await supplier credit note → reconcile credit note to claim → post credit to payables → age and escalate uncollected claims.
- **Business rules:** BR-SUP-03, BR-SUP-05, BR-STK-02, BR-ACC-01.
- **Outputs:** Supplier return, credit note reconciliation, payables adjustment, claims aging report.

## P07 — Inventory Adjustments, Counts & Transfers
- **Trigger:** Cycle count scheduled, discrepancy found, damage, theft, transfer between branches.
- **Actors:** Store staff; Pharmacist; Chain manager.
- **Flow (adjust/count):** Lock stock area → count vs system → reconcile variances → document reason (damage/theft/error/regulatory) → manager approval above threshold → post adjustment → update stock value.
- **Flow (transfer):** Select source & destination branch → select items/batches → confirm availability → ship with manifest → receive at destination → match manifest → record inter-branch cost → update both branches.
- **Business rules:** BR-STK-03, BR-STK-06, BR-STK-07, BR-AUTH-01, BR-BRANCH-01.
- **Outputs:** Adjustment journal, count variance report, transfer manifest, branch stock updates.

## P08 — Expiry & Recall Management
- **Trigger:** Batch approaching expiry threshold, regulatory recall notice, or supplier recall.
- **Actors:** Pharmacist; Purchase Manager; Compliance Officer; Accounts.
- **Flow (expiry):** Batches tracked from GRN → expiry watchlist by threshold → quarantine list near-expiry → disposition decisions (promotion/return/destroy) → documented disposal with witness → ledger impact.
- **Flow (recall):** Receive recall notice → identify affected batches across branches → quarantine all affected stock → halt sales (system blocks) → notify customers (if traced) → execute returns/destruction → document → report to authority if required.
- **Business rules:** BR-STK-01, BR-STK-04, BR-CTL-02, BR-RECALL-01, BR-AUTH-01.
- **Outputs:** Expiry watchlist, quarantine records, disposal certificates, recall execution report, blocked-sale log.

## P09 — Cash Management & Day-Close
- **Trigger:** End of business day, shift end, or manager request.
- **Actors:** Cashier; Store Manager; Accounts.
- **Flow:** Collect expected sales per payment type → count physical cash → reconcile variance → resolve/approve variances → lock day → post sales to ledger → generate day summary → archive.
- **Business rules:** BR-CASH-01, BR-CASH-02, BR-ACC-01, BR-ACC-03, BR-AUTH-01.
- **Outputs:** Day-close report, cash variance log, sales journal, locked period records.

## P10 — Accounting Posting & Tax Processing
- **Trigger:** Day-close completes, PO/GRN posts, returns post, payments collected.
- **Actors:** Finance Officer; System (automation).
- **Flow:** Financial events → map to chart of accounts → compute tax per product/rate → post double-entry entries → validate balances → generate financial statements (P&L, balance sheet, cash flow) → export for external accounting/tax filing → archive with full audit trail.
- **Business rules:** BR-ACC-01 … BR-ACC-04, BR-TAX-01 … BR-TAX-03, BR-LOC-01/02.
- **Outputs:** Ledgers, financial statements, tax-return-ready exports, e-invoice submission (where the market pack requires it), audit trail.

## P11 — Inter-Branch Transfer (Chain)
- **Trigger:** Branch stockout/overstock, central reallocation decision.
- **Actors:** Regional Manager; Branch staff.
- **Flow:** Request transfer → approve (cost center, quantity) → source branch ships (batch-level manifest) → destination branch receives → variance handling → cost and margin allocation → consolidated stock updated.
- **Business rules:** BR-BRANCH-01, BR-BRANCH-02, BR-STK-06, BR-AUTH-01.
- **Outputs:** Transfer order, manifest, branch stock updates, allocation journal.

## P12 — Distribution Dispatch (Warehouse)
- **Trigger:** Customer (pharmacy) order or branch replenishment.
- **Actors:** Warehouse staff; Delivery; Accounts; Customer pharmacy.
- **Flow:** Pick list from confirmed orders → batch verification at pick → pack & dispatch with delivery note → delivery proof → invoice/credit terms applied → stock and receivables updated → returns handled via claims process.
- **Business rules:** BR-STK-02, BR-SUP-05, BR-ACC-01, BR-CUST-01.
- **Outputs:** Dispatch/delivery note, invoice, receivables posting, delivery confirmation.

## P13 — Tenant Onboarding & Subscription Lifecycle
- **Trigger:** New customer signs up; subscription change; non-payment.
- **Actors:** Customer Success; Sales; Finance; Tenant Admin; System.
- **Flow:** Signup (trial/paid) → tenant provisioning (isolated data space) → market-pack activation (P17) → business configuration (branches, users, products, tax, POS) → data import/migration → training → activation → recurring billing (invoice/payment/reminders) → plan change (upgrade/downgrade with feature enforcement) → suspension/reinstatement policy → churn/offboarding (data export).
- **Business rules:** BR-SUB-01 … BR-SUB-06, BR-TEN-01 … BR-TEN-03, BR-SEC-03.
- **Outputs:** Tenant record, subscription contract, configuration state, invoices, entitlement state, health score.

## P14 — User, Role & Access Management
- **Trigger:** Staff join/leave, role change, audit request.
- **Actors:** Tenant Admin; Pharmacy Owner; Compliance Officer; System.
- **Flow:** Create named user → assign role(s) → permissions per role/branch scope → configure authentication (password policy, 2FA, session) → grant/revoke on lifecycle events → record all access events → periodic access review → forensic audit on request.
- **Business rules:** BR-SEC-01 … BR-SEC-05, BR-AUD-01.
- **Outputs:** User registry, role catalog, access logs, audit trail, review reports.

## P15 — Reporting & Compliance
- **Trigger:** Daily, weekly, monthly; regulatory request; ad-hoc.
- **Actors:** Owner; Managers; Finance; Compliance Officer; Regulator (via export).
- **Flow:** Select report scope (tenant/branch/date) → generate from live posted data → apply filters → validate totals → export (PDF/Excel/CSV/tax format) → schedule/deliver → archive.
- **Business rules:** BR-REP-01, BR-TAX-02, BR-AUD-01.
- **Outputs:** Operational and financial reports, regulatory submissions, archives.

## P16 — Customer Credit & Loyalty
- **Trigger:** Credit customer purchase, loyalty redemption, credit limit event.
- **Actors:** Cashier; Accounts; Customer.
- **Flow (credit):** Verify credit customer identity → check credit limit & aging → approve/block sale → post to AR → payment allocation → statement.
- **Flow (loyalty):** Opt-in → earn points per policy → redeem with controls → report.
- **Business rules:** BR-CUST-01 … BR-CUST-03, BR-LOY-01.
- **Outputs:** AR aging, credit approval log, loyalty ledger, statements.

## P17 — Localization & Compliance Configuration
- **Trigger:** New market go-live, a market regulation change, or a tenant activating a market pack.
- **Actors:** Platform Configuration Admin; Tenant Admin; Compliance Officer; System.
- **Flow:** Select target market pack → validate regulatory mapping (tax, e-invoicing, currency, language, calendar, drug reference, Rx mode, health-authority reporting) → apply tenant defaults → run compliance readiness checks → enable pack features via flags → test in sandbox → activate (audited) → subscribe to regulation-change notifications → update pack under version control.
- **Business rules:** BR-LOC-01 … BR-LOC-04, BR-CUR-01/02, BR-TAX-03, BR-PLUG-01/02, BR-TEN-02/03.
- **Outputs:** Market pack version, tenant compliance configuration, readiness report, activation changelog.

---

# 10. Business Rules

Business rules are atomic, testable statements. Every rule has a unique ID and is a pass/fail validation. Rules are grouped by domain. *Configurable* rules have default values set at tenant level unless market config overrides (AS-01).

## 10.1 Stock & Inventory (BR-STK)
| ID | Rule (testable) |
|----|-----------------|
| BR-STK-01 | A product may only be received into sellable stock with a valid batch/lot number and a non-past expiry date, unless the product class explicitly allows no-batch handling. |
| BR-STK-02 | A sale, dispense, or dispatch line MUST NOT be finalized if the requested quantity exceeds available sellable stock for that batch or product. |
| BR-STK-03 | Every stock adjustment MUST record a reason code (damage, theft, count-variance, expiry, error, regulatory) and a user; adjustments above the configured value threshold MUST also carry manager approval. |
| BR-STK-04 | A batch within X days of expiry (configurable, default 90) is flagged on the expiry watchlist; within Y days (default 30) it is quarantined from sale unless explicitly overridden with documented justification by the Pharmacist-in-Charge. |
| BR-STK-05 | Partial goods receipt MUST record a variance reason and MAY create a backorder against the open PO line; over-receipt beyond the configured tolerance (default 2%) requires manager approval. |
| BR-STK-06 | An inter-branch transfer MUST be initiated at batch level and MUST be balanced (source decrease equals destination increase) before close, with variance handling for in-transit losses. |
| BR-STK-07 | Negative stock MUST NOT be created by normal transactions; only a manager-approved adjustment may correct a negative balance, with mandatory reason capture. |

## 10.2 Sales & POS (BR-SAL)
| ID | Rule |
|----|------|
| BR-SAL-01 | A sale cannot be finalized with zero sale lines or with a line that has no valid price. |
| BR-SAL-02 | Discounts apply per tenant policy: discount % above the tenant maximum (default 10%) or discount above absolute amount (default configured) requires manager override with reason. |
| BR-SAL-03 | A return/refund MUST reference the original sale transaction; refunds above the configured threshold (default) require manager approval and reason capture. |
| BR-SAL-04 | Voiding a sale or line requires reason capture and the original operator identity; voided transactions remain fully preserved in the audit trail. |
| BR-SAL-05 | Returned medicines are routed to restock or quarantine based on condition assessment; returned controlled substances MUST go to quarantine and follow disposition rules. |
| BR-SAL-06 | Restricted-category products (per config) require an authorized pharmacist approval event before the sale is finalized. |

## 10.3 Prescriptions (BR-RX)
| ID | Rule |
|----|------|
| BR-RX-01 | A prescription MUST record issuer, issue date, patient (or anonymized placeholder per privacy config), prescribed items, quantities, and directions before fulfillment. |
| BR-RX-02 | A prescription with an issue date older than the configured validity window (default 90 days) MUST NOT be fulfilled without Pharmacist-in-Charge approval and justification. |
| BR-RX-03 | Dispensed quantity MUST NOT exceed the prescribed quantity unless clinically justified and recorded by the Pharmacist-in-Charge. |
| BR-RX-04 | Each fulfilled prescription MUST carry the verifying pharmacist's identity and timestamp (dispense signature) in the audit trail. |
| BR-RX-05 | Refill/repeat count MUST NOT exceed the prescribed refills unless revalidated. |
| BR-RX-06 | Controlled/scheduled substances MUST additionally follow BR-CTL rules; the system MUST block fulfillment of a controlled Rx without a valid issuer reference and required documentation. |

## 10.4 Controlled Substances (BR-CTL)
| ID | Rule |
|----|------|
| BR-CTL-01 | Every controlled-substance transaction (receive, sell, transfer, adjust, destroy) MUST create an immutable register entry with user, timestamp, quantity, and batch. |
| BR-CTL-02 | Controlled substance stock MUST NOT be sold without documented purchaser/requisition reference where required by market configuration. |
| BR-CTL-03 | Controlled substance inventory MUST be reconcilable to the register at any time; physical count variance requires immediate documented review and, if above threshold, compliance notification. |
| BR-CTL-04 | Disposal/destruction of controlled substances MUST be witnessed and documented (witness identity + timestamp) before stock removal. |

## 10.5 Pricing (BR-PRC)
| ID | Rule |
|----|------|
| BR-PRC-01 | Every sale line price is derived from the active price list or approved manual price; manual price changes above threshold require approval and are logged. |
| BR-PRC-02 | Margin markup on purchase cost follows tenant or market rules; price lists can be per-branch with head-office override in chain tenancies. |
| BR-PRC-03 | A price cannot be negative; a sale price cannot be below configured minimum margin without manager approval (configurable off). |

## 10.6 Purchasing & Suppliers (BR-PUR / BR-SUP)
| ID | Rule |
|----|------|
| BR-PUR-01 | A purchase order MUST have an approved supplier, expected date, and line-level items with quantity and agreed price before it is issued. |
| BR-PUR-02 | Goods receipt against a PO records price and cost as per PO unless variance approval recorded (BR-STK-05). |
| BR-PUR-03 | Purchase order creation above the tenant authorization limit requires approval by a second authorized user. |
| BR-PUR-04 | Reorder suggestions are generated only for active products with a defined min/max or demand signal; suggestions MUST NOT auto-create POs without human confirmation. |
| BR-PUR-05 | A PO cannot be received more than the ordered quantity unless over-receipt approval recorded (BR-STK-05). |
| BR-SUP-01 | Only approved (onboarded) suppliers can receive purchase orders. |
| BR-SUP-02 | Supplier performance (fill rate, on-time, quality) is scored from goods receipt and returns events automatically. |
| BR-SUP-03 | Supplier returns MUST reference the original purchase/GRN and MUST generate a claim awaiting supplier credit note. |
| BR-SUP-04 | Supplier credit terms (payment days, credit limit) are enforced at PO creation; blocked suppliers require approval. |
| BR-SUP-05 | Uncollected supplier credit notes older than 90 days MUST appear on the claims aging report for action. |

## 10.7 Customers, Credit & Loyalty (BR-CUST / BR-LOY)
| ID | Rule |
|----|------|
| BR-CUST-01 | Credit sales are allowed only for credit-enabled customers with available credit limit and no overdue balance beyond the configured threshold. |
| BR-CUST-02 | Credit sale creation and payment allocation MUST be posted to AR with full audit trail. |
| BR-CUST-03 | Customer statements MUST reflect all invoices, payments, and credit notes within the statement period. |
| BR-LOY-01 | Loyalty points accrue per configured policy and can only be redeemed within policy limits; point transactions are auditable. |

## 10.8 Cash & Accounting (BR-CASH / BR-ACC / BR-TAX)
| ID | Rule |
|----|------|
| BR-CASH-01 | Day-close MUST reconcile expected sales per payment type against declared cash; variance resolution requires documented reason and (above threshold) manager approval. |
| BR-CASH-02 | A day can only be closed once; post-close corrections require a manager-authorized re-open with full audit trail. |
| BR-ACC-01 | Every financial event MUST post balanced double-entry entries; unbalanced posting is rejected by the system. |
| BR-ACC-02 | The general ledger MUST reconcile to sub-ledgers (sales, purchases, AR, AP, inventory) after each day-close. |
| BR-ACC-03 | Posted periods are locked after close; any change requires an audited reversing entry. |
| BR-ACC-04 | Inventory valuation (cost basis) is consistent per tenant policy (FIFO default) across all postings. |
| BR-TAX-01 | Each product carries a tax treatment; the system computes tax on every taxable line and reports per tax rate. |
| BR-TAX-02 | Tax reports/exports MUST reconcile to posted sales within a configurable tolerance (default 0.00, no rounding drift). |
| BR-TAX-03 | When the active market pack requires electronic invoicing (e.g., ZATCA Phase 2 in KSA), an invoice is considered issued only after validation and transmission per that pack's specification; transmission failure blocks invoice issue. |

## 10.9 Branch & Multi-Branch (BR-BRANCH)
| ID | Rule |
|----|------|
| BR-BRANCH-01 | Every transaction MUST belong to exactly one branch; consolidated reports roll up branches per hierarchy without duplication. |
| BR-BRANCH-02 | Head-office policy (pricing, discounts, product availability) can be pushed centrally; branch deviation requires override with reason and is visible in reports. |

## 10.10 Security, Privacy & Audit (BR-SEC / BR-PRIV / BR-AUD)
| ID | Rule |
|----|------|
| BR-SEC-01 | Every user MUST have a unique named account; shared logins are prohibited by configuration enforcement. |
| BR-SEC-02 | Access is granted via roles; each role defines module and action permissions and branch scope. |
| BR-SEC-03 | Privileged actions (price overrides, refunds above threshold, voids, adjustments, role changes) require approval or 2FA per policy. |
| BR-SEC-04 | Password policy, session timeout, and lockout thresholds are configurable per tenant and enforced centrally. |
| BR-PRIV-01 | Patient data is stored under the configured privacy regime; only role-authorized staff can view prescription-linked identity, and exports are consent-scoped. |
| BR-AUD-01 | All create/update/delete of financial, stock, prescription, controlled-substance, and permission data MUST be recorded immutably with user, timestamp, before/after values, and IP/device. |

## 10.11 Multi-Tenancy & Subscription (BR-TEN / BR-SUB)
| ID | Rule |
|----|------|
| BR-TEN-01 | Tenant data MUST be isolated at the data layer; cross-tenant access is prohibited and enforced by architecture plus access controls. |
| BR-TEN-02 | Tenant feature entitlements are enforced at runtime by the subscription plan; a feature not in plan is unavailable and flagged on upgrade path. |
| BR-TEN-03 | Tenant configuration changes (branches, users, roles, products, plans) are versioned and auditable. |
| BR-SUB-01 | Subscription plan determines licensed limits (users, branches, transactions, storage) which are enforced with clear warning at 80/90/100% usage. |
| BR-SUB-02 | Invoicing is generated on a committed schedule; late payment triggers reminder flow, then soft limit, then suspension per policy with data retained and accessible for export. |
| BR-SUB-03 | Plan upgrade is immediate and prorated; downgrade takes effect at next billing period with entitlement validation. |
| BR-SUB-04 | Trial tenants convert or are suspended; trial data is exportable at any time before and during grace period. |
| BR-SUB-05 | All subscription and billing changes are auditable and reflected in tenant invoice history. |
| BR-SUB-06 | Tenants on a suspended plan MUST retain full data access for export during the grace period; suspension never deletes tenant data without a documented, approved offboarding policy. |

## 10.12 Reporting (BR-REP)
| ID | Rule |
|----|------|
| BR-REP-01 | Operational reports MUST be generated from posted, reconciled data and MUST display the data currency timestamp. |
| BR-REP-02 | Cross-branch reports MUST balance to the sum of branch-level reports. |

## 10.13 Recall (BR-RECALL)
| ID | Rule |
|----|------|
| BR-RECALL-01 | On a recall, all affected batch/lot inventory across all branches is automatically quarantined and blocked from sale, with a system-wide report of affected quantities. |

## 10.14 Localization, Currency & Plugin Compliance (BR-LOC / BR-CUR / BR-PLUG)
| ID | Rule |
|----|------|
| BR-LOC-01 | The core MUST be country-neutral; market-specific behavior (tax, e-invoicing, currency, language, calendar, drug reference, Rx mode, health-authority reporting) MUST be delivered by an active market pack, not by core code. |
| BR-LOC-02 | A tenant MUST have at least one active market pack before live transactions; mixing market packs on one tenant requires explicit configuration approval. |
| BR-LOC-03 | Arabic (RTL) and English interfaces MUST render correctly, including mixed-script content (e.g., Latin drug names inside an Arabic UI). |
| BR-LOC-04 | Business dates are stored canonically; display MAY be Gregorian or Hijri per tenant preference without altering business logic. |
| BR-CUR-01 | Transactions are recorded in the tenant base currency; any multi-currency transaction captures the applied rate and is reported in base currency with full rate audit. |
| BR-CUR-02 | Reporting MUST be expressible in the tenant base currency and, where configured, a secondary currency (e.g., USD) under consistent revaluation rules. |
| BR-PLUG-01 | A market pack MUST NOT access another market pack's configuration or data; plugin isolation is enforced at runtime. |
| BR-PLUG-02 | Market pack updates MUST be versioned, validated in sandbox, and audited before activation; a pack change MUST NOT alter the core. |

---

# 11. Functional Requirements (High-Level)

High-level functional requirements per IEEE 29148 — each FR is measurable and testable. Detailed acceptance criteria live in the SRS. Requirements are grouped by domain with traceability to processes (P-nn) and rules (BR-nn).

## 11.1 Pharmacy Operations (FR-PH)
| ID | Requirement | Acceptance (measurable) | Trace |
|----|-------------|-------------------------|-------|
| FR-PH-01 | The system shall support configuring one or more branches per tenant, each with its own address, tax registration, and operating profile. | Branch create/edit within 2 min; all transactions attributable to a branch. | P13, BR-BRANCH-01 |
| FR-PH-02 | The system shall provide a day-close workflow that reconciles expected vs declared cash per payment type. | Variance report generated in <10 s; variance resolution recorded. | P09, BR-CASH-01/02 |
| FR-PH-03 | The system shall support shift/open-close of registers/drawers with operator attribution. | Register open/close events logged with timestamps. | P09 |
| FR-PH-04 | The system shall provide on-screen guidance for staff on common counter tasks with a maximum of 3 steps to scan-and-sell. | Task completion <10 s per transaction for trained staff. | P01 |
| FR-PH-05 | The system shall support offline resilience: brief connectivity loss shall not lose the active transaction. | Active sale survives 30 s connectivity drop and completes on reconnect. | P01, NFR-N-08 |

## 11.2 Inventory Management (FR-INV)
| ID | Requirement | Acceptance | Trace |
|----|-------------|------------|-------|
| FR-INV-01 | The system shall maintain a product master supporting drugs, non-drugs, and service items with classification, pack units, barcodes (multiple), tax treatment, and category. | Product create via form or import ≤5 min; duplicate barcode detection. | P04/P05, BR-PRC-01, BR-TAX-01 |
| FR-INV-02 | The system shall track stock at product-batch-location level including quantity, cost, expiry, and status (sellable/quarantined/committed). | Batch-level stock query <2 s at 100k lines. | P05, BR-STK-01/02 |
| FR-INV-03 | The system shall provide reorder suggestions based on demand signals and min/max. | Suggestions generated on demand; manual confirm required. | P04, BR-PUR-04 |
| FR-INV-04 | The system shall support cycle counting with scheduled counts and variance reconciliation. | Count batch completes with variance report; adjustments post via BR-STK-03. | P07 |
| FR-INV-05 | The system shall support stock adjustments and inter-branch transfers with reasons and approvals. | Transfer closes balanced; adjustments audited. | P07/P11 |
| FR-INV-06 | The system shall maintain an expiry watchlist with configurable thresholds and quarantine actions. | Watchlist updates daily; quarantined batches blocked from sale. | P08, BR-STK-04 |
| FR-INV-07 | The system shall support batch-level recall management (quarantine, block, report). | One action quarantines all affected batches; report <30 s. | P08, BR-RECALL-01 |

## 11.3 Sales & POS (FR-POS)
| ID | Requirement | Acceptance | Trace |
|----|-------------|------------|-------|
| FR-POS-01 | The system shall support barcode/fast-search checkout with cart, discounts, and line/order level actions. | Scan-to-cart <1 s; search <2 s. | P01 |
| FR-POS-02 | The system shall support cash, card, QR, and mixed payments with tender and change calculation. | Tender reconciliation exact; cash variance logic per policy. | P01 |
| FR-POS-03 | The system shall support receipts (print and/or email/QR) with tax details and legal footer per market. | Receipt generated in <3 s. | P01, BR-TAX-01 |
| FR-POS-04 | The system shall support returns/refunds with original transaction linkage, reason capture, and approval thresholds. | Return posts reversed entries; audit preserved. | P03, BR-SAL-03/05 |
| FR-POS-05 | The system shall support void and price override with approval and full audit. | Voids logged immutably; overrides flagged. | BR-SAL-04, BR-SEC-03 |
| FR-POS-06 | The system shall support restricted-product sale approval by an authorized pharmacist. | Restricted line blocked until approval event. | BR-SAL-06 |
| FR-POS-07 | The system shall support layaway/credit-sale for eligible customers per BR-CUST-01. | Credit block/approve enforced at checkout. | P16, BR-CUST-01 |

## 11.4 Purchasing & Suppliers (FR-PUR)
| ID | Requirement | Acceptance | Trace |
|----|-------------|------------|-------|
| FR-PUR-01 | The system shall support purchase orders with supplier, terms, lines, prices, expected dates, and approval workflow. | PO create ≤5 min; approval enforced by limit. | P04, BR-PUR-01/03 |
| FR-PUR-02 | The system shall support goods receipt (GRN) with batch/expiry capture, variance, and backorder handling. | GRN posts stock and payables; variance documented. | P05, BR-STK-05, BR-PUR-02 |
| FR-PUR-03 | The system shall support supplier returns and credit-note claims with aging and reconciliation. | Claim tracked to credit note; aging report current. | P06, BR-SUP-03/05 |
| FR-PUR-04 | The system shall track supplier performance scorecards (fill, on-time, quality). | Scores computed from events automatically. | BR-SUP-02 |
| FR-PUR-05 | The system shall maintain a supplier master with onboarding status, terms, and credit configuration. | Supplier lifecycle enforced per BR-SUP-01/04. | P04/P06 |

## 11.5 Customers (FR-CUST)
| ID | Requirement | Acceptance | Trace |
|----|-------------|------------|-------|
| FR-CUST-01 | The system shall maintain a customer master (walk-in profile, loyalty opt-in, credit profile) with privacy-scoped fields. | Customer lookup <2 s; consent recorded. | P16, BR-PRIV-01 |
| FR-CUST-02 | The system shall support credit customers with limits, aging, blocking, and statements. | Credit decision enforced at sale; statements current. | P16, BR-CUST-01..03 |
| FR-CUST-03 | The system shall support a loyalty program (earn/redeem/expire) per tenant policy. | Points ledger consistent; redemption rules enforced. | P16, BR-LOY-01 |

## 11.6 Prescription Management (FR-RX)
| ID | Requirement | Acceptance | Trace |
|----|-------------|------------|-------|
| FR-RX-01 | The system shall capture prescriptions with issuer, issue date, items, quantities, directions, and patient reference, including image/attachment capture. | Rx record complete before fulfillment; attachment ≤5 MB. | P02, BR-RX-01 |
| FR-RX-02 | The system shall enforce prescription validity, refill limits, and pharmacist verification. | Invalid/expired/over-quantity blocked or approved-with-justification. | P02, BR-RX-02..05 |
| FR-RX-03 | The system shall maintain a controlled-substance register (immutable) and dispense log. | Register reconciles to stock at any time. | P02, BR-CTL-01..03 |
| FR-RX-04 | The system shall archive fulfilled prescriptions (paper scan or digital reference) for the configured retention period. | Archive retrieval <10 s; retention enforced. | P02, BR-AUD-01 |
| FR-RX-05 | The system shall expose a configurable interface point for digital prescriptions (per market). | Adapter contract documented; stub implemented in MVP. | P02 |

## 11.7 Accounting (FR-ACC)
| ID | Requirement | Acceptance | Trace |
|----|-------------|------------|-------|
| FR-ACC-01 | The system shall post balanced double-entry entries for all financial events automatically. | Zero unbalanced posts; ledger-subledger reconciles after close. | P10, BR-ACC-01/02 |
| FR-ACC-02 | The system shall provide a chart of accounts, AR/AP, cash/bank ledgers, and inventory valuation (FIFO default). | Reports match sub-ledgers. | P10, BR-ACC-04 |
| FR-ACC-03 | The system shall compute tax per product/rate and produce tax-return-ready exports. | Export reconciles to posted sales to 0 drift. | P10, BR-TAX-01/02 |
| FR-ACC-04 | The system shall support period locking and audited reversals. | Locked periods reject unapproved changes. | P10, BR-ACC-03 |
| FR-ACC-05 | The system shall support market-specific tax engines and e-invoicing (e.g., ZATCA) via active market packs. | E-invoice validated/transmitted before issue per BR-TAX-03; rate engine from pack. | P10/P17, BR-TAX-03, BR-LOC-01 |

## 11.8 Reporting (FR-REP)
| ID | Requirement | Acceptance | Trace |
|----|-------------|------------|-------|
| FR-REP-01 | The system shall provide standard operational reports: sales, stock, expiry, low stock, purchases, supplier, cash, profit/margin, branch comparison. | Report generated <10 s for 90-day data at tenant scale. | P15, BR-REP-01 |
| FR-REP-02 | The system shall support consolidated multi-branch reporting. | Consolidated = sum of branches. | BR-REP-02 |
| FR-REP-03 | The system shall support report scheduling, delivery, and export (PDF/Excel/CSV). | Scheduled delivery on time; exports complete. | P15 |
| FR-REP-04 | The system shall support compliance report exports (audit, controlled register, tax, recall). | Exports complete and time-stamped. | P15, BR-AUD-01 |

## 11.9 Branch Management (FR-BR)
| ID | Requirement | Acceptance | Trace |
|----|-------------|------------|-------|
| FR-BR-01 | The system shall support a tenant branch hierarchy with central policy push (pricing, discounts, product availability, approval thresholds). | Policy push propagates to branches <60 s; deviations flagged. | P11/P13, BR-BRANCH-02 |
| FR-BR-02 | The system shall support inter-branch transfers with batch-level manifests and cost allocation. | Transfers balanced and audited. | P11, BR-STK-06 |
| FR-BR-03 | The system shall provide head-office dashboards across branches. | Live data within 1 min of transaction. | P15 |

## 11.10 User & Role Management (FR-USR)
| ID | Requirement | Acceptance | Trace |
|----|-------------|------------|-------|
| FR-USR-01 | The system shall provide RBAC with roles, permissions, and branch scope. | Role assignment effective immediately; least-privilege default. | P14, BR-SEC-01/02 |
| FR-USR-02 | The system shall enforce authentication policies (password, 2FA, session, lockout). | Policy enforced centrally; 2FA available for admin/privileged. | P14, BR-SEC-04 |
| FR-USR-03 | The system shall provide full audit logging of access and privileged actions with forensic export. | Every privileged event logged immutably; export <60 s. | P14, BR-AUD-01 |

## 11.11 Subscription Management (FR-SUB)
| ID | Requirement | Acceptance | Trace |
|----|-------------|------------|-------|
| FR-SUB-01 | The system shall manage subscription plans, entitlements, add-ons, and licensed limits. | Entitlement enforced at runtime; limits warn at 80/90/100%. | P13, BR-SUB-01 |
| FR-SUB-02 | The system shall generate invoices, process payments, send reminders, and enforce suspension/reinstatement. | Billing cycle accurate; suspension preserves data export. | P13, BR-SUB-02 |
| FR-SUB-03 | The system shall support plan change with proration and entitlement validation. | Upgrade immediate; downgrade next period. | P13, BR-SUB-03 |
| FR-SUB-04 | The system shall provide tenant self-service for subscription and billing history. | Self-service changes audited. | P13, BR-SUB-05 |

## 11.12 Multi-Tenant SaaS Management (FR-TEN)
| ID | Requirement | Acceptance | Trace |
|----|-------------|------------|-------|
| FR-TEN-01 | The system shall provide automated tenant provisioning with isolated data space and configuration defaults. | Tenant live in <15 min with wizard. | P13, BR-TEN-01 |
| FR-TEN-02 | The system shall support tenant-level configuration (tax, currency, units, language, policies) via configuration layer. | Config versioned and auditable. | P13, BR-TEN-03 |
| FR-TEN-03 | The system shall provide a tenant health dashboard (usage, errors, license, billing health). | Health score computed daily; alerts configured. | P13, BR-TEN-02 |
| FR-TEN-04 | The system shall support tenant data export on request and at offboarding. | Full export within 24 h of request; format documented. | P13, BR-SUB-06 |

## 11.13 AI Readiness (FR-AI)
| ID | Requirement | Acceptance | Trace |
|----|-------------|------------|-------|
| FR-AI-01 | The system shall persist all transaction and master data in a structured, analytics-ready model with no destructive updates (append/audit). | No data loss on update; history preserved. | All, BR-AUD-01 |
| FR-AI-02 | The system shall expose demand and price/margin history APIs suitable for forecasting and insight modules. | API contract documented by Phase 5. | FR-AI-01 |
| FR-AI-03 | The system shall support feature flags so AI capabilities can be rolled out per tenant/plan. | Flags configurable without release. | FR-TEN-02 |

## 11.14 Marketplace Readiness (FR-MKT)
| ID | Requirement | Acceptance | Trace |
|----|-------------|------------|-------|
| FR-MKT-01 | The system shall expose a documented partner API and sandbox environment for third-party add-ons and B2B ordering. | Sandbox self-service by Phase 6; contract versioned. | Roadmap Phase 6 |
| FR-MKT-02 | The system shall support a catalog of add-ons purchasable within subscription. | Add-on lifecycle via FR-SUB-01. | FR-SUB-01 |

## 11.15 Localization, Compliance Plugins & Multi-Currency (FR-LOC)
| ID | Requirement | Acceptance | Trace |
|----|-------------|------------|-------|
| FR-LOC-01 | The system shall provide a localization and compliance plugin framework where each market pack defines tax, e-invoicing, currency, language, calendar, drug reference, Rx mode, and health-authority reporting behavior. | Two market packs (GCC, Yemen) activate without core changes; pack activation audited. | P17, BR-LOC-01/02, BR-PLUG-01/02 |
| FR-LOC-02 | The system shall provide Arabic (RTL) and English interfaces with correct mixed-script rendering. | All core screens render correctly in both languages; Latin drug names display correctly inside Arabic UI. | BR-LOC-03 |
| FR-LOC-03 | The system shall support multi-currency transactions and reporting in the tenant base currency with an optional secondary currency. | Rate capture, revaluation, and rate audit per BR-CUR-01/02. | P10, BR-CUR-01/02 |
| FR-LOC-04 | The system shall support Gregorian and Hijri calendar display on canonical business dates. | Both calendars render; date-based rules use canonical dates. | BR-LOC-04 |
| FR-LOC-05 | The system shall integrate with market e-invoicing specifications when the active market pack requires it (e.g., ZATCA FATOORAH Phase 2). | E-invoice validated and transmitted before issue; failure blocks issue (BR-TAX-03). | P10/P17, BR-TAX-03 |
| FR-LOC-06 | The system shall map national drug registration codes and GS1/SFDA-aligned barcodes per active market pack. | National code captured and searchable; barcode scan resolves per pack. | P17, BR-LOC-01 |
| FR-LOC-07 | The system shall support market-specific controlled-substance registers and health-authority report adapters. | Register/report formats per pack; exports validated against pack spec. | P17, BR-LOC-01 |

---

# 12. Non-Functional Requirements (Business-Level)

Business-level NFRs per IEEE 29148. Technical elaboration (SLA internals, scaling budgets) belongs to the SRS/architecture, but the business commitments below are binding.

| ID | Category | Business Requirement | Target / Acceptance |
|----|----------|----------------------|---------------------|
| NFR-N-01 | Availability | The platform shall be available during pharmacy operating windows with no scheduled maintenance during high-traffic hours. | ≥99.5% monthly availability; maintenance windows ≤4 h/month outside 08:00–22:00 local. |
| NFR-N-02 | Performance | Core transactions (checkout, stock lookup, day-close) shall complete within acceptable operational time. | Checkout transaction <2 s; stock/branch queries <2 s at 100k stock lines; day-close <10 s. |
| NFR-N-03 | Concurrency | The platform shall serve peak concurrent terminal load per region. | ≥1,500 concurrent terminals/region with no degradation >10% at target scale. |
| NFR-N-04 | Scalability | Adding tenants or branches shall not require per-tenant engineering. | Horizontal scale supported; new tenant cost curve declining. |
| NFR-N-05 | Security | Tenant and patient data shall be protected per market data-privacy regime; access least-privilege by default. | Encryption in transit/at rest; RBAC enforced; penetration-tested before launch. |
| NFR-N-06 | Privacy | Patient-linked data shall be stored and handled under the configured privacy regime with consent records. | Privacy regime compliance per launch market (AS-02); consent captured for any marketing use. |
| NFR-N-07 | Auditability | All regulated, financial, and permission events shall be immutable and exportable. | 100% event capture; audit export <60 s for 90-day scope. |
| NFR-N-08 | Resilience | Brief network loss must not corrupt or lose active transactions. | Active transaction survives 30 s outage; no silent data loss. |
| NFR-N-09 | Usability | New staff shall reach productive checkout speed quickly. | New user productive in <30 min guided onboarding; zero-training checkout for trained staff. |
| NFR-N-10 | Interoperability | The platform shall integrate with device peripherals and (per market) external systems. | Printer/scan/cash-drawer/QR integration list; API contract documented. |
| NFR-N-11 | Multi-Language | The platform shall be localizable without code changes. | Arabic (RTL) and English supported from MVP; additional languages via packs. |
| NFR-N-12 | Backup & Recovery | Tenant data shall be protected and restorable. | Daily backups; RPO ≤24 h; RTO ≤4 h business time; restore tested quarterly. |
| NFR-N-13 | Support | Customer support SLAs shall be defined by plan tier. | Critical issue response: ≤4 business hours (standard), ≤1 hour (Enterprise). |
| NFR-N-14 | Data Retention | Records shall be retained per regulatory and tenant policy with export capability. | Retention configurable; controlled/Rx records per legal minimum; export on request. |
| NFR-N-15 | Portability | Tenants can export and migrate their data. | Full documented export ≤24 h; no data hostage model. |
| NFR-N-16 | Cost Efficiency | Platform costs shall scale economically with tenant growth to protect margins. | Gross margin per tenant ≥70% at target scale. |
| NFR-N-17 | Localization | Arabic (RTL) and English shall be fully supported; adding a language shall not require core changes. | Language added via pack without code change; RTL/bidi correct on all core screens. |
| NFR-N-18 | Multi-Currency | Multi-currency operations with consistent valuation and audit. | Rates audited; reports balance in base currency; secondary currency correct. |
| NFR-N-19 | Plugin Security | Market packs execute in isolation without cross-pack data access or privilege escalation. | Isolation tests pass; a compromised pack cannot access other packs/tenants. |

---

# 13. Business Risks

Risk register with likelihood (L) and impact (I) on a High/Medium/Low scale and mitigation. Reassessed quarterly.

| ID | Risk | Category | L | I | Mitigation |
|----|------|----------|---|---|------------|
| RK-01 | Regulatory non-compliance in launch market (tax, Rx, controlled substances, privacy) causing fines, suspension, or reputational damage. | Compliance | H | H | Design compliance configuration layer; engage legal/compliance adviser before launch; pilot with regulators where possible; audit-first architecture. |
| RK-02 | Wrong launch-market assumption delays localization or forces rework (AS-01). | Market | M | H | Decision gated in Open Decisions (Appendix B) before SRS; config layer limits rework. |
| RK-03 | Low adoption by pharmacy staff due to usability or speed. | Adoption | M | H | Co-design with pilot partners; <30 min onboarding; fast checkout; champion program; usage telemetry. |
| RK-04 | Data migration failure/loss from incumbent systems erodes trust at onboarding. | Operational | H | H | Structured migration toolkit, dry-run migration, validation reports, rollback plan, support during switch-over. |
| RK-05 | Churn after trial/early period because perceived value lags effort. | Commercial | M | H | Time-to-value dashboards; onboarding success criteria; NRR monitoring; expansion offers. |
| RK-06 | Multi-tenant complexity (isolation, upgrades, noisy tenants) increases cost and risk. | Technical | M | M | Isolation-by-design (BR-TEN-01); capacity and quota controls; per-tenant health monitoring. |
| RK-07 | Safety-critical data loss or integrity issue (expiry, controlled stock) triggers legal liability. | Safety | L | H | Immutable audit, reconciliation controls, batch/expiry enforcement, controlled register checks, tested backups. |
| RK-08 | Competitive pressure from incumbents and new entrants erodes pricing power. | Market | M | M | Differentiated safety/compliance automation; fast onboarding; strong chain consolidation; switch incentives. |
| RK-09 | Pricing model mispriced vs market willingness to pay. | Commercial | M | H | Structured pricing research with pilot partners; tier-based plans; usage-based add-ons. |
| RK-10 | Security breach of patient or financial data. | Security | L | H | Security-by-design, pen-testing, least-privilege, monitoring, incident plan, compliance with privacy law. |
| RK-11 | Scope creep (marketplace, AI, patient app) distracts MVP. | Delivery | M | H | MoSCoW discipline (Section 17); roadmap gates; change control on OOS list. |
| RK-12 | Payment/finance integration (gateways, tax authority) dependency delays launch. | Delivery | M | M | Start integration early; fallback manual export path; abstraction layer. |
| RK-13 | Key personnel dependency within delivery team. | Delivery | M | M | Documentation standards, cross-training, knowledge continuity plans. |
| RK-14 | Pilot partners have unrealistic expectations of MVP scope. | Stakeholder | M | M | Signed pilot agreement with scope, timeline, success criteria, and fair value exchange. |
| RK-15 | Intra-region regulatory variance across GCC states (health authorities, tax, e-invoicing, Rx law) increases localization effort and defect risk. | Compliance | H | M | Market packs per state; shared framework; legal validation per pack; phased market rollout. |
| RK-16 | ZATCA e-invoicing (KSA Phase 2) misimplementation blocks KSA go-live and creates penalty exposure. | Compliance | H | H | Dedicated e-invoicing workstream; sandbox validation with ZATCA; expert review; early start. |
| RK-17 | Yemeni Rial volatility and immature payment infrastructure affect pricing, billing, and revenue predictability. | Market | H | M | Invoice options in USD/SAR (config), secondary-currency reporting, local payment rails, phased Yemen launch. |
| RK-18 | Arabic RTL and mixed-script defects erode trust in a flagship market. | Product Quality | M | H | Arabic-first QA matrix, native-speaker UX review, bilingual test cases, pilot validation. |
| RK-19 | Market-pack defects or isolation bugs undermine the "one product, many markets" promise. | Technical | M | H | Isolation-by-design, pack sandboxing, versioned activation, pack regression suite. |

---

# 14. Business Constraints

| ID | Constraint | Type | Impact |
|----|-----------|------|--------|
| CN-01 | Multi-tenant SaaS economics prohibit per-tenant customization and custom code. | Business/Technical | Configuration-over-customization policy (OOS-11). |
| CN-02 | Regulatory requirements vary by market and must be configured, not hard-coded. | Regulatory | Compliance configuration layer required from MVP. |
| CN-03 | Pharmacy operating hours constrain maintenance windows. | Operational | NFR-N-01 maintenance policy. |
| CN-04 | MVP delivery horizon targets ~12 months to production go-live (AS-03). | Schedule | Scope discipline; MoSCoW musts are the MVP contract. |
| CN-05 | Hardware diversity at stores (printers, scanners, POS devices) requires device abstraction. | Technical | Peripheral abstraction layer; certified device list. |
| CN-06 | Data privacy laws may restrict cross-border data flows. | Legal | Hosting/residency decision per market (AS-06, Appendix B). |
| CN-07 | No legacy codebase or incumbent technical debt to carry. | Technical (opportunity) | Greenfield allows clean architecture; no migration burden internally. |
| CN-08 | Budget and team capacity are finite; roadmap must sequence value. | Commercial | Phase gating and KPI checkpoints per phase. |
| CN-09 | GCC VAT framework and KSA ZATCA e-invoicing impose mandatory tax reporting formats where those markets are served. | Regulatory | Pluggable tax/e-invoicing engine via market packs; ZATCA adapter scheduled for KSA go-live. |
| CN-10 | Market packs must not compromise multi-tenant isolation or the country-neutral core. | Technical | Plugin framework with strict isolation and audited activation governance (BR-PLUG). |

---

# 15. Business Assumptions

Explicit and validated by the Business Analysis. Any change requires impact assessment. Items marked ⚠️ are open decisions flagged in Appendix B.

| ID | Assumption | Status |
|----|-----------|--------|
| AS-01 | **First deployment markets are Yemen and the GCC** (KSA, UAE, Qatar, Kuwait, Bahrain, Oman); the core is country-neutral with plugin-based market packs. Languages: **Arabic (RTL) and English**. | Confirmed by sponsor (Aug 2026); sequencing per DEC-08/DEC-09 |
| AS-02 | The MVP compliance set is best-practice base (batch/expiry, controlled-substance registers, audit) **plus GCC-market requirements as configured**: pluggable VAT engine, and ZATCA e-invoicing where KSA is served. Legal validation per market pack at SRS. | Hold (legal validation pending) |
| AS-03 | Target MVP is **production-grade in ~12 months**, with a paid pilot co-design program of ≥10 pilot partner locations already available (confirmed). | Confirmed by sponsor |
| AS-04 | MVP customer segments are **independent pharmacies first, small chains second**; warehouses and hospital pharmacies follow in later phases. | Hold (validated with sales) |
| AS-05 | Subscription revenue is the core commercial model; add-ons and marketplace are later expansion revenue. | Hold |
| AS-06 | Initial hosting is single-region, **GCC-region preferred** for latency/residency; multi-region residency is an Enterprise-phase item. ⚠️ | Pending DEC-05 |
| AS-07 | Pharmacies have intermittent-but-adequate internet; brief outage resilience (NFR-N-08) is sufficient, no full offline mode in MVP. | Hold |
| AS-08 | Barcode and printed receipts are the default store reality; digital receipts are additive. | Hold |
| AS-09 | Suppliers are reachable by print/email order in MVP; supplier self-service portal is later. | Hold |
| AS-10 | Patients are privacy-scoped records; no patient-facing app or records beyond pharmacy-scope in MVP. | Hold |
| AS-11 | Existing customer data can be migrated via structured CSV/Excel imports plus manual validation; incumbent-system direct migration tooling is post-MVP. | Hold |
| AS-12 | The organization will staff required compliance/security advisory before launch market decision. | Hold |
| AS-13 | No third-party PMS/ERP data or pricing benchmarks were available to the BA at writing; KPIs are target-based, to be validated in pilot. | Hold |
| AS-14 | Arabic (RTL) and English are the initial languages; additional languages are delivered via plugin packs later. | Hold |
| AS-15 | Multi-currency (SAR, AED, QAR, KWD, BHD, OMR, YER, plus USD as secondary) is required from MVP; base currency is set per tenant. | Hold |
| AS-16 | Yemen launch faces operational constraints (currency volatility, payment rails, infrastructure) and is phased commercially after GCC anchor markets. | Hold (validate with sales) |
| AS-17 | KSA launch requires ZATCA-compliant e-invoicing; other GCC markets follow their national frameworks. | Hold (legal validation) |

---

# 16. Success Metrics (KPIs)

Metrics are categorized by audience. Baselines set in Year 1 pilot; targets reviewed quarterly.

## 16.1 Commercial KPIs
| KPI | Definition | Target |
|-----|-----------|--------|
| KPI-01 | Active paying tenants | ≥10 by Month 12 (pilot+paid); ≥100 Year 2; ≥500 Year 3 |
| KPI-02 | Active locations (branches) | ≥1,500 by end of Year 3 |
| KPI-03 | Monthly recurring revenue (MRR) / ARR growth | ≥15% QoQ in Years 1–2 |
| KPI-04 | Net revenue retention (NRR) | ≥110% from Year 2 |
| KPI-05 | Logo churn | <5% per year from Year 2 |
| KPI-06 | Gross margin per tenant | ≥70% at target scale |
| KPI-07 | Average revenue per tenant (ARPU) expansion via add-ons | ≥10% ARPU growth YoY |

## 16.2 Product & Operational KPIs
| KPI | Definition | Target |
|-----|-----------|--------|
| KPI-08 | Time-to-first-sale (new tenant from signup) | ≤5 business days |
| KPI-09 | Staff time-to-proficiency | ≤30 min guided onboarding |
| KPI-10 | Platform availability | ≥99.5% monthly |
| KPI-11 | Core transaction response | Checkout <2 s; queries <2 s |
| KPI-12 | Rule enforcement completeness | 100% of BR rules enforced in production code (BR compliance score) |
| KPI-13 | Audit event capture | 100% of mandated events logged |
| KPI-14 | Data reconciliation | Day-close and ledger-subledger reconcile with 0 unexplained variance |

## 16.3 Customer-Value KPIs (validated with pilot partners)
| KPI | Definition | Target |
|-----|-----------|--------|
| KPI-15 | Reduction in expiry write-offs after adoption | ≥15% within 6 months |
| KPI-16 | Reduction in stockouts | ≥15% within 6 months |
| KPI-17 | Sales under-reporting / cash shrinkage elimination | 100% of sales captured (day-close reconciliation) |
| KPI-18 | Customer satisfaction (CSAT) | ≥4.2/5 quarterly |
| KPI-19 | Support resolution within SLA | ≥95% within SLA by tier |

## 16.4 Readiness KPIs
| KPI | Definition | Target |
|-----|-----------|--------|
| KPI-20 | Compliance readiness per launch market | 100% of required controls mapped & tested pre-launch |
| KPI-21 | Data export capability | Full tenant export ≤24 h, tested quarterly |
| KPI-22 | Restore capability | RTO ≤4 h, tested quarterly |
| KPI-23 | Market-pack readiness per market | 100% of pack controls mapped, validated, and tested before that market's go-live |

---

# 17. Feature Prioritization (MoSCoW)

Prioritization applies to the **MVP contract** (Phase 1). Post-MVP features are phased in the Roadmap (Section 18).

## 17.1 Must Have (MVP non-negotiable)
- Product master + batch/expiry inventory (FR-INV-01, 02, 06)
- Stock adjustments, cycle counts, transfers (FR-INV-04, 05)
- Barcode POS with cash/card/QR/mixed payments (FR-POS-01, 02, 03)
- Returns, voids, price overrides with approval (FR-POS-04, 05)
- Restricted-product pharmacist approval (FR-POS-06)
- Purchasing: PO, GRN with variance/backorder, supplier returns & claims (FR-PUR-01, 02, 03)
- Supplier master + scorecards (FR-PUR-04, 05)
- Prescription capture, validation, controlled register (FR-RX-01, 02, 03, 04)
- Customer master + credit + loyalty (FR-CUST-01, 02, 03)
- Multi-branch hierarchy, policy push, inter-branch transfer, consolidated reporting (FR-BR-01, 02, 03)
- RBAC, 2FA-ready auth, immutable audit (FR-USR-01, 02, 03)
- Subscription lifecycle: plans, entitlements, invoicing, suspension (FR-SUB-01..04)
- Tenant provisioning + configuration + health (FR-TEN-01..04)
- Accounting core: double-entry posting, day-close, tax exports, period lock (FR-ACC-01..04)
- Operational reports (sales, stock, expiry, cash, profit) (FR-REP-01..04)
- Expiry watchlist & recall quarantine (FR-INV-06, 07)
- Resilience for active transactions (NFR-N-08)
- **Localization & compliance plugin framework with GCC and Yemen market packs (FR-LOC-01)**
- **Arabic (RTL) + English bilingual interface (FR-LOC-02)**
- **Multi-currency with base + secondary currency (FR-LOC-03, BR-CUR)**
- **Gregorian + Hijri calendar display (FR-LOC-04)**
- **National drug code + GS1/SFDA-aligned barcode mapping per market pack (FR-LOC-06)**
- **ZATCA e-invoicing adapter where KSA launch is confirmed (FR-LOC-05, FR-ACC-05)**

## 17.2 Should Have (high value, second wave within/right after MVP)
- Digital prescription adapter (interface point) (FR-RX-05)
- Report scheduling and delivery (FR-REP-03)
- Layaway/credit-sale at POS (FR-POS-07)
- Tenant health dashboard advanced alerts (FR-TEN-03)
- Multi-language packs config (NFR-N-11)
- Data import for products/customers (self-serve) (FR-TEN-04)
- Sales margin reporting by product (FR-REP-01 extension)

## 17.3 Could Have (differentiator, if capacity)
- Advanced return/quarantine workflows with disposition certificates
- Customer statements automation (FR-CUST-02)
- Gamified onboarding and in-product guidance
- Barcode-based inventory apps (handheld scanning)
- Promotions engine (multi-buy, percentage off) — beyond discount rules

## 17.4 Won't Have This Release (explicitly deferred)
- Offline POS mode (OOS-07)
- Supplier self-service portal (OOS-09)
- Patient app / online ordering / delivery (OOS-03)
- Full financial ERP modules — HR/payroll/assets (OOS-02)
- Insurance claims adjudication (OOS-05)
- AI products (Phase 5, design-ready only)
- Marketplace (Phase 6)

---

# 18. Product Roadmap

Phases are outcome-gated: a phase starts only when its KPIs and acceptance conditions are met. Timeline is indicative.

```
Phase 1   Phase 2    Phase 3    Phase 4     Phase 5    Phase 6
MVP ────► V2 ──────► V3 ──────► Enterprise ─► AI ─────► Marketplace
M0–12     M9–18      M18–30     M30–42      M36–48     M42–54
```

## Phase 1 — MVP (Months 0–12)
- **Goal:** Production-grade core for independent pharmacies and small chains; pilot partners co-design.
- **Deliverables:** All MVP "Must Have" features (Section 17.1); **localization & compliance plugin framework with GCC and Yemen market packs**; **Arabic (RTL) and English interfaces**; **multi-currency engine**; **GS1/national drug-code mapping**; **ZATCA e-invoicing adapter for KSA launch**; tenant onboarding wizard; data import; subscription billing; day-close and tax exports; structured analytics-ready data model.
- **Gate-out KPIs:** 10+ pilot locations live; 0 critical defects; rule enforcement 100%; day-close reconcile 0 variance; CSAT ≥4.2 on pilot; 99.5% availability during pilot; market-pack readiness 100% per served market (KPI-23).
- **Decision required at M3:** confirm go-live sequencing and primary GCC launch market(s) (DEC-08/DEC-09) to finalize market-pack priorities and the ZATCA workstream.

## Phase 2 — V2 (Months 9–18)
- **Goal:** Win chain segment and warehouse distribution.
- **Deliverables:** Distribution/dispatch module (P12); credit management maturity (statements, aging, collections); offline resilience review; handheld barcode inventory; enhanced chain dashboards; supplier self-service beta; report scheduling; multi-language packs; layaway & promotions engine.
- **Gate-out KPIs:** Chains ≥15% of tenants; warehouse pilot live; NRR ≥105%.

## Phase 3 — V3 (Months 18–30)
- **Goal:** Full back-office financial depth and integrations.
- **Deliverables:** Deep accounting (fixed assets-light, AR/AP maturity, multi-ledger), financial statement pack; integrations (accounting packages, payment gateways breadth, tax authority per market); insurance/TPA claims module (configurable per market); open API formalization.
- **Gate-out KPIs:** Finance module adoption ≥60% of tenants; integration coverage ≥3 major external systems.

## Phase 4 — Enterprise (Months 30–42)
- **Goal:** Large chains and multi-region corporate customers.
- **Deliverables:** Head-office suite (budgets, margin control, procurement negotiation tools, consolidated treasury view); SLA-backed contracts; multi-region hosting/residency; dedicated support tiers; custom integration program; audit/compliance packs for enterprise procurement.
- **Gate-out KPIs:** ≥2 enterprise (50+ location) customers; enterprise NRR ≥115%; margin per enterprise tenant ≥75%.

## Phase 5 — AI (Months 36–48, overlaps Enterprise)
- **Goal:** Intelligence on top of transaction data (product built on FR-AI foundations).
- **Deliverables:** Demand forecasting and automated purchase suggestions with confidence; expiry-write-off prediction; anomaly detection (cash/stock variance); profit and supplier-term optimization recommendations; natural-language dashboards; per-tenant feature-flagged rollout.
- **Gate-out KPIs:** ≥30% of tenants use ≥1 AI feature monthly; measured ≥10% improvement in stock availability or margin vs baseline.

## Phase 6 — Marketplace & Ecosystem (Months 42–54)
- **Goal:** Ecosystem revenue.
- **Deliverables:** Add-on marketplace (payroll, e-prescription, loyalty marketing, analytics); B2B ordering hub (pharmacies order from suppliers in-platform); partner API + sandbox; revenue share model.
- **Gate-out KPIs:** Marketplace + AI ARR ≥10% of total; ≥3 external apps live.

---

# 19. Business Opportunities

| ID | Opportunity | Value | Dependencies | Horizon |
|----|-------------|-------|--------------|---------|
| OP-01 | Sell "compliance as a feature": automatic rule enforcement reduces pharmacy risk — premium pricing lever vs incumbents. | High (differentiation, higher willingness to pay) | BR rule engine, compliance config layer | MVP |
| OP-02 | Chain consolidation economics: one tenant, many branches with central control — strong B2B ACV, high retention (switching cost). | High | Branch module, policy push | V2 |
| OP-03 | Warehouse/B2B distribution module extends TAM into supply side of pharmacy value chain. | Medium-High | P12, credit maturity | V2 |
| OP-04 | Data-driven insights (expiry, demand, supplier performance) become sellable AI add-ons. | High (expansion revenue) | Analytics-ready model, AI phase | Phase 5 |
| OP-05 | B2B marketplace/ordering hub monetizes order flow and supplier participation. | High (ecosystem) | Supplier base critical mass, API/sandbox | Phase 6 |
| OP-06 | Digital prescription adapter creates stickiness and positions platform for national e-Rx programs. | Medium | Market decision (AS-01), adapter | V2+ |
| OP-07 | Partner hardware/device certification program (printers, scanners, tablets) generates referral revenue and reduces support load. | Medium | Device abstraction | MVP+ |
| OP-08 | Geographic expansion into adjacent markets via the config layer with low marginal engineering. | High (TAM) | Config layer, residency options | Phase 4+ |
| OP-09 | Customer success-led upsell (promotions, loyalty, reporting tiers) raises ARPU without new acquisition cost. | Medium-High | Product telemetry, NRR discipline | Ongoing |
| OP-10 | Franchise/group buying programs for independents (aggregate purchasing) — future B2B opportunity. | Medium | Data + supplier relationships | Phase 6 |
| OP-11 | Cross-GCC expansion at low marginal engineering via the plugin framework (one core, six market packs). | High | Plugin framework, legal validation per market | Phase 4+ |
| OP-12 | Yemen as a volume market with affordability positioning and Arabic-first experience. | Medium | Payment rails, currency handling, thin margins | V2+ |

---

# 20. Strategic Recommendations

| ID | Recommendation | Rationale | Owner | Priority |
|----|----------------|-----------|-------|----------|
| ST-01 | **Lock GCC + Yemen as the first deployment markets and sequence go-live** (DEC-08/DEC-09); resolve KSA ZATCA timing early. | AS-01 is now confirmed; sequencing avoids build-then-rework. | Executive Sponsor + PM | Immediate |
| ST-02 | **Run a structured paid pilot program** (≥10 locations) as a co-design engine, with signed scope and measurable success criteria. | Confirmed pilot partners exist; de-risks adoption, usability, and migration. | PM + Customer Success | M3 |
| ST-03 | **Build the compliance configuration layer first**, not last. | Regulatory variance is the single biggest cost if retrofitted. | Architecture | MVP start |
| ST-04 | **Commit to configuration-over-customization** as a product policy. | Protects multi-tenant economics; avoids OOS-11 erosion. | PM | Ongoing |
| ST-05 | **Design for auditability and immutability from day one.** | Reduces cost of compliance, recalls, and disputes; foundation for AI (FR-AI-01). | Architecture | MVP start |
| ST-06 | **Make onboarding and data migration a first-class product feature**, not a services afterthought. | Migration risk (RK-04) is a top adoption blocker. | Customer Success + Product | MVP |
| ST-07 | **Sequence chain features (V2) before warehouse (V2) but design warehouse data model in MVP.** | Chain expands from MVP base cheaply; warehouse needs credit/dispatch maturity. | PM | Roadmap |
| ST-08 | **Price for value on compliance safety, not just feature parity.** | Supports margin target (KPI-06) and differentiation (OP-01). | Sales + Finance | MVP launch |
| ST-09 | **Instrument usage telemetry from MVP** to drive retention and AI features later. | Feeds NRR (KPI-04) and AI readiness (FR-AI-01). | Product | MVP |
| ST-10 | **Establish a quarterly risk review** of this document's register. | Keeps risks (Section 13) current as market decisions land. | BA + PM | Ongoing |
| ST-11 | **Lock the MVP MoSCoW contract** and route all new asks through change control. | Prevents scope creep (RK-11). | PM | M3 |
| ST-12 | **Validate KPI baselines with pilot partners** before committing commercial targets. | AS-13 acknowledges baseline data not yet available. | BA + Customer Success | Pilot |
| ST-13 | **Treat Arabic (RTL) as a first-class experience**, validated by native speakers — not a translation afterthought. | Arabic quality is a key differentiator and trust factor in GCC/Yemen (RK-18). | Product + QA | MVP |
| ST-14 | **Start the ZATCA e-invoicing workstream early** with an external tax expert if KSA is in the first wave. | Misimplementation blocks KSA go-live and creates penalty exposure (RK-16). | PM + Compliance | M3 |
| ST-15 | **Validate the Yemen market model commercially** (currency, payment rails, pricing) before heavy investment; anchor commercial growth in the GCC. | Preserves margin targets amid currency/payment risk (RK-17, AS-16). | Sales + Finance | M6 |

---

# 21. Final Business Summary

PharmaCloud ERP is a commercially viable, production-ready SaaS platform concept for the pharmacy market. The business case rests on three defensible pillars:

1. **Safety and compliance automation** that incumbents treat as an afterthought — expiry, batch traceability, controlled substances, prescription validity, and tax are enforced by the system, converting regulatory burden into a selling point.
2. **Multi-branch control for chains and distribution for warehouses** on the same tenant architecture — enabling a land (independent) / expand (chain) / extend (warehouse, AI, marketplace) growth motion.
3. **A country-neutral core with plugin-based market packs** — serving Yemen and the GCC (Arabic/English, VAT and ZATCA e-invoicing, national drug codes) from one codebase, containing regulatory risk and preserving expansion optionality.

The MVP is deliberately scoped to a production-grade core (independent pharmacies + small chains, 12 months) with paid pilot partners co-designing it. Later phases add distribution, deep accounting, enterprise head-office features, AI intelligence, and a B2B marketplace — each phase gated by measurable KPIs.

**The package is ready for the SRS phase** — the launch market (Yemen + GCC, Arabic/English) is now confirmed; remaining open items are go-live sequencing and compliance-pack validation (DEC-08…DEC-10), which are resolved in parallel with SRS elaboration and do not block starting it. Business rules are atomic and testable (Section 10); requirements are measurable and traceable (Section 11); risks, constraints, and assumptions are explicit (Sections 13–15).

---

# 22. Validation Checklist

| # | Check | Status |
|---|-------|--------|
| V-01 | No stakeholder is missing (buyer, user, operator, regulatory, financial, technical, commercial, ecosystem, indirect beneficiary). | ✔ Covered (STK-01…22) |
| V-02 | All core business processes are documented. | ✔ 17 processes, all required domains (Section 9) |
| V-03 | Requirements are measurable. | ✔ Each FR has acceptance target; KPIs quantified (Section 16) |
| V-04 | Scope is clearly defined (in/out). | ✔ Sections 7–8 with explicit OOS list |
| V-05 | Risks are identified. | ✔ 19 risks with likelihood/impact/mitigation (Section 13) |
| V-06 | Assumptions are explicit. | ✔ 17 assumptions, flagged open items (Section 15) |
| V-07 | Business rules are testable. | ✔ 70+ atomic pass/fail rules with IDs (Section 10) |
| V-08 | Document supports multi-tenant SaaS expansion. | ✔ Tenant/subscription rules, FR-TEN/SB, roadmap Phases 4–6 |
| V-09 | Document ready for SRS phase without major revision. | ✔ Open Decisions isolated in Appendix B; requirements mapped to SRS |
| V-10 | Alignment with BABOK v3 / BPMN 2.0 / IEEE 29148 / ISO 9001 documentation principles. | ✔ Applied throughout |
| V-11 | Localization and market compliance (GCC + Yemen; Arabic RTL + English; pluggable tax/e-invoicing; multi-currency) addressed explicitly. | ✔ Sections 7.3/7.4; BR-LOC/CUR/PLUG; FR-LOC; NFR-N-17..19; RK-15..19 |

---

# 23. Appendix A — Traceability Matrix (Excerpt)

Full matrix delivered as a spreadsheet artefact with the SRS. Excerpt for the sales domain demonstrates the pattern (Requirement → Process → Rules).

| Requirement | Process | Business Rules | KPI |
|-------------|---------|----------------|-----|
| FR-POS-01/02/03 | P01 | BR-SAL-01, BR-PRC-01, BR-TAX-01 | KPI-11 |
| FR-POS-04 | P03 | BR-SAL-03, BR-SAL-05, BR-ACC-01 | KPI-14 |
| FR-POS-05 | P01 | BR-SAL-04, BR-SEC-03 | KPI-13 |
| FR-POS-06 | P01 | BR-SAL-06 | KPI-12 |
| FR-INV-02 | P05 | BR-STK-01/02 | KPI-11 |
| FR-INV-06/07 | P08 | BR-STK-04, BR-RECALL-01 | KPI-15 |
| FR-RX-01..04 | P02 | BR-RX-01..06, BR-CTL-01..03 | KPI-13 |
| FR-ACC-01..04 | P10 | BR-ACC-01..04, BR-TAX-01/02 | KPI-14 |
| FR-SUB-01..04 | P13 | BR-SUB-01..06 | KPI-04/05 |
| FR-TEN-01..04 | P13 | BR-TEN-01..03 | KPI-01 |
| FR-LOC-01..04 | P17 | BR-LOC-01..04, BR-CUR-01/02 | KPI-23 |
| FR-LOC-05 | P10/P17 | BR-TAX-03 | KPI-23 |
| FR-LOC-06/07 | P17 | BR-LOC-01 | KPI-23 |

---

# 24. Appendix B — Open Decisions Log

Items that require sponsor/PM decision and materially affect downstream artefacts. None block SRS kickoff, but each has a resolution deadline.

| ID | Decision | Options | Deadline | Impact if unresolved |
|----|----------|---------|----------|----------------------|
| DEC-01 | **Launch market / jurisdiction** (drives tax regime, Rx law, controlled-substance schema, language, hosting residency). | **RESOLVED (2026-08-05):** first deployment GCC + Yemen; global-neutral core with plugin market packs; languages Arabic (RTL) + English | Resolved | — |
| DEC-02 | **Compliance set mandatory at launch** (beyond best-practice base). | Best-practice base + GCC-market set (VAT engine; ZATCA e-invoicing where KSA served) | M3 | NFR-N-05/06 and certification roadmap cannot be locked |
| DEC-03 | **MVP segment prioritization** (independent-first vs chains-first resourcing split). | Independent-first (recommended) vs parallel | M3 | Sales resourcing, onboarding toolkit, chain features scope |
| DEC-04 | **Pricing/tier structure** and pilot partner commercial terms. | To be defined with sales + pilot partners | M6 | KPI-03/06/07 baselines; subscription module parameters |
| DEC-05 | **Hosting region / data residency** at MVP. | GCC single-region (recommended) vs multi-region | M6 | NFR-N-14/15, CN-06, latency, cost model |
| DEC-06 | **Payment gateway(s)** for tenant subscription billing. | To be selected | M6 | FR-SUB-02, RK-12 |
| DEC-07 | **Accounting package integration targets** for V3 (if any). | QuickBooks/Xero/regional/TBD | M18 | FR-ACC integration roadmap |
| DEC-08 | **Go-live sequencing across GCC + Yemen** (which market first). | GCC anchor first (KSA/UAE), Yemen phased (recommended) vs parallel | M3 | Market-pack priorities, sales resourcing, ZATCA timing, Yemen commercial model |
| DEC-09 | **Primary GCC launch market(s) for MVP wave 1.** | KSA, UAE, or both (recommended KSA + UAE) | M3 | ZATCA adapter, digital-Rx adapter, SFDA/MOHAP reference-data priority |
| DEC-10 | **Yemen commercial model** (currency/billing, payment rails, pricing, pilot). | USD/SAR invoicing with YER local records (recommended) vs YER-only | M6 | Billing, currency handling, revenue predictability (RK-17) |

---

*End of Business Analysis Package — PharmaCloud ERP v1.1.*
