# PharmaCloud ERP — Role Workspace Operational Guide (دليل بيئات العمل التشغيلية)

## 1. Workstation Operational Ergonomics

### A. Pharmacist Clinical Workstation (`/pharmacy`)
- **Prescription Review Queue**: Real-time triage of incoming doctor prescriptions.
- **Controlled Substances Enforcement**: Dual pharmacist digital sign-off and patient ID verification for narcotics.
- **FEFO Dispatch**: Strict automated prioritization of batches with closest expiration date.

### B. High-Speed Cashier POS Workstation (`/pos`)
- **Keyboard Shortcuts**: `F2` (Search/Barcode), `F4` (Cash Checkout), `F8` (Card Checkout), `ESC` (Cancel Cart).
- **Register Sessions**: Mandatory starting float entry upon opening shift; end-of-day discrepancy reporting.
- **Barcode Workflow**: Supports GS1 DataMatrix (2D) and standard EAN-13 barcodes with batch decoding.

### C. Inventory & Warehouse Engine (`/inventory`)
- **Double-Entry Ledger**: Every stock movement is backed by debit and credit location transactions.
- **Receiving (GRN)**: Quality inspection, temperature verification, batch numbering, and expiry registration.
- **Inter-Branch Transfers**: Requisition, dispatch, transit, and receipt acknowledgment.

### D. General Ledger & Accounting (`/accounting`)
- **Automated Double-Entry**: POS sales, purchases, and payments post automatically to appropriate ledger accounts.
- **Chart of Accounts**: Standardized 4-level account structure (1000 Assets, 2000 Liabilities, 3000 Equity, 4000 Revenue, 5000 Expenses).
