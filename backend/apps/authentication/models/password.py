"""Password reuse prevention.

Keeps a rolling window of the most recent password hashes per user so password
changes can reject hashes already used within the configured history size.
"""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.db import models

from apps.common.models import UUIDTimeStampedModel


class PasswordHistory(UUIDTimeStampedModel):
    """One entry per password the user has set (most recent first)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_history",
        verbose_name="User",
    )
    password_hash = models.CharField(max_length=255, verbose_name="Password hash")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Password history entry"
        verbose_name_plural = "Password history"
        indexes = [
            models.Index(fields=["user", "-created_at"], name="auth_password_user_created_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.user} / {self.created_at:%Y-%m-%d %H:%M}"

    def matches(self, raw_password: str) -> bool:
        """Whether ``raw_password`` verifies against this stored hash."""
        return check_password(raw_password, self.password_hash)
