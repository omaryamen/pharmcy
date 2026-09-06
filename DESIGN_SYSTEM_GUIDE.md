# PharmaCloud ERP — Global Design System Guide (دليل نظام التصميم الموحد)

## 1. Typography & Hierarchy
- **Arabic Font**: `Cairo` (Google Fonts), optimized for legible Arabic numerals and pharmaceutical terminology.
- **English & Code Font**: `Inter` and `JetBrains Mono` for tabular figures and financial amounts.

## 2. Color Palette & Functional Tokens
- **Primary / Brand**: HSL `217 91% 55%` (Clinical Blue)
- **Success / Validated**: Emerald Green (`bg-emerald-600`) for approved prescriptions and balanced drawers.
- **Warning / Action Needed**: Amber / Warm Yellow (`bg-amber-600`) for near-expiry batches and review queues.
- **Destructive / High Alert**: Crimson Red (`bg-destructive`) for expired batches and narcotics warnings.
- **Dark Mode**: Deep Slate `hsl(224 45% 8%)` with high-contrast borders (`hsl(224 35% 18%)`).

## 3. Standard UI Component Library
- `Button`: Primary, Secondary, Outline, Ghost, Destructive (`components/ui/button.tsx`).
- `Card`: Standard padding with border and subtle hover feedback (`components/ui/card.tsx`).
- `Badge`: Status badges with color-coded semantic variants (`components/ui/badge.tsx`).
- `EmptyState`: Standardized empty queue and no-search-result layouts (`components/ui/empty-state.tsx`).
- `ConfirmationDialog`: Accessible modal preventing accidental destructive actions (`components/ui/confirmation-dialog.tsx`).
- `Breadcrumbs`: Path navigation (`components/ui/breadcrumbs.tsx`).
- `Skeleton`: Shimmer pulse loader (`components/ui/skeleton.tsx`).
