"""Verification / one-time tokens.

Covers email verification, phone verification and password reset. The
human-facing code is delivered in plaintext (email / SMS) but only its
SHA-256 digest is ever stored, so a database leak cannot be replayed as a
valid token. Codes are single-use, expire, and are rate-limited per token.
"""

from __future__ import annotations

import hashlib
import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import UUIDTimeStampedModel


class VerificationTokenKind(models.TextChoices):
    """What the token authorizes."""

    EMAIL_VERIFICATION = "email_verification", _("Email verification")
    PHONE_VERIFICATION = "phone_verification", _("Phone verification")
    PASSWORD_RESET = "password_reset", _("Password reset")
    EMAIL_CHANGE = "email_change", _("Email change")


class VerificationToken(UUIDTimeStampedModel):
    """A hashed, single-use, expiring verification code.

    ``token_hash`` stores ``sha256(code)``. ``expires_at`` enforces validity,
    ``consumed_at`` enforces single use and ``attempts`` / ``max_attempts``
    rate-limit guessing attempts on the plaintext code.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="verification_tokens",
        verbose_name="User",
    )
    kind = models.CharField(
        max_length=32,
        choices=VerificationTokenKind.choices,
        db_index=True,
        verbose_name="Kind",
    )
    token_hash = models.CharField(max_length=64, unique=True, verbose_name="Token hash")
    expires_at = models.DateTimeField(db_index=True, verbose_name="Expires at")
    consumed_at = models.DateTimeField(null=True, blank=True, verbose_name="Consumed at")
    attempts = models.PositiveSmallIntegerField(default=0, verbose_name="Failed attempts")
    max_attempts = models.PositiveSmallIntegerField(default=5, verbose_name="Max attempts")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Verification token"
        verbose_name_plural = "Verification tokens"
        indexes = [
            models.Index(fields=["user", "kind"], name="auth_token_user_kind_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.user} / {self.get_kind_display()}"

    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------
    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    @property
    def is_consumed(self) -> bool:
        return self.consumed_at is not None

    @property
    def is_usable(self) -> bool:
        return not self.is_consumed and not self.is_expired and self.attempts < self.max_attempts

    # ------------------------------------------------------------------
    # Transitions (persisted; policy lives in services)
    # ------------------------------------------------------------------
    def consume(self) -> None:
        self.consumed_at = timezone.now()
        self.save(update_fields=["consumed_at", "updated_at"])

    def register_failed_attempt(self) -> bool:
        """Record one wrong code; returns ``True`` when attempts are spent."""
        self.attempts += 1
        self.save(update_fields=["attempts", "updated_at"])
        return self.attempts >= self.max_attempts

    # ------------------------------------------------------------------
    # Factories
    # ------------------------------------------------------------------
    @classmethod
    def hash_token(cls, raw_code: str) -> str:
        return hashlib.sha256(raw_code.encode("utf-8")).hexdigest()

    @classmethod
    def new_code(cls, length: int = 6) -> str:
        """Cryptographically random numeric code (OTP)."""
        return f"{secrets.randbelow(10**length):0{length}d}"

    @classmethod
    def matches(cls, raw_code: str, token_hash: str) -> bool:
        return secrets.compare_digest(cls.hash_token(raw_code), token_hash)
