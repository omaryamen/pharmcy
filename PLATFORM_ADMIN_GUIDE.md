# PharmaCloud ERP — Platform Administration & Control Center Guide (دليل إدارة المنصة السحابية)

## 1. Overview & Over-Tenant Role Architecture
The **Platform SuperAdmin** operates above individual tenant pharmacies, governing platform-wide SaaS infrastructure, multi-tenant isolation boundaries, subscription entitlements, global feature flags, system health diagnostics, and immutable audit logs.

```
                  ┌───────────────────────────────────────────────┐
                  │       PharmaCloud Platform SuperAdmin         │
                  │              (Over-Tenant Level)              │
                  └───────────────────────┬───────────────────────┘
                                          │
       ┌──────────────────────────────────┼──────────────────────────────────┐
       │                                  │                                  │
       ▼                                  ▼                                  ▼
[ Tenant: Al-Amal ]             [ Tenant: Al-Shifa ]              [ Tenant: Al-Noor ]
 ├── 5 Branches                  ├── 2 Branches                    ├── 1 Branch
 └── 18 Users                    └── 8 Users                       └── 3 Users
```

---

## 2. Platform Admin Workspaces & Capabilities

| Sub-Module / Workspace | Capabilities | Access / Isolation Rule |
|---|---|---|
| **Platform Overview** | Real-time C-level metrics: Total tenants, MRR/ARR, active subscriptions, health summary. | Superadmin only (`IsAdminUser`). |
| **Tenant Management** | Tenant provisioning, status switching (Active ➔ Suspended ➔ Reactivated), plan quotas. | Isolated to metadata; cannot access patient PHI without audited impersonation. |
| **Feature Flags** | Progressive rollout management (0-100%), global vs tenant-specific feature toggles. | Changes immediately audited in `PlatformAuditLog`. |
| **Tenant Impersonation** | Regulated support session with visible impersonation banner and explicit termination. | Mandatory ticket reference and immutable session token logging. |
| **Emergency Maintenance** | Activate platform-wide maintenance mode with custom user message. | Blocks standard tenant users while preserving platform admin access. |
| **Platform Audit Log** | Immutable append-only log tracking all privileged administrative operations. | Actor, Action, Target Tenant, IP, Timestamp, and Delta Payload. |

---

## 3. API Endpoints

- `GET /api/v1/platform/overview/` — High-level platform KPIs and MRR aggregates.
- `GET /api/v1/platform/health/` — Component-level latency and health diagnostics.
- `POST /api/v1/platform/tenants/{pk}/suspend/` — Suspend non-compliant tenant.
- `POST /api/v1/platform/tenants/{pk}/reactivate/` — Reactivate suspended tenant.
- `POST /api/v1/platform/tenants/{pk}/impersonate/` — Start audited impersonation session.
- `GET /api/v1/platform/feature-flags/` — List global and tenant feature flags.
