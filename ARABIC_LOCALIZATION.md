# PharmaCloud ERP — Arabic-First Localization & Internationalization Architecture

## 1. Executive Architecture Summary
PharmaCloud ERP is engineered with an **Arabic-First Architecture**, positioning Arabic (Modern Standard Arabic - العربية الفصحى المؤسسية) as the default operational language for enterprise pharmacy chains in the Middle East, while maintaining full English (LTR) bidirectional compatibility.

---

## 2. Localization Components
- **Centralized Dictionary Engine**: `frontend/lib/translations/ar.ts` (Arabic) and `frontend/lib/translations/en.ts` (English).
- **React Context Provider**: `frontend/lib/i18n.tsx` managing `locale` (`"ar"` | `"en"`), `direction` (`"rtl"` | `"ltr"`), and reactive string lookup `t(key)`.
- **Dynamic DOM Layout**: Automatically applies `dir="rtl"` / `dir="ltr"` and `lang="ar"` / `lang="en"` with localStorage persistence (`pharmacloud_locale`).
- **Typography & Font Rendering**: High-legibility Arabic typography stack integrated with Tailwind CSS.

---

## 3. Directional Iconography Rules
- **Mirrored**: Navigation chevrons, pagination arrows, back/forward buttons, breadcrumb separators.
- **Unmirrored**: Barcode symbols, medical Rx glyphs, status badges, mathematical operators, lock/shield security icons.
