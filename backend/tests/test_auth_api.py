"""API tests for the JWT session lifecycle: login, refresh, verify, logout.

These replace the default SimpleJWT views, so they assert the session ledger
rows, audit events, brute-force lockout and anti-enumeration behaviour.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.core import mail
from django.test import override_settings
from django.utils import timezone

from apps.authentication.models import LoginSession, SecurityEvent
from apps.core.models import User, UserStatus

LOGIN_URL = "/api/v1/auth/token/"


def login(api_client, email, password, **extra):
    payload = {"email": email, "password": password, **extra}
    return api_client.post(LOGIN_URL, payload, format="json")


@pytest.mark.django_db
class TestLogin:
    def test_login_success_returns_tokens_user_and_session(self, api_client, user):
        response = login(api_client, user.email, "TestPass!123")

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["access"]
        assert data["refresh"]
        assert data["user"]["email"] == user.email
        assert data["session_id"]

        session = LoginSession.objects.get(pk=data["session_id"])
        assert session.user_id == user.pk
        assert session.is_active is True
        assert session.device_type == "api"  # no User-Agent sent by the test client

    def test_login_resets_failed_attempts_on_success(self, api_client, user):
        login(api_client, user.email, "wrong-password")
        user.refresh_from_db()
        assert user.failed_login_attempts == 1

        login(api_client, user.email, "TestPass!123")
        user.refresh_from_db()
        assert user.failed_login_attempts == 0

    def test_login_rejects_wrong_password(self, api_client, user):
        response = login(api_client, user.email, "wrong-password")
        assert response.status_code == 401
        assert response.json()["errors"][0]["code"] == "invalid_credentials"

    def test_login_unknown_email_returns_same_error(self, api_client):
        response = login(api_client, "ghost@pharmacloud.test", "TestPass!123")
        assert response.status_code == 401
        assert response.json()["errors"][0]["code"] == "invalid_credentials"

    def test_login_requires_verified_email(self, api_client, db):
        user = User.objects.create_user(
            email="pending@pharmacloud.test",
            password="TestPass!123",
            first_name="Pending",
            status=UserStatus.PENDING_VERIFICATION,
            email_verified=False,
        )
        response = login(api_client, user.email, "TestPass!123")
        assert response.status_code == 403
        assert response.json()["errors"][0]["code"] == "email_not_verified"

    def test_login_inactive_account(self, api_client, user):
        user.deactivate()
        response = login(api_client, user.email, "TestPass!123")
        assert response.status_code == 403
        assert response.json()["errors"][0]["code"] == "account_inactive"

    @override_settings(AUTH_MAX_LOGIN_ATTEMPTS=3)
    def test_login_locks_account_after_max_attempts(self, api_client, user):
        for _ in range(2):
            assert login(api_client, user.email, "wrong-password").status_code == 401

        response = login(api_client, user.email, "wrong-password")
        assert response.status_code == 423
        assert response.json()["errors"][0]["code"] == "account_locked"

        user.refresh_from_db()
        assert user.is_locked is True

        # Even correct credentials are refused while locked.
        assert login(api_client, user.email, "TestPass!123").status_code == 423

    @override_settings(AUTH_MAX_LOGIN_ATTEMPTS=2)
    def test_lockout_sends_notice_email(self, api_client, user):
        login(api_client, user.email, "wrong-password")
        login(api_client, user.email, "wrong-password")

        subjects = [message.subject for message in mail.outbox]
        assert any("locked" in subject for subject in subjects)

    def test_remember_me_session_gets_long_lifetime(self, api_client, user):
        response = login(api_client, user.email, "TestPass!123", remember_me=True)
        session = LoginSession.objects.get(pk=response.json()["data"]["session_id"])
        assert session.remember_me is True
        assert session.expires_at >= timezone.now() + timedelta(days=60)

    def test_login_records_security_events(self, api_client, user):
        login(api_client, user.email, "wrong-password")
        login(api_client, user.email, "TestPass!123")

        events = list(
            SecurityEvent.objects.filter(user=user).order_by("created_at").values_list("event_type", flat=True)
        )
        assert events[-2:] == ["login_failed", "login_success"]


@pytest.mark.django_db
class TestRefresh:
    def test_refresh_rotates_token(self, api_client, user):
        refresh = login(api_client, user.email, "TestPass!123").json()["data"]["refresh"]

        response = api_client.post("/api/v1/auth/token/refresh/", {"refresh": refresh}, format="json")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["access"]
        assert data["refresh"] != refresh

    def test_old_refresh_is_revoked_after_rotation(self, api_client, user):
        refresh = login(api_client, user.email, "TestPass!123").json()["data"]["refresh"]

        api_client.post("/api/v1/auth/token/refresh/", {"refresh": refresh}, format="json")
        again = api_client.post("/api/v1/auth/token/refresh/", {"refresh": refresh}, format="json")
        assert again.status_code == 401
        assert again.json()["errors"][0]["code"] == "token_revoked"

    def test_refresh_rejected_for_revoked_session(self, api_client, user):
        data = login(api_client, user.email, "TestPass!123").json()["data"]
        api_client.post("/api/v1/auth/logout/", {"refresh": data["refresh"]}, format="json")

        response = api_client.post("/api/v1/auth/token/refresh/", {"refresh": data["refresh"]}, format="json")
        assert response.status_code == 401
        assert response.json()["errors"][0]["code"] == "token_revoked"

    def test_refresh_rejects_garbage(self, api_client):
        response = api_client.post("/api/v1/auth/token/refresh/", {"refresh": "not.a.jwt"}, format="json")
        assert response.status_code == 401
        assert response.json()["errors"][0]["code"] == "invalid_token"

    def test_refresh_records_token_refreshed_event(self, api_client, user):
        refresh = login(api_client, user.email, "TestPass!123").json()["data"]["refresh"]
        api_client.post("/api/v1/auth/token/refresh/", {"refresh": refresh}, format="json")

        assert SecurityEvent.objects.filter(user=user, event_type="token_refreshed").exists()


@pytest.mark.django_db
class TestVerify:
    def test_verify_valid_access_token(self, api_client, user):
        access = login(api_client, user.email, "TestPass!123").json()["data"]["access"]
        response = api_client.post("/api/v1/auth/token/verify/", {"token": access}, format="json")
        assert response.status_code == 200

    def test_verify_rejects_garbage(self, api_client):
        response = api_client.post("/api/v1/auth/token/verify/", {"token": "garbage"}, format="json")
        assert response.status_code == 401
        assert response.json()["errors"][0]["code"] == "invalid_token"


@pytest.mark.django_db
class TestLogout:
    def test_logout_revokes_refresh_token(self, api_client, user):
        data = login(api_client, user.email, "TestPass!123").json()["data"]

        response = api_client.post("/api/v1/auth/logout/", {"refresh": data["refresh"]}, format="json")
        assert response.status_code == 200

        again = api_client.post("/api/v1/auth/token/refresh/", {"refresh": data["refresh"]}, format="json")
        assert again.status_code == 401
        assert again.json()["errors"][0]["code"] == "token_revoked"

    def test_logout_is_idempotent(self, api_client, user):
        refresh = login(api_client, user.email, "TestPass!123").json()["data"]["refresh"]
        assert api_client.post("/api/v1/auth/logout/", {"refresh": refresh}, format="json").status_code == 200
        assert api_client.post("/api/v1/auth/logout/", {"refresh": refresh}, format="json").status_code == 200

    def test_logout_with_garbage_token_is_safe(self, api_client):
        response = api_client.post("/api/v1/auth/logout/", {"refresh": "garbage"}, format="json")
        assert response.status_code == 200

    def test_logout_records_event_and_revokes_ledger(self, api_client, user):
        data = login(api_client, user.email, "TestPass!123").json()["data"]
        api_client.post("/api/v1/auth/logout/", {"refresh": data["refresh"]}, format="json")

        session = LoginSession.objects.get(pk=data["session_id"])
        assert session.is_active is False
        assert SecurityEvent.objects.filter(user=user, event_type="logout").exists()
