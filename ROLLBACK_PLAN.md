# PharmaCloud ERP — Production Rollback Plan

## 1. Quick Application Rollback (Code Revert)
If a software defect is detected immediately post-deployment:

```bash
# 1. Rollback Git repository to the previous release tag
git checkout v1.34.0

# 2. Re-build and restart containers
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

---

## 2. Database Migration Rollback
If a backward-incompatible schema migration caused issues:

```bash
# 1. Revert specific migration in Django
docker compose -f docker-compose.prod.yml run --rm backend python manage.py migrate <app_name> <previous_migration_name>

# 2. Restart backend
docker compose -f docker-compose.prod.yml restart backend
```

---

## 3. Full Catastrophic Disaster Recovery
In the event of database corruption or unrecoverable loss:

1. Stop web traffic: `docker compose -f docker-compose.prod.yml stop backend frontend nginx`
2. Restore database from pre-deployment snapshot: `./scripts/restore_db.sh <backup_file.sql.gz>`
3. Restart all services: `docker compose -f docker-compose.prod.yml up -d`
4. Run health check: `curl -f http://localhost:80/api/v1/platform/health/`
