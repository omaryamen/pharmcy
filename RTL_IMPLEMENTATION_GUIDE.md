# PharmaCloud ERP — RTL Layout & Bidirectional Implementation Guide

## 1. Directional CSS & Logical Layout Principles
- **Logical Tailwind Utilities**:
  - `start-*` and `end-*` for directional offsets.
  - `ms-*` (margin-inline-start) and `me-*` (margin-inline-end) for spacing.
  - `ps-*` (padding-inline-start) and `pe-*` (padding-inline-end) for padding.
  - `rtl:text-right` and `rtl:text-left` for explicit table alignments.
- **Form Controls**: Input fields, search bars, and selects maintain proper padding for icons using `rtl:left-auto rtl:right-3` and `rtl:pl-3 rtl:pr-9`.
- **Numbers & SKU/Barcode Codes**: Retain standard LTR numeral order (`font-mono` direction neutral) while embedded in Arabic sentence flow.
