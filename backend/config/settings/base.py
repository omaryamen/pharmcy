"""Base settings shared by all environments.

Environment variables are read via django-environ from a ``.env`` file in the
project root. Every setting in this module can be overridden by an environment
variable. Environment-specific modules (development / testing / production)
import this module and apply their overrides.
"""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import environ

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/

env = environ.Env()

_env_file = BASE_DIR / ".env"
if _env_file.exists():
    environ.Env.read_env(str(_env_file))

# ---------------------------------------------------------------------------
# Core Django settings
# ---------------------------------------------------------------------------
DEBUG = env.bool("DJANGO_DEBUG", default=False)

if DEBUG:
    SECRET_KEY = env.str("DJANGO_SECRET_KEY", default="dev-insecure-secret-key-do-not-use-in-production")
else:
    SECRET_KEY = env.str("DJANGO_SECRET_KEY")  # required when DEBUG=False

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "0.0.0.0"])
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom user model (apps.core)
AUTH_USER_MODEL = "core.User"

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "django_celery_beat",
    "django_celery_results",
    "storages",
]

LOCAL_APPS = [
    "apps.common.apps.CommonConfig",
    "apps.core.apps.CoreConfig",
    "apps.authentication.apps.AuthenticationConfig",
    "apps.rbac.apps.RbacConfig",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # PharmaCloud custom middleware
    "apps.common.middleware.request_context.RequestContextMiddleware",
    "apps.common.middleware.tenant.TenantIdentificationMiddleware",
    "apps.rbac.middleware.PermissionContextMiddleware",
]

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ---------------------------------------------------------------------------
# Database (PostgreSQL via DATABASE_URL)
# ---------------------------------------------------------------------------
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres://postgres:postgres@localhost:5432/pharmacloud",
    )
}

DATABASES["default"]["ATOMIC_REQUESTS"] = True
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DATABASE_CONN_MAX_AGE", default=60)

# ---------------------------------------------------------------------------
# Cache (Redis)
# ---------------------------------------------------------------------------
REDIS_URL = env.str("REDIS_URL", default="redis://localhost:6379/0")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
        "TIMEOUT": 300,
    },
}

# ---------------------------------------------------------------------------
# Celery
# ---------------------------------------------------------------------------
CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", default=REDIS_URL)
CELERY_RESULT_BACKEND = env.str("CELERY_RESULT_BACKEND", default=REDIS_URL)

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=False)
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_WORKER_MAX_TASKS_PER_CHILD = 200
CELERY_WORKER_SEND_TASK_EVENTS = True
CELERY_TASK_SEND_SENT_EVENT = True
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internationalization & localization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en"
LANGUAGES = [
    ("en", "English"),
    ("ar", "العربية"),
]
TIME_ZONE = env.str("DJANGO_TIME_ZONE", default="UTC")
USE_I18N = True
USE_TZ = True
LOCALE_PATHS = [BASE_DIR / "locale"]

# ---------------------------------------------------------------------------
# Static & media
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", default="no-reply@pharmacloud.local")
SERVER_EMAIL = env.str("SERVER_EMAIL", default="errors@pharmacloud.local")
EMAIL_BACKEND = env.str("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "apps.common.api.renderers.ApiRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "apps.common.permissions.IsAuthenticatedAndActive",
    ],
    "DEFAULT_PAGINATION_CLASS": "apps.common.api.pagination.DefaultPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ["v1"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "apps.common.api.exceptions.api_exception_handler",
    "COERCE_DECIMAL_TO_STRING": True,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/min",
        "user": "1000/min",
        # Authentication endpoint scopes (apps.authentication.throttles).
        "auth_login_email": "10/min",
        "auth_login_ip": "30/min",
        "auth_password_reset_email": "5/hour",
        "auth_register_ip": "5/min",
    },
}

# ---------------------------------------------------------------------------
# JWT (djangorestframework-simplejwt)
# ---------------------------------------------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env.int("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", default=60)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("JWT_REFRESH_TOKEN_LIFETIME_DAYS", default=7)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    "TOKEN_USER_CLASS": "apps.core.models.user.User",
}

# ---------------------------------------------------------------------------
# Identity & security policy (apps.authentication)
# ---------------------------------------------------------------------------
# Brute-force protection: consecutive failed logins before the account locks.
AUTH_MAX_LOGIN_ATTEMPTS = env.int("AUTH_MAX_LOGIN_ATTEMPTS", default=5)

# Email verification is required before the account can log in.
AUTH_VERIFY_EMAIL_REQUIRED = env.bool("AUTH_VERIFY_EMAIL_REQUIRED", default=True)

# Verification codes (email / phone / password reset).
AUTH_VERIFICATION_CODE_LENGTH = env.int("AUTH_VERIFICATION_CODE_LENGTH", default=6)
AUTH_VERIFICATION_CODE_LIFETIME_MINUTES = env.int("AUTH_VERIFICATION_CODE_LIFETIME_MINUTES", default=10)
AUTH_VERIFICATION_MAX_ATTEMPTS = env.int("AUTH_VERIFICATION_MAX_ATTEMPTS", default=5)

