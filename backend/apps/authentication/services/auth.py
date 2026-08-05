"""Authentication service: login, refresh, logout, verify.

Owns the login lifecycle on top of SimpleJWT:

- login validates credentials, enforces account state (locked / inactive /
  unverified), applies the failed-login lockout policy, issues an access +
  refresh pair, and opens a ``LoginSession`` ledger row keyed by the refresh
  token's JWT id;
- refresh slides the ledger row forward to the rotated refresh token and is
  rejected for any token whose session was revoked (so the ledger is the source
  of truth, with the SimpleJWT blacklist as defense-in-depth);
- logout revokes the session and blacklists the refresh token;
- verify confirms an access token's validity.

Credentials are checked with the same generic error for unknown and known
accounts (constant-time fallback) so the API never enumerates emails.
"""

from __future__ import annotations

import base64
import json
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings as jwt_settings
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.models import User

from ..exceptions import (
    AccountInactiveError,
    AccountLockedError,
    EmailNotVerifiedError,
    InvalidCredentialsError,
    InvalidTokenError,
    TokenRevokedError,
)
from ..models import SessionDeviceType, SessionRevokeReason
from ..repositories import LoginSessionRepository, SecurityEventRepository
from ..utils import client_ip
from .events import record_login_failure, record_login_success, record_token_refreshed


