"""Authentication model unit tests."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.authentication.models import (
    LoginSession,
    PasswordHistory,
    SecurityEvent,
    SecurityEventType,
    SessionRevokeReason,
    VerificationToken,
    VerificationTokenKind,
)
from apps.authentication.repositories import LoginSessionRepository
from apps.core.models import User


@pytest.mark.django_db
class TestLoginSession:
    def test_create_and_touch(self, user):
        session = LoginSession.objects.create(
            user=user,
            refresh_token_jti="jti-1",
            device_name="Chrome",
            device_type="web",
            expires_at=timezone.now() + timedelta(days=30),
        )
        assert session.is_active is True
        assert session.is_expired is False

        session.touch()
        session.refresh_from_db()
        assert session.last_used_at is not None

    def test_revoke_is_idempotent(self, user):
        session = LoginSession.objects.create(user=user, refresh_token_jti="jti-2")
        session.revoke(reason=SessionRevokeReason.LOGOUT)
        first_revoked_at = session.revoked_at

        session.revoke(reason=SessionRevokeReason.LOGOUT)
        session.refresh_from_db()
        assert session.is_active is False
        assert session.revoked_at == first_revoked_at

    def test_is_expired(self, user):
        session = LoginSession.objects.create(
            user=user,
            refresh_token_jti="jti-3",
            expires_at=timezone.now() - timedelta(minutes=1),
        )
        assert session.is_expired is True

    def test_repository_blacklists_refresh_token(self, user):
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)
        session = LoginSession.objects.create(user=user, refresh_token_jti=refresh["jti"])

        repo = LoginSessionRepository()
        assert repo.blacklist_refresh_token(refresh["jti"]) is True
        assert repo.blacklist_refresh_token(refresh["jti"]) is False  # already blacklisted

        from rest_framework_simplejwt.exceptions import TokenError

        with pytest.raises(TokenError):
            RefreshToken(str(refresh))

        assert session.is_active is True  # ledger row unaffected by pure blacklist


@pytest.mark.django_db
class TestVerificationToken:
    def test_hash_is_one_way_and_matches(self):
        digest = VerificationToken.hash_token("123456")
        assert digest != "123456"
        assert len(digest) == 64
        assert VerificationToken.matches("123456", digest) is True
        assert VerificationToken.matches("000000", digest) is False

    def test_new_code_is_numeric(self):
        assert VerificationToken.new_code(6).isdigit()
        assert len(VerificationToken.new_code(6)) == 6

    def test_consume_and_usable(self, user):
        token = VerificationToken.objects.create(
            user=user,
            kind=VerificationTokenKind.EMAIL_VERIFICATION,
            token_hash=VerificationToken.hash_token("111111"),
            expires_at=timezone.now() + timedelta(minutes=10),
        )
        assert token.is_usable is True
        token.consume()
        token.refresh_from_db()
        assert token.is_consumed is True
        assert token.is_usable is False

    def test_attempt_budget(self, user):
        token = VerificationToken.objects.create(
            user=user,
            kind=VerificationTokenKind.EMAIL_VERIFICATION,
            token_hash=VerificationToken.hash_token("111111"),
            expires_at=timezone.now() + timedelta(minutes=10),
            max_attempts=3,
        )
        assert token.register_failed_attempt() is False
        assert token.register_failed_attempt() is False
        assert token.register_failed_attempt() is True
        assert token.is_usable is False

    def test_expired_token_is_not_usable(self, user):
        token = VerificationToken.objects.create(
            user=user,
            kind=VerificationTokenKind.EMAIL_VERIFICATION,
            token_hash=VerificationToken.hash_token("111111"),
            expires_at=timezone.now() - timedelta(minutes=1),
        )
        assert token.is_expired is True
        assert token.is_usable is False


@pytest.mark.django_db
class TestPasswordHistory:
    def test_matches(self, user):
        from django.contrib.auth.hashers import make_password

        entry = PasswordHistory.objects.create(
            user=user,
            password_hash=make_password("OldPass!123"),
        )
        assert entry.matches("OldPass!123") is True
        assert entry.matches("OtherPass!123") is False


@pytest.mark.django_db
class TestSecurityEvent:
    def test_record_with_request_context(self, user, api_client):
        event = SecurityEvent.record(
            user=user,
            event_type=SecurityEventType.LOGIN_SUCCESS,
            request=api_client.post("/").wsgi_request,
            details={"attempts": 1},
        )
        assert event.event_type == "login_success"
        assert event.details == {"attempts": 1}
        assert event.pk is not None

    def test_record_survives_soft_delete(self, user):
        event = SecurityEvent.record(user=user, event_type=SecurityEventType.LOGIN_FAILED)
        user.delete()
        event.refresh_from_db()
        assert event.user_id == user.pk  # SET_NULL would only fire on hard delete
