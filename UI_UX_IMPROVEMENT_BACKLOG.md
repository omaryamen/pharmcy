# PharmaCloud ERP — UI / UX Improvement Backlog

| ID | Priority | Category | Module | Screen / Component | Problem Observed | Recommended Solution |
|---|---|---|---|---|---|---|
| **UX-01** | P1 | UX | POS | `/pos` | Cash register opening/closing float dialog is missing before initiating sales session. | Add a cashier session opening/closing modal with starting cash float tracking. |
| **UX-02** | P1 | UX | Prescriptions | `/prescriptions` | Rejection reason modal is missing when clicking "Reject Prescription". | Provide a mandatory clinical rejection reason prompt (e.g. incorrect dosage, expired Rx, doctor contact needed). |
| **UI-01** | P2 | UI | Inventory | `/inventory` | Dense table on mobile viewport (390px) causes horizontal scrolling without a sticky first column. | Implement card view fallback or sticky medicine name column for narrow mobile screens. |
| **UI-02** | P2 | UI | Dashboard | `/dashboard` | Quick KPI trend badges can benefit from mini sparkline preview charts. | Add lightweight SVG sparkline visualizations under revenue and inventory KPI cards. |
| **RTL-01** | P2 | RTL | AppShell | `Header Search` | Search keyboard shortcut indicator `(Ctrl+K)` flips awkwardly in Arabic mode. | Enclose keyboard shortcut tokens in directional isolate `<bdi>` or `dir="ltr"` wrappers. |
| **SEC-01** | P1 | SECURITY | Settings | `/settings` | Destructive tenant actions lack two-step confirmation text verification. | Require typing tenant code or confirmation text before performing critical configuration changes. |
| **UX-03** | P2 | UX | Accounting | `/accounting` | Chart of accounts tree navigation is represented as flat table rather than expandable hierarchy. | Add expandable parent-child node tree view for Asset / Liability / Equity / Revenue / Expense accounts. |
