"""Verification token persistence."""

from __future__ import annotations

from datetime import timedelta

from django.db.models import QuerySet
from django.utils import timezone

from apps.common.repositories.base import BaseRepository

from ..models import VerificationToken, VerificationTokenKind


class VerificationTokenRepository(BaseRepository[VerificationToken]):
    model = VerificationToken

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------
    def for_user_and_kind(self, user, kind: VerificationTokenKind) -> QuerySet[VerificationToken]:
        return self.filter(user=user, kind=kind)

    def latest_for_user_and_kind(self, user, kind: VerificationTokenKind) -> VerificationToken | None:
        return self.for_user_and_kind(user, kind).order_by("-created_at").first()

    def get_by_hash(self, token_hash: str) -> VerificationToken | None:
        return self.get_or_none(token_hash=token_hash)

    def usable_latest(self, user, kind: VerificationTokenKind) -> VerificationToken | None:
        """Most recent token for ``user``+``kind`` that is still usable."""
        for token in self.for_user_and_kind(user, kind).order_by("-created_at")[:5]:
            if token.is_usable:
                return token
        return None

    # ------------------------------------------------------------------
    # Writing
    # ------------------------------------------------------------------
    def create_token(
        self,
        *,
        user,
        kind: VerificationTokenKind,
        raw_code: str,
        expires_at,
        max_attempts: int = 5,
    ) -> VerificationToken:
        return self.create(
            user=user,
            kind=kind,
            token_hash=VerificationToken.hash_token(raw_code),
            expires_at=expires_at,
            max_attempts=max_attempts,
        )

    def consume(self, token: VerificationToken) -> None:
        token.consume()

    def register_failed_attempt(self, token: VerificationToken) -> bool:
        """Record a wrong code; ``True`` once the attempt budget is spent."""
        return token.register_failed_attempt()

    def invalidate_previous(self, user, kind: VerificationTokenKind, keep: VerificationToken) -> int:
        """Consume all earlier outstanding tokens of the same kind.

        Keeps ``keep`` (the fresh token) usable; returns the number consumed.
        """
        earlier = self.filter(user=user, kind=kind, consumed_at__isnull=True).exclude(pk=keep.pk)
        count = earlier.count()
        now = timezone.now()
        earlier.update(consumed_at=now, updated_at=now)
        return count

    def purge_expired(self, max_age: timedelta | None = None) -> int:
        """Delete expired tokens (and any older than ``max_age``)."""
        queryset = self.filter(expires_at__lte=timezone.now())
        if max_age is not None:
            queryset = queryset | self.filter(created_at__lte=timezone.now() - max_age)
        deleted, _ = queryset.delete()
        return deleted
