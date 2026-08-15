#!/bin/bash
# ======================================================================
# PharmaCloud ERP — Automated Database Backup Script
# Usage: ./scripts/backup_db.sh
# ======================================================================
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/var/backups/pharmacloud}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="${BACKUP_DIR}/pharmacloud_db_${TIMESTAMP}.sql.gz"

mkdir -p "${BACKUP_DIR}"

echo "[$(date)] Starting database backup..."
docker compose -f docker-compose.prod.yml exec -T db pg_dump -U "${POSTGRES_USER:-pharmacloud}" -d pharmacloud | gzip > "${FILENAME}"

echo "[$(date)] Backup successfully generated: ${FILENAME} ($(du -h "${FILENAME}" | cut -f1))"

# Retention: Delete backups older than 30 days
find "${BACKUP_DIR}" -type f -name "pharmacloud_db_*.sql.gz" -mtime +30 -delete
echo "[$(date)] 30-day retention cleanup complete."
