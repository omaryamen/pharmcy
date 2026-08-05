"""Session read queries."""

from __future__ import annotations

from django.db.models import QuerySet

from ..models import LoginSession


def sessions_for_user(user, *, include_revoked: bool = False) -> QuerySet[LoginSession]:
    """All sessions for ``user``, most recent first."""
    queryset = LoginSession.objects.filter(user=user)
    if not include_revoked:
        queryset = queryset.filter(is_active=True)
    return queryset.order_by("-created_at")


def active_session_count(user) -> int:
    return LoginSession.objects.filter(user=user, is_active=True).count()
