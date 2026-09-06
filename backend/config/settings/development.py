"""Development settings — local machine / docker-compose.dev.

Never deploy with these settings.
"""

from __future__ import annotations

from .base import *  # noqa: F401,F403
from .base import INSTALLED_APPS, MIDDLEWARE, REST_FRAMEWORK, SPECTACULAR_SETTINGS  # noqa: F401

DEBUG = True

ALLOWED_HOSTS = ["*"]  # dev only

# Debug Toolbar + Django Extensions
INSTALLED_APPS = [*INSTALLED_APPS, "debug_toolbar", "django_extensions"]

MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware", *MIDDLEWARE]

INTERNAL_IPS = ["127.0.0.1", "localhost"]

# Browsable API enabled for development inspection.
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_RENDERER_CLASSES": [
        *REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"],
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}

CORS_ALLOW_ALL_ORIGINS = True  # dev only

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Public API docs during development (production keeps them authenticated).
SPECTACULAR_SETTINGS = {
    **SPECTACULAR_SETTINGS,
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
}

# Local in-memory cache for dev if Redis is not running
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "pharmacloud-dev-cache",
    }
}

