"""Login session persistence."""

from __future__ import annotations

from django.db.models import QuerySet
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from apps.common.repositories.base import BaseRepository

from ..models import LoginSession, SessionDeviceType, SessionRevokeReason


class LoginSessionRepository(BaseRepository[LoginSession]):
    model = LoginSession

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------
    def active_for_user(self, user) -> QuerySet[LoginSession]:
        return self.filter(user=user, is_active=True)

    def get_by_jti(self, jti: str) -> LoginSession | None:
        return self.get_or_none(refresh_token_jti=jti)

    def get_active_by_jti(self, jti: str) -> LoginSession | None:
        return self.filter(refresh_token_jti=jti, is_active=True).select_related("user").first()

    # ------------------------------------------------------------------
    # Token blacklisting (defense-in-depth alongside the session ledger)
    # ------------------------------------------------------------------
    def blacklist_refresh_token(self, jti: str) -> bool:
        """Blacklist a refresh token by its JWT id.

        ``RefreshToken.for_user`` pre-registers an ``OutstandingToken`` for
        every token we issue, so revocation does not require the raw token.
        Returns ``True`` when the token was blacklisted.
        """
        outstanding = OutstandingToken.objects.filter(jti=jti).first()
        if outstanding is None:
            return False
        BlacklistedToken.objects.get_or_create(token=outstanding)
        return True

    def blacklist_refresh_tokens(self, jtis: list[str]) -> int:
        blacklisted = 0
        for jti in jtis:
            if self.blacklist_refresh_token(jti):
                blacklisted += 1
        return blacklisted

    # ------------------------------------------------------------------
    # Writing
    # ------------------------------------------------------------------
    def create_session(
        self,
        *,
        user,
        refresh_token_jti: str,
        device_name: str = "",
        device_type: str = SessionDeviceType.WEB,
        ip_address: str | None = None,
        user_agent: str = "",
        remember_me: bool = False,
        expires_at=None,
    ) -> LoginSession:
        return self.create(
            user=user,
            refresh_token_jti=refresh_token_jti,
            device_name=device_name,
            device_type=device_type,
            ip_address=ip_address,
            user_agent=user_agent,
            remember_me=remember_me,
            expires_at=expires_at,
        )

    def touch(self, session: LoginSession) -> None:
        session.touch()

    def revoke(
        self,
        session: LoginSession,
        *,
        reason: str = SessionRevokeReason.LOGOUT,
        by=None,
    ) -> None:
        session.revoke(reason=reason, by=by)
        self.blacklist_refresh_token(session.refresh_token_jti)

    def revoke_all_for_user(self, user, *, reason: str = SessionRevokeReason.SECURITY, by=None) -> int:
        """Revoke and blacklist every live session for ``user``.

        Returns the number of sessions revoked.
        """
        sessions = list(self.active_for_user(user))
        for session in sessions:
            session.revoke(reason=reason, by=by)
        jtis = [session.refresh_token_jti for session in sessions]
        self.blacklist_refresh_tokens(jtis)
        return len(sessions)
