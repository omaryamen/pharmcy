# PharmaCloud ERP — Production Architecture Design

## 1. System Topology & Network Architecture

```
                 [ Public Internet / Clients / Mobile Apps ]
                                      │
                                      ▼
                        [ HTTPS / TLS 1.3 - Port 443 ]
                                      │
                       ┌──────────────┴──────────────┐
                       │   Nginx Reverse Proxy (Edge)│
                       └──────────────┬──────────────┘
                                      │
               ┌──────────────────────┴──────────────────────┐
               │                                             │
               ▼                                             ▼
     [ Next.js 15 Web App ]                       [ Django 5 REST Backend ]
     (Port 3000 / SSR & SPA)                      (Port 8000 / Gunicorn)
                                                             │
                              ┌──────────────────────────────┼──────────────────────────────┐
                              │                              │                              │
                              ▼                              ▼                              ▼
                   [ PostgreSQL 16 Cluster ]          [ Redis 7 Cluster ]          [ S3 / MinIO Storage ]
                   (ACID / Double-Entry)              (Cache & Celery Broker)      (Prescriptions & Media)
                                                             │
                                              ┌──────────────┴──────────────┐
                                              │                             │
                                              ▼                             ▼
                                    [ Celery Workers (8x) ]        [ Celery Beat Scheduler ]
                                    (Outbox / Notifications)       (Billing & Expiry Scans)
```

---

## 2. Core Components & Runtime Topology
| Service | Runtime Engine | Scale / Concurrency | Memory Allocation | Health Probe |
|---|---|---|---|---|
| **Web Reverse Proxy** | Nginx 1.27 Alpine | Multi-worker event loop | 128 MB | `curl -f http://localhost:80/` |
| **Frontend UI** | Node 22 (Next.js 15 Standalone) | 4-8 Node worker instances | 512 MB | HTTP `200` on `/` |
| **Backend API** | Python 3.10 (Django 5 + Gunicorn) | 4-8 Gunicorn sync/async workers | 1 GB | `/api/v1/platform/health/` |
| **Asynchronous Engine** | Celery 5.4 + Redis | 8 worker threads | 512 MB | Celery inspect ping |
| **Cron Scheduler** | Celery Beat | 1 master scheduler process | 128 MB | Heartbeat log |
| **Primary Database** | PostgreSQL 16 Alpine | Dedicated connection pool | 2 - 8 GB | `pg_isready` |
| **Cache & Task Queue** | Redis 7 Alpine (AOF enabled) | In-memory with disk persistence | 512 MB - 2 GB | `redis-cli ping` |

---

## 3. Storage & Persistence Mapping
- **Database Storage Volume (`pgdata`)**: PostgreSQL relational data, write-ahead logs (WAL), indexes.
- **Cache Storage Volume (`redisdata`)**: Append-Only File (AOF) for Redis keys and message queues.
- **Static Assets Volume (`static_volume`)**: Minified JS/CSS, images, fonts, admin assets.
- **Protected Media Volume (`media_volume`)**: Medical prescription scans, customer invoices, signed documents.
