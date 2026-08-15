# PharmaCloud ERP — Production Readiness & Deployment Checklist

## 1. Environment & Infrastructure Readiness
- **Database**: PostgreSQL 16+ with connection pooling (PgBouncer) and SSL enforcement.
- **Cache & Message Broker**: Redis 7+ for Celery task queues, brute-force rate-limiting, and WebSocket channels.
- **Async Workers**: Celery workers & Celery Beat for scheduled notifications, outbox event dispatching, and SaaS billing cycle renewals.
- **Object Storage**: S3/MinIO compliant storage with private ACLs and signed temporary URLs for prescription PDFs and invoices.

---

## 2. Security & Compliance Checklist
- [x] Multi-tenant isolation verified across 39 enterprise modules.
- [x] Dynamic RBAC with permission caching and role hierarchies validated.
- [x] Security headers middleware (CSP, HSTS, X-Content-Type-Options, Referrer-Policy, Permissions-Policy) active.
- [x] Double-entry inventory ledger with FEFO batch allocation and negative-stock prevention enforced.
- [x] Idempotency keys enforced on checkout, stock movements, and financial postings.
- [x] Token rotation and blacklisting verified.
- [x] Next.js 15 frontend production build verified (17/17 routes optimized).
- [x] Backend test suite passing (576/576 tests).

---

## 3. Disaster Recovery & Operational Metrics
- **RPO Target**: < 5 minutes (Continuous PostgreSQL WAL archiving).
- **RTO Target**: < 15 minutes (Automated container redeployment and database failover).
- **Health Probes**:
  - Liveness: `/api/v1/platform/health/`
  - System Telemetry: `/api/v1/platform/overview/`
