"""Password history persistence."""

from __future__ import annotations

from django.contrib.auth.hashers import make_password
from django.db.models import QuerySet

from apps.common.repositories.base import BaseRepository

from ..models import PasswordHistory


class PasswordHistoryRepository(BaseRepository[PasswordHistory]):
    model = PasswordHistory

    def recent_for_user(self, user, size: int) -> QuerySet[PasswordHistory]:
        """The ``size`` most recent password entries for ``user``."""
        return self.filter(user=user).order_by("-created_at")[:size]

    def is_used_before(self, user, raw_password: str, size: int) -> bool:
        """Whether ``raw_password`` matches any of the last ``size`` hashes."""
        return any(entry.matches(raw_password) for entry in self.recent_for_user(user, size))

    def record(self, user, raw_password: str) -> PasswordHistory:
        """Persist an encoded copy of the newly set password."""
        return self.create(user=user, password_hash=make_password(raw_password))
