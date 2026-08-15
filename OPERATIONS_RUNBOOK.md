# PharmaCloud ERP — Operations Runbook & Maintenance Guide

## 1. Routine Operational Commands

### Checking Service Status
```bash
docker compose -f docker-compose.prod.yml ps
```

### Inspecting Live Production Logs
```bash
# Stream all logs
docker compose -f docker-compose.prod.yml logs -f --tail=100

# Stream backend API errors only
docker compose -f docker-compose.prod.yml logs -f backend

# Stream async Celery worker logs
docker compose -f docker-compose.prod.yml logs -f celery-worker
```

### Restarting Application Services
```bash
# Graceful restart of web backend
docker compose -f docker-compose.prod.yml restart backend

# Restart Celery workers after code update
docker compose -f docker-compose.prod.yml restart celery-worker celery-beat
```

---

## 2. Backup & Disaster Recovery Runbook

### Running Manual Database Backup
```bash
./scripts/backup_db.sh
```

### Restoring Database from Backup
```bash
./scripts/restore_db.sh /var/backups/pharmacloud/pharmacloud_db_20260815_120000.sql.gz
```

---

## 3. Incident Response Protocol
1. **Database Degradation**: Check connection pool utilization and `pg_stat_activity`.
2. **Celery Worker Hang**: Inspect dead-letter queue and restart `celery-worker`.
3. **Emergency Maintenance**: Trigger maintenance mode via Platform Ops API `/api/v1/platform/maintenance/`.
