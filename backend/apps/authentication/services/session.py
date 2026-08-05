"""Session service: list and revoke login sessions."""

from __future__ import annotations

from apps.common.exceptions import NotFoundError

from ..models import SecurityEventType, SessionRevokeReason
from ..repositories import LoginSessionRepository, SecurityEventRepository
from ..selectors import sessions_for_user
from .events import record_event


class SessionService:
    """Manage the session ledger for the authenticated user."""

    def __init__(
        self,
        session_repository: LoginSessionRepository | None = None,
        event_repository: SecurityEventRepository | None = None,
    ) -> None:
        self.sessions = session_repository or LoginSessionRepository()
        self.events = event_repository or SecurityEventRepository()

    def list_sessions(self, *, user, include_revoked: bool = False):
        return sessions_for_user(user, include_revoked=include_revoked)

    def revoke_session(self, *, user, session_id, request=None):
        """Revoke one of the user's own sessions (ownership enforced)."""
        session = self.sessions.get_or_none(pk=session_id, user=user)
        if session is None:
            raise NotFoundError("Session not found.")
        self.sessions.revoke(session, reason=SessionRevokeReason.LOGOUT, by=user)
        record_event(
            self.events,
            user=user,
            event_type=SecurityEventType.SESSION_REVOKED,
            session=session,
            request=request,
            details={"action": "revoke_one"},
        )
        return session

    def revoke_all_sessions(self, *, user, request=None) -> int:
        count = self.sessions.revoke_all_for_user(user, reason=SessionRevokeReason.LOGOUT, by=user)
        record_event(
            self.events,
            user=user,
            event_type=SecurityEventType.SESSION_REVOKED,
            request=request,
            details={"action": "revoke_all", "count": count},
        )
        return count
