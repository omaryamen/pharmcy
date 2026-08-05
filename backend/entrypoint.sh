#!/usr/bin/env sh
# ======================================================================
# Entrypoint for PharmaCloud ERP containers.
# Waits for the database, optionally migrates / collects static files,
# then delegates to the container command.
# ======================================================================
set -e

echo "[entrypoint] Waiting for database..."
python /app/scripts/wait_for_db.py

if [ "${DJANGO_MIGRATE:-true}" = "true" ]; then
    echo "[entrypoint] Applying database migrations..."
    python /app/manage.py migrate --noinput
fi

if [ "${DJANGO_COLLECTSTATIC:-true}" = "true" ]; then
    echo "[entrypoint] Collecting static files..."
    python /app/manage.py collectstatic --noinput
fi

echo "[entrypoint] Starting: $*"
exec "$@"