# Password reuse prevention: how many recent hashes are compared on change.
AUTH_PASSWORD_HISTORY_SIZE = env.int("AUTH_PASSWORD_HISTORY_SIZE", default=5)

# Session ledger: lifetime of short-lived vs "remember me" sessions.
AUTH_SESSION_LIFETIME_DAYS = env.int("AUTH_SESSION_LIFETIME_DAYS", default=30)
AUTH_REMEMBER_ME_LIFETIME_DAYS = env.int("AUTH_REMEMBER_ME_LIFETIME_DAYS", default=90)

# Cap on concurrent active sessions per user; the oldest is revoked when
# exceeded (the login that pushes past the cap succeeds).
AUTH_MAX_ACTIVE_SESSIONS = env.int("AUTH_MAX_ACTIVE_SESSIONS", default=10)

# Optional pluggable SMS backend for phone verification codes. When unset the
# code is written to the application log (development / audit only).
AUTH_SMS_BACKEND = env.str("AUTH_SMS_BACKEND", default="")

# Redis brute-force counters are keyed per identifier; this is their TTL.
AUTH_THROTTLE_WINDOW_SECONDS = env.int("AUTH_THROTTLE_WINDOW_SECONDS", default=300)

# ---------------------------------------------------------------------------
# RBAC (apps.rbac)
# ---------------------------------------------------------------------------
# Superusers short-circuit every permission check (platform support bypass).
RBAC_SUPERADMIN_BYPASS = env.bool("RBAC_SUPERADMIN_BYPASS", default=True)

# Effective-permission cache TTL (seconds). Correctness is guaranteed by the
# global version counter, so TTL only bounds cache growth.
RBAC_CACHE_TTL_SECONDS = env.int("RBAC_CACHE_TTL_SECONDS", default=300)

# Prevent an actor from granting a role whose granted permissions exceed the
# actor's own effective permissions.
RBAC_ENFORCE_ESCALATION_GUARD = env.bool("RBAC_ENFORCE_ESCALATION_GUARD", default=True)

# How many role version snapshots are retained per role (older ones are pruned).
RBAC_ROLE_HISTORY_MAX_VERSIONS = env.int("RBAC_ROLE_HISTORY_MAX_VERSIONS", default=20)

# Roles provisioned / protected during tenant bootstrap.
RBAC_PROTECTED_ROLE_CODES = env.list("RBAC_PROTECTED_ROLE_CODES", default=["admin"])
RBAC_DEFAULT_ROLE_CODES = env.list("RBAC_DEFAULT_ROLE_CODES", default=["member"])

# Provision baseline roles automatically when a new tenant is created.
RBAC_BOOTSTRAP_ON_TENANT_CREATE = env.bool("RBAC_BOOTSTRAP_ON_TENANT_CREATE", default=True)

# Allowed permission-code shape: <module>.<resource>.<action>.
RBAC_PERMISSION_CODE_REGEX = env.str(
    "RBAC_PERMISSION_CODE_REGEX",
    default=r"^[a-z][a-z0-9_]*(\.[a-z0-9_]+)+$",
)

# ---------------------------------------------------------------------------
# API documentation (drf-spectacular)
# ---------------------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "PharmaCloud ERP API",
    "DESCRIPTION": (
        "Enterprise multi-tenant SaaS pharmacy ERP platform. "
        "Country-neutral core with plugin-based market packs (GCC + Yemen). "
        "Base API exposes authentication, health checks, and the versioned "
        "envelope contract used by all business modules."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "COMPONENT_SPLIT_PATCH": True,
    "SWAGGER_UI_SETTINGS": {"persistAuthorization": True},
    "SECURITY": [{"BearerAuth": []}],
    "TAGS": [
        {"name": "health", "description": "Liveness & readiness probes"},
        {"name": "auth", "description": "JWT authentication endpoints"},
        {"name": "rbac", "description": "Roles, permissions, assignments and effective-permission queries"},
    ],
}

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = env.bool("CORS_ALLOW_ALL_ORIGINS", default=False)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_LEVEL = env.str("LOG_LEVEL", default="INFO")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        },
        "json": {
            "()": "apps.common.utils.logging.JsonFormatter",
        },
    },
    "filters": {
        "request_context": {
            "()": "apps.common.utils.logging.RequestContextFilter",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "filters": ["request_context"],
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": LOG_LEVEL, "propagate": False},
        "django.server": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "django.request": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "django.db.backends": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "apps": {"handlers": ["console"], "level": LOG_LEVEL, "propagate": False},
        "celery": {"handlers": ["console"], "level": LOG_LEVEL, "propagate": False},
        "redis": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}

# ---------------------------------------------------------------------------
# Health / observability
# ---------------------------------------------------------------------------
# Optional: expose request duration and structure in the log formatter.
REQUEST_ID_HEADER = "HTTP_X_REQUEST_ID"
TENANT_HEADER = "X-Tenant-ID"
