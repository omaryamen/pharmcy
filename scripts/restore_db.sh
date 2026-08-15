#!/bin/bash
# ======================================================================
# PharmaCloud ERP — Database Restore Script
# Usage: ./scripts/restore_db.sh /path/to/backup.sql.gz
# ======================================================================
set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Usage: $0 <path_to_backup_file.sql.gz>"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "${BACKUP_FILE}" ]; then
    echo "Error: Backup file '${BACKUP_FILE}' not found."
    exit 1
fi

read -p "WARNING: This will overwrite the current database. Proceed? (y/N): " CONFIRM
if [[ "${CONFIRM}" != [yY] && "${CONFIRM}" != [yY][eE][sS] ]]; then
    echo "Restore cancelled."
    exit 0
fi

echo "[$(date)] Restoring database from ${BACKUP_FILE}..."
gunzip -c "${BACKUP_FILE}" | docker compose -f docker-compose.prod.yml exec -T db psql -U "${POSTGRES_USER:-pharmacloud}" -d pharmacloud

echo "[$(date)] Database restoration completed successfully."
