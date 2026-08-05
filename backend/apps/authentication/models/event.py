"""Security audit trail.

Every notable identity event (login, logout, lockout, password change,
verification, account state transition, session revocation) is recorded here.
Events survive the (soft) deletion of their user because the FK is ``SET_NULL``
and soft deletion never issues a physical delete. Used by admin and by the
``/auth/security/events/`` API.
"""

from __future__ import annotations

from typing import Any

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import UUIDTimeStampedModel


class SecurityEventType(models.TextChoices):
    """Auditable identity events."""

    REGISTERED = "registered", _("Account registered")
    LOGIN_SUCCESS = "login_success", _("Login succeeded")
    LOGIN_FAILED = "login_failed", _("Login failed")
    LOGIN_LOCKED = "login_locked", _("Account locked after failed logins")
    LOGOUT = "logout", _("Logged out")
    TOKEN_REFRESHED = "token_refreshed", _("Token refreshed")
    EMAIL_VERIFICATION_REQUESTED = "email_verification_requested", _("Email verification requested")
    EMAIL_VERIFIED = "email_verified", _("Email verified")
    PHONE_VERIFICATION_REQUESTED = "phone_verification_requested", _("Phone verification requested")
    PHONE_VERIFIED = "phone_verified", _("Phone verified")
    PASSWORD_RESET_REQUESTED = "password_reset_requested", _("Password reset requested")
    PASSWORD_RESET_CONFIRMED = "password_reset_confirmed", _("Password reset confirmed")
    PASSWORD_CHANGED = "password_changed", _("Password changed")
    SESSION_REVOKED = "session_revoked", _("Session revoked")
    ACCOUNT_LOCKED = "account_locked", _("Account locked")
    ACCOUNT_UNLOCKED = "account_unlocked", _("Account unlocked")
    ACCOUNT_DEACTIVATED = "account_deactivated", _("Account deactivated")
    ACCOUNT_ACTIVATED = "account_activated", _("Account activated")
    PROFILE_UPDATED = "profile_updated", _("Profile updated")


class SecurityEvent(UUIDTimeStampedModel):
    """A single security-relevant identity event."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="security_events",
        verbose_name="User",
    )
    session = models.ForeignKey(
        "authentication.LoginSession",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="security_events",
        verbose_name="Session",
    )
    event_type = models.CharField(
        max_length=40,
        choices=SecurityEventType.choices,
        db_index=True,
        verbose_name="Event type",
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP address")
    user_agent = models.TextField(blank=True, default="", verbose_name="User agent")
    device_name = models.CharField(max_length=255, blank=True, default="", verbose_name="Device name")
    details = models.JSONField(default=dict, blank=True, verbose_name="Details")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Security event"
        verbose_name_plural = "Security events"
        indexes = [
            models.Index(fields=["user", "-created_at"], name="auth_event_user_created_idx"),
            models.Index(fields=["event_type", "-created_at"], name="auth_event_type_created_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.get_event_type_display()} / {self.user}"

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------
    @classmethod
    def record(
        cls,
        *,
        user,
        event_type: str,
        request=None,
        session=None,
        details: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        device_name: str = "",
    ) -> SecurityEvent:
        """Create an event, pulling request metadata when provided."""
        if request is not None:
            ip_address = ip_address or request.META.get("REMOTE_ADDR")
            user_agent = user_agent or request.META.get("HTTP_USER_AGENT", "")
        return cls.objects.create(
            user=user,
            session=session,
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent or "",
            device_name=device_name,
            details=details or {},
        )
