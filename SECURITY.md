# PharmaCloud ERP — Security Architecture & Policy

## 1. Security Overview & Principles
PharmaCloud ERP is an enterprise multi-tenant pharmaceutical SaaS platform designed with defense-in-depth, least privilege, zero trust, and OWASP Top 10 compliance:
- **Tenant Isolation**: Every database table and API query is strictly scoped to `tenant_id`. Row-level checks and middleware guarantee zero data leakage across tenant boundaries.
- **Server Authoritative**: Client-supplied prices, financial totals, stock quantities, and clinical approval flags are strictly recalculated server-side.
- **Double-Entry FEFO Inventory**: Stock adjustments and dispensations execute exclusively via the authoritative `StockMovementEngine` with row-level locks (`select_for_update`) and idempotency keys.
- **Prescription Privacy & Narcotics Control**: Patient prescription files and controlled substances (narcotics/psychotropics) require certified pharmacist RBAC authorization with immutable audit logging.

---

## 2. Authentication & Session Security
- **JWT with Token Rotation & Blacklisting**: Refresh tokens rotate on every usage (`ROTATE_REFRESH_TOKENS = True`, `BLACKLIST_AFTER_ROTATION = True`).
- **Brute-Force & Rate Limiting**: Redis-backed throttling throttles failed login attempts and sensitive mutations (`10/min` on login, `100/min` anonymous, `1000/min` authenticated).
- **MFA & Multi-Device Management**: Device registration tracks hardware UUIDs, push tokens, and supports instantaneous remote session revocation upon logout.

---

## 3. HTTP Security Headers
All responses are enforced via `SecurityHeadersMiddleware`:
- `Content-Security-Policy`: `default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data: https: blob:; connect-src 'self' https: ws: wss:; frame-ancestors 'none'; object-src 'none';`
- `Permissions-Policy`: `camera=(self), microphone=(), geolocation=(), payment=(self)`
- `X-Content-Type-Options`: `nosniff`
- `Referrer-Policy`: `strict-origin-when-cross-origin`
- `Cross-Origin-Opener-Policy`: `same-origin`

---

## 4. Audit & Compliance
- **FullAuditModel & Soft Deletion**: Records preserve `created_by`, `updated_by`, `deleted_by`, `created_at`, `updated_at`, `deleted_at`.
- **Platform Operations & Impersonation Audit**: Super Admin actions (tenant suspension, feature flags, maintenance windows, impersonation) are immutably logged with actor, target, reason, and timestamps.
