"""Thin event-recording helpers shared by services.

Keeps the audit-trail vocabulary in one place so services never inline raw
event strings and never repeat request-metadata plumbing.
"""

from __future__ import annotations

from ..models import SecurityEventType
from ..repositories import SecurityEventRepository


def record_login_success(repo: SecurityEventRepository, *, user, request=None, session=None, ip_address=None) -> None:
    repo.record(
        user=user,
        event_type=SecurityEventType.LOGIN_SUCCESS,
        request=request,
        session=session,
        ip_address=ip_address,
    )


def record_login_failure(
    repo: SecurityEventRepository,
    *,
    user,
    request=None,
    ip_address=None,
    user_agent=None,
    attempts: int | None = None,
    reason: str | None = None,
) -> None:
    details = {}
    if attempts is not None:
        details["attempts"] = attempts
    if reason is not None:
        details["reason"] = reason
    repo.record(
        user=user,
        event_type=SecurityEventType.LOGIN_FAILED,
        request=request,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details,
    )


def record_token_refreshed(repo: SecurityEventRepository, *, user, request=None, session=None) -> None:
    repo.record(
        user=user,
        event_type=SecurityEventType.TOKEN_REFRESHED,
        request=request,
        session=session,
    )


def record_event(repo: SecurityEventRepository, *, user, event_type, request=None, session=None, details=None) -> None:
    repo.record(
        user=user,
        event_type=event_type,
        request=request,
        session=session,
        details=details,
    )
