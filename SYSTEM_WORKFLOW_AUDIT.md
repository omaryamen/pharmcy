# PharmaCloud ERP — System Workflow Audit (تدقيق مسارات العمل التشغيلية)

## 1. Core End-to-End Enterprise Workflows

```
1. Procurement Pipeline:
   [ Purchase Request (PR) ] ➔ [ Purchase Order (PO) ] ➔ [ Goods Receipt (GRN) ] ➔ [ AP Invoice Matching ] ➔ [ GL Ledger Posting ]

2. Fast Counter Sales:
   [ Barcode Scan (POS) ] ➔ [ FEFO Batch Auto-Select ] ➔ [ Payment (Cash/Card) ] ➔ [ Stock Movement ] ➔ [ Tax Invoice & ZATCA QR ]

3. Clinical Prescriptions:
   [ Prescription Upload ] ➔ [ Clinical Verification Queue ] ➔ [ Controlled Narcotics Sign-off ] ➔ [ Dispensing ] ➔ [ Audit Log ]

4. Multi-Branch Inventory Rebalance:
   [ Branch Requisition ] ➔ [ Central Warehouse Pick & Pack ] ➔ [ Transit Dispatch ] ➔ [ Branch Receipt Acknowledgment ]

5. Financial Reconciliation:
   [ Daily POS Close ] ➔ [ Cash Drawer Float Count ] ➔ [ Bank Statement Matching ] ➔ [ Automated Journal Posting ]
```

---

## 2. Workflow Verification Checklist
-  **Procurement Integrity**: 3-Way Match validation strictly prevents accounts payable payment prior to physical GRN receiving.
-  **Clinical Safety**: Controlled substances (Narcotics) trigger dual pharmacist verification and require licensed medical doctor credentials.
-  **Inventory FEFO Compliance**: Every item sale and stock transfer automatically depletes batches with the earliest expiry date.
-  **Financial Double-Entry**: All transactions automatically post debit and credit legs to the general ledger.
