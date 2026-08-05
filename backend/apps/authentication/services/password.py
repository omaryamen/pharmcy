"""Password service: authenticated password change with reuse prevention."""

from __future__ import annotations

from django.conf import settings
from django.db import transaction

from apps.core.models import User

from ..exceptions import IncorrectCurrentPasswordError, PasswordReuseError
from ..models import SecurityEventType, SessionRevokeReason
from ..repositories import LoginSessionRepository, PasswordHistoryRepository, SecurityEventRepository
from ..validators import validate_password_strength
from .events import record_event


class PasswordService:
    """Change an authenticated user's password.

    Enforces the current-password check, Django's strength validators, the
    password-history reuse window, and revokes every live session afterwards so
    other devices must re-authenticate.
    """

    def __init__(
        self,
        password_repository: PasswordHistoryRepository | None = None,
        session_repository: LoginSessionRepository | None = None,
        event_repository: SecurityEventRepository | None = None,
    ) -> None:
        self.passwords = password_repository or PasswordHistoryRepository()
        self.sessions = session_repository or LoginSessionRepository()
        self.events = event_repository or SecurityEventRepository()

    @transaction.atomic
    def change_password(
        self,
        *,
        user: User,
        current_password: str,
        new_password: str,
        request=None,
    ) -> User:
        if not user.check_password(current_password):
            raise IncorrectCurrentPasswordError()

        validate_password_strength(new_password, user=user)
        if self.passwords.is_used_before(user, new_password, settings.AUTH_PASSWORD_HISTORY_SIZE):
            raise PasswordReuseError()

        user.set_password(new_password)
        user.save(update_fields=["password", "password_changed_at", "updated_at"])
        self.passwords.record(user, new_password)
        self._trim_history(user)

        self.sessions.revoke_all_for_user(user, reason=SessionRevokeReason.PASSWORD_CHANGE, by=user)
        record_event(self.events, user=user, event_type=SecurityEventType.PASSWORD_CHANGED, request=request)
        return user

    def _trim_history(self, user: User) -> None:
        """Keep at most ``AUTH_PASSWORD_HISTORY_SIZE`` hashes per user."""
        keep = settings.AUTH_PASSWORD_HISTORY_SIZE
        excess = list(self.passwords.filter(user=user).order_by("-created_at")[keep:])
        for entry in excess:
            self.passwords.delete(entry)
