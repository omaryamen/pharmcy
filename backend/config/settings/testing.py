"""Testing settings — used by the pytest suite.

Defaults to an in-memory SQLite database so the suite runs anywhere.
Set ``DATABASE_URL`` in the environment (CI) to run against PostgreSQL.
"""

from __future__ import annotations

import os

from .base import *  # noqa: F401,F403
from .base import env

DEBUG = False
TESTING = True

SECRET_KEY = env.str("DJANGO_SECRET_KEY", default="testing-insecure-secret-key")

# Fast password hashing for tests.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Run Celery tasks synchronously in tests.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# In-memory SQLite by default; CI overrides with TEST_DATABASE_URL (PostgreSQL).
# A dedicated variable (not DATABASE_URL) keeps the local .env out of the suite.
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
if TEST_DATABASE_URL:
    DATABASES = {
        "default": env.db_url("TEST_DATABASE_URL"),
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }

# Local, in-memory cache to avoid a Redis requirement for unit tests.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Keep throttle limits out of the way for the API tests.
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {  # noqa: F405
    "anon": "1000/min",
    "user": "10000/min",
    "auth_login_email": "100/min",
    "auth_login_ip": "300/min",
    "auth_password_reset_email": "60/hour",
    "auth_register_ip": "60/min",
}

# Capture emails in memory so tests can assert on deliveries.
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Local file storage for tests; media root overridden in conftest.
MEDIA_ROOT = "media_test"
STATIC_ROOT = "staticfiles_test"
