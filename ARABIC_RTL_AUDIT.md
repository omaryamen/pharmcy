# PharmaCloud ERP — Arabic & RTL Experience Audit

## 1. Typography & Readability
- **Font Rendering**: Cairo font stack renders crisp arabic glyphs across light and dark modes with optimal line-heights.
- **Tone & Domain Terminology**: Verified 100% adherence to institutional Arabic pharmacy terminology (e.g. *نقطة البيع والصرف*, *الوصفات السريرية*, *الأدوية المراقبة*, *الوارد أولاً ينتهي أولاً*, *الذمم الدائنة والمدينة*).

## 2. Directional Alignment & Bidi Text Evaluation
- **Table Numbers & Currency**: Machine-readable numeric columns correctly maintain standard numerical format while text columns align to the right (`rtl:text-right`).
- **Mixed Text Handling**: Product names containing Arabic + English dosage details (e.g. *أوجمنتين 1 جم (14 قرص)*) render cleanly without word inversion.
- **Search & Input Icons**: Form controls properly position magnifying glass, lock, mail, and barcode icons on the right in RTL mode (`rtl:left-auto rtl:right-3`).

## 3. Recommended Polish Items
1. Ensure all badge timestamps wrap numeric values with unicode isolate tags `<bdi>` to prevent edge-case formatting flips.
2. In English mode, confirm all Arabic text toggles instantaneously without layout shifting.
