"""DRF throttles for authentication endpoints.

Coarse, identifier-scoped rate limits complement the account-level lockout:
brute-force attacks that rotate identities/IPs are still bounded because the
``failed_login_attempts`` counter and lockout live in the database, while these
throttles bound request volume per email and per IP on sensitive endpoints.

All scopes are configured in ``REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]`` and
rely on the Redis-backed default cache in production (locmem in tests).
"""

from __future__ import annotations

from rest_framework.request import Request
from rest_framework.throttling import SimpleRateThrottle


class EmailScopedRateThrottle(SimpleRateThrottle):
    """Rate-limit by a request-body identifier (e.g. email)."""

    scope = None
    identifier_field = "email"

    def get_cache_key(self, request: Request, view) -> str | None:
        if self.get_rate() is None:
            return None
        try:
            identifier = str(request.data.get(self.identifier_field, "")).strip().lower()
        except Exception:  # noqa: BLE001 - unparseable body, fall back to IP
            identifier = ""
        if not identifier:
            identifier = f"ip:{self.get_ident(request)}"
        return self.cache_format % {"scope": self.scope, "ident": identifier}


class LoginEmailThrottle(EmailScopedRateThrottle):
    """Bounded login attempts per email address."""

    scope = "auth_login_email"


class PasswordResetEmailThrottle(EmailScopedRateThrottle):
    """Bounded password-reset requests per email address."""

    scope = "auth_password_reset_email"


class IPRateThrottle(SimpleRateThrottle):
    """Rate-limit by client IP only."""

    scope = None

    def get_cache_key(self, request: Request, view) -> str | None:
        if self.get_rate() is None:
            return None
        ident = self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}


class LoginIPThrottle(IPRateThrottle):
    """Bounded login attempts per client IP."""

    scope = "auth_login_ip"


class RegisterIPThrottle(IPRateThrottle):
    """Bounded registration requests per client IP (anti-abuse)."""

    scope = "auth_register_ip"
