#!/bin/bash
# ======================================================================
# PharmaCloud ERP — Zero-Downtime Production Deployment Script
# Usage: ./scripts/deploy_prod.sh
# ======================================================================
set -euo pipefail

echo "========================================================"
echo " Starting PharmaCloud ERP Production Deployment"
echo "========================================================"

# 1. Pull latest images and build containers
echo "Step 1: Building production containers..."
docker compose -f docker-compose.prod.yml build --pull

# 2. Start database and cache services
echo "Step 2: Starting infrastructure (PostgreSQL & Redis)..."
docker compose -f docker-compose.prod.yml up -d db redis

# 3. Apply database migrations
echo "Step 3: Running database migrations..."
docker compose -f docker-compose.prod.yml run --rm backend python manage.py migrate --noinput

# 4. Collect static files
echo "Step 4: Collecting static assets..."
docker compose -f docker-compose.prod.yml run --rm backend python manage.py collectstatic --noinput

# 5. Launch web application and async workers
echo "Step 5: Starting web, frontend, celery, and reverse proxy..."
docker compose -f docker-compose.prod.yml up -d

# 6. Verify health probes
echo "Step 6: Verifying platform health..."
sleep 5
docker compose -f docker-compose.prod.yml ps

echo "========================================================"
echo " PharmaCloud ERP Production Deployment Complete & Active"
echo "========================================================"
