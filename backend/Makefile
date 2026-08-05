# ======================================================================
# PharmaCloud ERP backend — Makefile
# Usage: make <target>
# NOTE: On Windows use PowerShell or WSL. See README for manual commands.
# ======================================================================

PYTHON       := python
DJANGO       := python manage.py
SETTINGS     ?= config.settings.development
TEST_SETTINGS ?= config.settings.testing
COMPOSE      := docker compose
COMPOSE_PROD := docker compose -f docker-compose.prod.yml

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-24s\033[0m %s\n", $$1, $$2}'

# ----------------------------------------------------------------------
# Setup
# ----------------------------------------------------------------------
.PHONY: install
install: ## Install dev dependencies into the current environment
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements/development.txt

.PHONY: venv
venv: ## Create a virtual environment (.venv)
	$(PYTHON) -m venv .venv

# ----------------------------------------------------------------------
# Django
# ----------------------------------------------------------------------
.PHONY: run
run: ## Run the development server
	DJANGO_SETTINGS_MODULE=$(SETTINGS) $(DJANGO) runserver 0.0.0.0:8000

.PHONY: shell
shell: ## Open a Django shell
	DJANGO_SETTINGS_MODULE=$(SETTINGS) $(DJANGO) shell

.PHONY: migrate
migrate: ## Apply database migrations
	DJANGO_SETTINGS_MODULE=$(SETTINGS) $(DJANGO) migrate

.PHONY: makemigrations
makemigrations: ## Create migrations for app changes
	DJANGO_SETTINGS_MODULE=$(SETTINGS) $(DJANGO) makemigrations

.PHONY: check
check: ## Run Django system checks
	DJANGO_SETTINGS_MODULE=$(SETTINGS) $(DJANGO) check

.PHONY: createsuperuser
createsuperuser: ## Create a Django superuser
	DJANGO_SETTINGS_MODULE=$(SETTINGS) $(DJANGO) createsuperuser

.PHONY: collectstatic
collectstatic: ## Collect static files
	DJANGO_SETTINGS_MODULE=$(SETTINGS) $(DJANGO) collectstatic --noinput

# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------
.PHONY: test
test: ## Run the test suite
	DJANGO_SETTINGS_MODULE=$(TEST_SETTINGS) pytest

.PHONY: test-cov
test-cov: ## Run tests with coverage report
	DJANGO_SETTINGS_MODULE=$(TEST_SETTINGS) pytest --cov=. --cov-report=term-missing --cov-report=xml

.PHONY: test-watch
test-watch: ## Run tests in watch mode
	DJANGO_SETTINGS_MODULE=$(TEST_SETTINGS) pytest-watch

# ----------------------------------------------------------------------
# Quality
# ----------------------------------------------------------------------
.PHONY: lint
lint: ## Run ruff linter
	ruff check .

.PHONY: format
format: ## Format code with black/isort
	black .
	isort .

.PHONY: format-check
format-check: ## Verify formatting
	black --check .
	isort --check-only --profile black --line-length 119 .

.PHONY: pre-commit-install
pre-commit-install: ## Install pre-commit hooks
	pre-commit install

.PHONY: pre-commit-run
pre-commit-run: ## Run all pre-commit hooks
	pre-commit run --all-files

# ----------------------------------------------------------------------
# Docker (development)
# ----------------------------------------------------------------------
.PHONY: docker-up
docker-up: ## Start the dev stack (db, redis, minio, web, workers)
	$(COMPOSE) up --build

.PHONY: docker-up-d
docker-up-d: ## Start the dev stack detached
	$(COMPOSE) up -d --build

.PHONY: docker-down
docker-down: ## Stop the dev stack
	$(COMPOSE) down

.PHONY: docker-down-v
docker-down-v: ## Stop the dev stack and remove volumes
	$(COMPOSE) down -v

.PHONY: docker-logs
docker-logs: ## Tail logs from the dev stack
	$(COMPOSE) logs -f

# ----------------------------------------------------------------------
# Docker (production)
# ----------------------------------------------------------------------
.PHONY: prod-up
prod-up: ## Start the production stack
	$(COMPOSE_PROD) up -d --build

.PHONY: prod-down
prod-down: ## Stop the production stack
	$(COMPOSE_PROD) down

# ----------------------------------------------------------------------
# Celery
# ----------------------------------------------------------------------
.PHONY: celery-worker
celery-worker: ## Start a Celery worker
	celery -A config worker -l INFO

.PHONY: celery-beat
celery-beat: ## Start the Celery beat scheduler
	celery -A config beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler

# ----------------------------------------------------------------------
# Cleanup
# ----------------------------------------------------------------------
.PHONY: clean
clean: ## Remove caches and build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +
	rm -rf htmlcov .coverage coverage.xml

.PHONY: tree
tree: ## Print the project tree (Windows: use `tree /F /A`)
	@command -v tree >/dev/null 2>&1 && tree -a -I '.git|.venv|__pycache__|.pytest_cache|.ruff_cache|media|staticfiles' || echo "Install the 'tree' command to use this target."
