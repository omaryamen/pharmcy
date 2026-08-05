"""Authentication app — identity lifecycle.

Implements login / logout / refresh / verification / password flows on top of
the ``core.User`` model, with session tracking, brute-force protection and a
full security audit trail. JWT (SimpleJWT) remains the token backend; this app
adds the session ledger, hashed verification tokens, password-history reuse
prevention and per-endpoint throttling.
"""

from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.authentication"
    label = "authentication"
    verbose_name = "Authentication"

    def ready(self) -> None:
        from . import signals  # noqa: F401