def decode_payload_unverified(raw_token: str) -> dict | None:
    """Decode a JWT's payload without any signature/expiry verification.

    Used only to recover the ``jti`` of an already-expired refresh token at
    logout so the session ledger can be cleaned up. Claim values are never
    trusted for authorization.
    """
    try:
        _, payload_b64, _ = raw_token.split(".")
    except ValueError:
        return None
    try:
        payload_b64 += "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
    except (ValueError, TypeError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


class AuthService:
    """Coordinates authentication flows across repositories and events."""

    def __init__(
        self,
        session_repository: LoginSessionRepository | None = None,
        event_repository: SecurityEventRepository | None = None,
    ) -> None:
        self.sessions = session_repository or LoginSessionRepository()
        self.events = event_repository or SecurityEventRepository()

    # ------------------------------------------------------------------
    # Login
    # ------------------------------------------------------------------
    @transaction.atomic
    def login(
        self,
        *,
        email: str,
        password: str,
        request=None,
        remember_me: bool = False,
        device_name: str = "",
        device_type: str = SessionDeviceType.WEB,
        user_agent: str = "",
    ) -> dict:
        email = (email or "").strip().lower()
        user = User.objects.filter(email=email).first()
        ip_address = client_ip(request)

        if user is None:
            # Equalize timing with a real hash check (no account enumeration).
            self._dummy_password_check(password)
            raise InvalidCredentialsError()

        self._assert_can_login(user, request=request, ip_address=ip_address, user_agent=user_agent)

        if not user.check_password(password):
            locked = user.register_failed_login(settings.AUTH_MAX_LOGIN_ATTEMPTS)
            record_login_failure(
                self.events,
                user=user,
                request=request,
                ip_address=ip_address,
                user_agent=user_agent,
                attempts=user.failed_login_attempts,
            )
            if locked:
                from ..tasks import send_account_locked_notice_task

                send_account_locked_notice_task.delay(str(user.pk))
                raise AccountLockedError()
            raise InvalidCredentialsError()

        self._on_login_success(user)
        tokens = self._issue_tokens(user, remember_me=remember_me)
        session = self.sessions.create_session(
            user=user,
            refresh_token_jti=tokens["refresh_jti"],
            device_name=device_name,
            device_type=device_type,
            ip_address=ip_address,
            user_agent=user_agent,
            remember_me=remember_me,
            expires_at=tokens["expires_at"],
        )
        self._enforce_session_cap(user, keep=session)
        record_login_success(self.events, user=user, request=request, session=session, ip_address=ip_address)

        return {
            "access": tokens["access"],
            "refresh": tokens["refresh"],
            "user": user,
            "session_id": str(session.pk),
            "expires_at": tokens["expires_at"],
        }

    def _assert_can_login(self, user: User, *, request, ip_address, user_agent) -> None:
        if user.is_locked:
            record_login_failure(
                self.events,
                user=user,
                request=request,
                ip_address=ip_address,
                user_agent=user_agent,
                reason="account_locked",
            )
            raise AccountLockedError()
        if user.is_deactivated:
            record_login_failure(
                self.events,
                user=user,
                request=request,
                ip_address=ip_address,
                user_agent=user_agent,
                reason="account_inactive",
            )
            raise AccountInactiveError()
        if settings.AUTH_VERIFY_EMAIL_REQUIRED and not user.email_verified:
            record_login_failure(
                self.events,
                user=user,
                request=request,
                ip_address=ip_address,
                user_agent=user_agent,
                reason="email_not_verified",
            )
            raise EmailNotVerifiedError()

    def _on_login_success(self, user: User) -> None:
        user.reset_failed_logins()
        user.last_login = timezone.now()
        user.save(update_fields=["last_login", "updated_at"])

    def _issue_tokens(self, user: User, *, remember_me: bool) -> dict:
        refresh = RefreshToken.for_user(user)
        lifetime_days = settings.AUTH_REMEMBER_ME_LIFETIME_DAYS if remember_me else settings.AUTH_SESSION_LIFETIME_DAYS
        lifetime = timedelta(days=lifetime_days)
        refresh.set_exp(lifetime=lifetime)

        jti = refresh[jwt_settings.JTI_CLAIM]
        expires_at = timezone.now() + lifetime
        # Keep the blacklist bookkeeping row in sync with the real lifetime.
        OutstandingToken.objects.filter(jti=jti).update(expires_at=expires_at)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "refresh_jti": jti,
            "expires_at": expires_at,
        }

    def _enforce_session_cap(self, user: User, *, keep) -> None:
        max_sessions = settings.AUTH_MAX_ACTIVE_SESSIONS
        active = self.sessions.active_for_user(user).order_by("created_at")
        excess = active.count() - max_sessions
        if excess > 0:
            for stale in active[:excess]:
                self.sessions.revoke(stale, reason=SessionRevokeReason.EXPIRED)

    # ------------------------------------------------------------------
    # Refresh
    # ------------------------------------------------------------------
    @transaction.atomic
    def refresh(self, *, refresh_token: str, request=None) -> dict:
        try:
            old = RefreshToken(refresh_token)
        except TokenError as exc:
            raise InvalidTokenError() from exc

        jti = old[jwt_settings.JTI_CLAIM]
        session = self.sessions.get_active_by_jti(jti)
        if session is None:
            raise TokenRevokedError()

        user = session.user
        if getattr(user, "is_deleted", False) or not user.is_active:
            raise AccountInactiveError()

        # Rotate: blacklist the old token, mint a fresh pair.
        old.blacklist()
        new = RefreshToken.for_user(user)
        if session.remember_me:
            new.set_exp(lifetime=timedelta(days=settings.AUTH_REMEMBER_ME_LIFETIME_DAYS))

        new_jti = new[jwt_settings.JTI_CLAIM]
        self.sessions.update(session, refresh_token_jti=new_jti)
        self.sessions.touch(session)
        record_token_refreshed(self.events, user=user, request=request, session=session)

        return {
            "access": str(new.access_token),
            "refresh": str(new),
            "user": user,
            "session_id": str(session.pk),
            "expires_at": session.expires_at,
        }

    # ------------------------------------------------------------------
    # Logout / verify
    # ------------------------------------------------------------------
    def logout(self, *, refresh_token: str, request=None) -> None:
        """Revoke the session behind ``refresh_token`` (idempotent)."""
        payload = decode_payload_unverified(refresh_token or "")
        if payload is None:
            return
        jti = payload.get(jwt_settings.JTI_CLAIM)
        if not jti:
            return

        session = self.sessions.get_by_jti(jti)
        if session is not None:
            self.sessions.revoke(session, reason=SessionRevokeReason.LOGOUT, by=session.user)
            self.events.record(
                user=session.user,
                event_type="logout",
                session=session,
                request=request,
                details={"reason": "user_logout"},
            )
        else:
            # Unknown token to the ledger: blacklist whatever row exists.
            self.sessions.blacklist_refresh_token(jti)

    def verify_token(self, *, access_token: str) -> bool:
        from rest_framework_simplejwt.tokens import AccessToken

        try:
            AccessToken(access_token)
            return True
        except TokenError:
            return False

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _dummy_password_check(password: str) -> None:
        from django.contrib.auth.hashers import check_password, make_password

        check_password(password, make_password("dummy-account-password"))
