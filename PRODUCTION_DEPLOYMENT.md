# PharmaCloud ERP — Production Deployment Guide

## 1. Prerequisites
- **Operating System**: Ubuntu 22.04 LTS / Debian 12 / RHEL 9 (Linux x86_64 or ARM64).
- **Runtime Tools**: Docker 26+, Docker Compose v2.24+, Git.
- **Hardware Sizing**: Minimum 4 vCPU, 8 GB RAM, 50 GB NVMe SSD.
- **Network**: Open ports 80 (HTTP) and 443 (HTTPS). Internal ports (5432, 6379, 8000, 3000) strictly blocked from public ingress.

---

## 2. Step-by-Step Deployment Procedure

### Step 1: Clone Repository & Create Environment Configuration
```bash
git clone https://github.com/omaryamen/pharmcy.git /opt/pharmacloud
cd /opt/pharmacloud

# Create production environment file from template
cp backend/.env.example .env.production
chmod 600 .env.production
```

### Step 2: Configure Production Environment Variables
Edit `.env.production` with secure randomly-generated secrets:
- `DJANGO_SECRET_KEY`: High-entropy 64-character string (`openssl rand -hex 32`).
- `POSTGRES_PASSWORD`: Strong database password.
- `REDIS_PASSWORD`: Strong Redis authentication password.
- `DJANGO_ALLOWED_HOSTS`: Domain names (e.g. `pharmacloud.app,api.pharmacloud.app`).
- `DJANGO_CSRF_TRUSTED_ORIGINS`: Origins (e.g. `https://pharmacloud.app,https://api.pharmacloud.app`).

### Step 3: Run Deployment Automation
```bash
chmod +x scripts/*.sh
./scripts/deploy_prod.sh
```

### Step 4: Verify Deployment Health
```bash
docker compose -f docker-compose.prod.yml ps
curl -I https://pharmacloud.app/api/v1/platform/health/
```
