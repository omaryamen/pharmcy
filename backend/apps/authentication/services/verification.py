"""Verification service: email/phone verification and password reset.

Verification codes are generated, delivered (email/SMS), stored hashed and
single-use. One usable code per user+kind is enforced — requesting a new code
consumes all previous ones.
"""

from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.core.models import User, UserStatus

from ..exceptions import (
    InvalidVerificationCodeError,
    PasswordReuseError,
    TooManyVerificationAttemptsError,
)
from ..models import SecurityEventType, VerificationToken, VerificationTokenKind
from ..repositories import (
    LoginSessionRepository,
    PasswordHistoryRepository,
    SecurityEventRepository,
    VerificationTokenRepository,
)
from ..tasks import (
    send_password_reset_code_email_task,
    send_phone_verification_code_task,
    send_verification_code_email_task,
)
from ..validators import validate_password_strength
from .events import record_event


def issue_verification_code(
    repository: VerificationTokenRepository,
    user: User,
    kind: VerificationTokenKind,
    *,
    request=None,
) -> VerificationToken:
    """Generate, persist and deliver a fresh verification code.

    Previous usable codes for the same user+kind are consumed so only the most
    recent code is ever valid.
    """
    code = VerificationToken.new_code(settings.AUTH_VERIFICATION_CODE_LENGTH)
    expires_at = timezone.now() + timedelta(minutes=settings.AUTH_VERIFICATION_CODE_LIFETIME_MINUTES)
    token = repository.create_token(
        user=user,
        kind=kind,
        raw_code=code,
        expires_at=expires_at,
        max_attempts=settings.AUTH_VERIFICATION_MAX_ATTEMPTS,
    )
    repository.invalidate_previous(user, kind, keep=token)

    if kind == VerificationTokenKind.EMAIL_VERIFICATION:
        send_verification_code_email_task.delay(str(user.pk), code)
    elif kind == VerificationTokenKind.PASSWORD_RESET:
        send_password_reset_code_email_task.delay(str(user.pk), code)
    elif kind == VerificationTokenKind.PHONE_VERIFICATION:
        send_phone_verification_code_task.delay(str(user.pk), code)
    return token


class VerificationService:
    """Email/phone verification and password-reset use cases."""

    def __init__(
        self,
        verification_repository: VerificationTokenRepository | None = None,
        password_repository: PasswordHistoryRepository | None = None,
        session_repository: LoginSessionRepository | None = None,
        event_repository: SecurityEventRepository | None = None,
    ) -> None:
        self.verifications = verification_repository or VerificationTokenRepository()
        self.passwords = password_repository or PasswordHistoryRepository()
        self.sessions = session_repository or LoginSessionRepository()
        self.events = event_repository or SecurityEventRepository()

    # ------------------------------------------------------------------
    # Email verification
    # ------------------------------------------------------------------
    @transaction.atomic
    def request_email_verification(self, *, user: User, request=None) -> VerificationToken:
        issue_verification_code(self.verifications, user, VerificationTokenKind.EMAIL_VERIFICATION, request=request)
        record_event(
            self.events,
            user=user,
            event_type=SecurityEventType.EMAIL_VERIFICATION_REQUESTED,
            request=request,
        )
        return self.verifications.latest_for_user_and_kind(user, VerificationTokenKind.EMAIL_VERIFICATION)

    @transaction.atomic
    def verify_email(self, *, user: User, code: str, request=None) -> User:
        if user.email_verified:
            return user  # idempotent

        token = self.verifications.usable_latest(user, VerificationTokenKind.EMAIL_VERIFICATION)
        self._assert_usable_token(token, code)

        self.verifications.consume(token)
        user.email_verified = True
        if user.is_pending_verification:
            user.status = UserStatus.ACTIVE
        user.save(update_fields=["email_verified", "status", "is_active", "updated_at"])
        record_event(self.events, user=user, event_type=SecurityEventType.EMAIL_VERIFIED, request=request)
        return user

    # ------------------------------------------------------------------
    # Phone verification
    # ------------------------------------------------------------------
    @transaction.atomic
    def request_phone_verification(self, *, user: User, request=None) -> VerificationToken:
        if not user.phone:
            from apps.common.exceptions import ValidationFailedError

            raise ValidationFailedError("A phone number is required.", code="phone_required", field="phone")
        issue_verification_code(self.verifications, user, VerificationTokenKind.PHONE_VERIFICATION, request=request)
        record_event(
            self.events,
            user=user,
            event_type=SecurityEventType.PHONE_VERIFICATION_REQUESTED,
            request=request,
        )
        return self.verifications.latest_for_user_and_kind(user, VerificationTokenKind.PHONE_VERIFICATION)

    @transaction.atomic
    def verify_phone(self, *, user: User, code: str, request=None) -> User:
        if user.phone_verified:
            return user  # idempotent

        token = self.verifications.usable_latest(user, VerificationTokenKind.PHONE_VERIFICATION)
        self._assert_usable_token(token, code)

        self.verifications.consume(token)
        user.phone_verified = True
        user.save(update_fields=["phone_verified", "updated_at"])
        record_event(self.events, user=user, event_type=SecurityEventType.PHONE_VERIFIED, request=request)
        return user

    # ------------------------------------------------------------------
    # Password reset (anonymous)
    # ------------------------------------------------------------------
    @transaction.atomic
    def request_password_reset(self, *, email: str, request=None) -> bool:
        """Issue a reset code. Returns whether an account was found; callers
        must present the same response either way to avoid user enumeration."""
        user = User.objects.filter(email=(email or "").strip().lower()).first()
        if user is None:
            return False
        issue_verification_code(self.verifications, user, VerificationTokenKind.PASSWORD_RESET, request=request)
        record_event(self.events, user=user, event_type=SecurityEventType.PASSWORD_RESET_REQUESTED, request=request)
        return True

    @transaction.atomic
    def reset_password(
        self,
        *,
        email: str,
        code: str,
        new_password: str,
        request=None,
    ) -> User:
        email = (email or "").strip().lower()
        user = User.objects.filter(email=email).first()
        token = (
            self.verifications.usable_latest(user, VerificationTokenKind.PASSWORD_RESET) if user is not None else None
        )
        # Same error for "unknown email" and "bad code" — never enumerate.
        self._assert_usable_token(token, code)

        validate_password_strength(new_password, user=user)
        if self.passwords.is_used_before(user, new_password, settings.AUTH_PASSWORD_HISTORY_SIZE):
            raise PasswordReuseError()

        self.verifications.consume(token)
        user.set_password(new_password)
        if user.is_locked:
            user.status = UserStatus.ACTIVE
            user.failed_login_attempts = 0
            user.save(
                update_fields=[
                    "password",
                    "password_changed_at",
                    "status",
                    "failed_login_attempts",
                    "is_active",
                    "updated_at",
                ]
            )
        else:
            user.save(update_fields=["password", "password_changed_at", "updated_at"])

        self.passwords.record(user, new_password)
        self.sessions.revoke_all_for_user(user, reason="password_change", by=user)
        record_event(self.events, user=user, event_type=SecurityEventType.PASSWORD_RESET_CONFIRMED, request=request)
        return user

    # ------------------------------------------------------------------
    # Shared code verification
    # ------------------------------------------------------------------
    def _assert_usable_token(self, token: VerificationToken | None, code: str) -> None:
        if token is None:
            raise InvalidVerificationCodeError()
        if not VerificationToken.matches(code, token.token_hash):
            spent = self.verifications.register_failed_attempt(token)
            if spent:
                raise TooManyVerificationAttemptsError()
            raise InvalidVerificationCodeError()
