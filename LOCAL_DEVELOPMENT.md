# PharmaCloud ERP — Local Development & Execution Guide

## 1. Prerequisites
- **Python**: Python 3.10+ with active virtual environment `.venv`
- **Node.js**: Node 22+ or 24+ and npm 11+
- **PostgreSQL**: PostgreSQL 16+ (or local Docker container `docker run -d --name pg-local -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:16-alpine`)
- **Redis**: Redis 7+ (or local Docker container `docker run -d --name redis-local -p 6379:6379 redis:7-alpine`)

---

## 2. Starting Backend Services Locally

### Step 1: Activate Virtual Environment
```bash
# In Windows PowerShell
cd backend
.\.venv\Scripts\Activate.ps1
```

### Step 2: Run Database Migrations & Django Checks
```bash
python manage.py check
python manage.py migrate
```

### Step 3: Start Django Local Development Server (Port 8000)
```bash
python manage.py runserver 127.0.0.1:8000
```

### Step 4: (Optional) Start Celery Worker & Beat
```bash
# Terminal A: Celery Worker
celery -A config worker -l INFO

# Terminal B: Celery Beat
celery -A config beat -l INFO
```

---

## 3. Starting Frontend Web App Locally

### Step 1: Install Dependencies
```bash
cd frontend
npm install
```

### Step 2: Start Next.js Development Server (Port 3000)
```bash
npm run dev
```

### Step 3: Access Application in Browser
Open `http://localhost:3000` to access the PharmaCloud ERP unified workspace.

---

## 4. Running Automated Local Tests
```bash
# Run all backend regression tests (578 tests)
cd backend
pytest tests/ -q --tb=short

# Run frontend type checking
cd frontend
npm run type-check

# Run frontend production build test
npm run build
```
