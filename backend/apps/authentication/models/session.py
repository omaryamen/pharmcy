"""Login session ledger.

Each issued refresh token is tracked as a ``LoginSession`` so sessions can be
listed, touched and revoked independently. Revoking a session blacklists its
refresh token (SimpleJWT ``token_blacklist``) which immediately invalidates
that session's ability to mint new access tokens.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import UUIDTimeStampedModel


class SessionDeviceType(models.TextChoices):
    """Device class reported by the client (used for display, not trust)."""

    WEB = "web", _("Web")
    MOBILE = "mobile", _("Mobile")
    TABLET = "tablet", _("Tablet")
    DESKTOP = "desktop", _("Desktop")
    API = "api", _("API")


class SessionRevokeReason(models.TextChoices):
    """Why a session was ended."""

    LOGOUT = "logout", _("User logged out")
    SECURITY = "security", _("Revoked for security reasons")
    PASSWORD_CHANGE = "password_change", _("Password was changed")
    ADMIN = "admin", _("Revoked by an administrator")
    EXPIRED = "expired", _("Session expired")


class LoginSession(UUIDTimeStampedModel):
    """One authenticated device / refresh token.

    ``refresh_token_jti`` is the JWT identifier of the refresh token this
    session issued for. ``expires_at`` reflects ``remember_me``: remembered
    sessions outlive short-lived ones and are kept until explicitly revoked.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="login_sessions",
        verbose_name="User",
    )
    refresh_token_jti = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        verbose_name="Refresh token JTI",
    )
    device_name = models.CharField(max_length=255, blank=True, default="", verbose_name="Device name")
    device_type = models.CharField(
        max_length=24,
        choices=SessionDeviceType.choices,
        default=SessionDeviceType.WEB,
        verbose_name="Device type",
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP address")
    user_agent = models.TextField(blank=True, default="", verbose_name="User agent")
    remember_me = models.BooleanField(default=False, verbose_name="Remember me")

    is_active = models.BooleanField(default=True, db_index=True, verbose_name="Active")
    last_used_at = models.DateTimeField(null=True, blank=True, verbose_name="Last used at")
    expires_at = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name="Expires at")

    revoked_at = models.DateTimeField(null=True, blank=True, verbose_name="Revoked at")
    revoked_reason = models.CharField(
        max_length=32,
        choices=SessionRevokeReason.choices,
        null=True,
        blank=True,
        verbose_name="Revoke reason",
    )
    revoked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="Revoked by",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Login session"
        verbose_name_plural = "Login sessions"
        indexes = [
            models.Index(fields=["user", "is_active"], name="auth_session_user_active_idx"),
            models.Index(fields=["user", "-created_at"], name="auth_session_user_created_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.user} / {self.get_device_type_display()}"

    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------
    @property
    def is_revoked(self) -> bool:
        return not self.is_active

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return timezone.now() >= self.expires_at

    # ------------------------------------------------------------------
    # Transitions (persisted; policy lives in services)
    # ------------------------------------------------------------------
    def touch(self) -> None:
        """Mark the session as the most recently used one."""
        self.last_used_at = timezone.now()
        self.save(update_fields=["last_used_at", "updated_at"])

    def revoke(self, *, reason: str = SessionRevokeReason.LOGOUT, by=None) -> None:
        """End the session. Idempotent: a revoked session stays revoked."""
        if self.is_active:
            self.is_active = False
            self.revoked_at = timezone.now()
            self.revoked_reason = reason
            self.revoked_by = by
            self.save(
                update_fields=[
                    "is_active",
                    "revoked_at",
                    "revoked_reason",
                    "revoked_by",
                    "updated_at",
                ]
            )
