"""API tests for registration, email/phone verification and password reset."""

from __future__ import annotations

import pytest
from django.core import mail
from django.test import override_settings

from apps.authentication.models import PasswordHistory, SecurityEvent
from apps.core.models import User, UserStatus
from tests.helpers import extract_otp, get_email, register_and_extract_code

REGISTER_URL = "/api/v1/auth/register/"
VERIFY_URL = "/api/v1/auth/email/verify/confirm/"


@pytest.mark.django_db
class TestRegistration:
    def test_register_creates_pending_user_and_sends_code(self, api_client):
        response = api_client.post(
            REGISTER_URL,
            {
                "email": "new.user@pharmacloud.test",
                "first_name": "New",
                "last_name": "User",
                "password": "StrongPass!123",
            },
            format="json",
        )

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["verification_sent"] is True
        assert data["user"]["email"] == "new.user@pharmacloud.test"

        user = User.objects.get(email="new.user@pharmacloud.test")
        assert user.status == UserStatus.PENDING_VERIFICATION
        assert user.email_verified is False
        assert user.is_active is False

        message = get_email(user.email)
        assert "verification" in message.subject.lower()
        assert extract_otp(message).isdigit()

        assert SecurityEvent.objects.filter(user=user, event_type="registered").exists()
        assert PasswordHistory.objects.filter(user=user).count() == 1

    def test_register_without_verification_requirement_activates(self, api_client):
        with override_settings(AUTH_VERIFY_EMAIL_REQUIRED=False):
            response = api_client.post(
                REGISTER_URL,
                {"email": "fast@pharmacloud.test", "first_name": "Fast", "password": "StrongPass!123"},
                format="json",
            )

        assert response.status_code == 201
        assert response.json()["data"]["verification_sent"] is False
        user = User.objects.get(email="fast@pharmacloud.test")
        assert user.status == UserStatus.ACTIVE
        assert user.email_verified is True

    def test_register_duplicate_email_conflict(self, api_client, user):
        response = api_client.post(
            REGISTER_URL,
            {"email": user.email, "first_name": "Dup", "password": "StrongPass!123"},
            format="json",
        )
        assert response.status_code == 409
        assert response.json()["errors"][0]["code"] == "email_taken"

    def test_register_email_conflict_is_case_insensitive(self, api_client, user):
        response = api_client.post(
            REGISTER_URL,
            {"email": user.email.upper(), "first_name": "Dup", "password": "StrongPass!123"},
            format="json",
        )
        assert response.status_code == 409

    def test_register_rejects_weak_password(self, api_client):
        response = api_client.post(
            REGISTER_URL,
            {"email": "weak@pharmacloud.test", "first_name": "Weak", "password": "short"},
            format="json",
        )
        assert response.status_code == 422
        assert response.json()["errors"][0]["code"] == "weak_password"

    def test_register_missing_fields(self, api_client):
        response = api_client.post(REGISTER_URL, {}, format="json")
        assert response.status_code == 400


@pytest.mark.django_db
class TestEmailVerification:
    def test_verify_email_unlocks_account(self, api_client):
        code = register_and_extract_code(api_client, email="verify@pharmacloud.test")

        response = api_client.post(
            VERIFY_URL,
            {"email": "verify@pharmacloud.test", "code": code},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["data"]["email_verified"] is True

        user = User.objects.get(email="verify@pharmacloud.test")
        assert user.status == UserStatus.ACTIVE
        assert user.email_verified is True

        # Now the account can log in.
        login_response = api_client.post(
            "/api/v1/auth/token/",
            {"email": "verify@pharmacloud.test", "password": "StrongPass!123"},
            format="json",
        )
        assert login_response.status_code == 200

    def test_verify_email_wrong_code(self, api_client):
        register_and_extract_code(api_client, email="wrong@pharmacloud.test")

        response = api_client.post(
            VERIFY_URL,
            {"email": "wrong@pharmacloud.test", "code": "000000"},
            format="json",
        )
        assert response.status_code == 400
        assert response.json()["errors"][0]["code"] == "invalid_verification_code"

    @override_settings(AUTH_VERIFICATION_MAX_ATTEMPTS=3)
    def test_verify_email_exhausts_attempts(self, api_client):
        register_and_extract_code(api_client, email="burst@pharmacloud.test")

        for _ in range(2):
            assert (
                api_client.post(
                    VERIFY_URL,
                    {"email": "burst@pharmacloud.test", "code": "000000"},
                    format="json",
                ).status_code
                == 400
            )

        last = api_client.post(
            VERIFY_URL,
            {"email": "burst@pharmacloud.test", "code": "000000"},
            format="json",
        )
        assert last.status_code == 429
        assert last.json()["errors"][0]["code"] == "too_many_verification_attempts"

    def test_resend_invalidates_previous_code(self, api_client):
        first = register_and_extract_code(api_client, email="resend@pharmacloud.test")

        response = api_client.post(
            "/api/v1/auth/email/verify/request/",
            {"email": "resend@pharmacloud.test"},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["data"]["sent"] is True

        second = extract_otp(get_email("resend@pharmacloud.test"))
        assert second != first

        assert (
            api_client.post(
                VERIFY_URL,
                {"email": "resend@pharmacloud.test", "code": first},
                format="json",
            ).status_code
            == 400
        )

        ok = api_client.post(
            VERIFY_URL,
            {"email": "resend@pharmacloud.test", "code": second},
            format="json",
        )
        assert ok.status_code == 200

    def test_verify_unknown_email(self, api_client):
        response = api_client.post(
            VERIFY_URL,
            {"email": "ghost@pharmacloud.test", "code": "123456"},
            format="json",
        )
        assert response.status_code == 400
        assert response.json()["errors"][0]["code"] == "invalid_verification_code"

    def test_resend_unknown_email_no_error(self, api_client):
        response = api_client.post(
            "/api/v1/auth/email/verify/request/",
            {"email": "ghost@pharmacloud.test"},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["data"]["sent"] is False
        assert not mail.outbox

    def test_verify_already_verified_email_conflict_on_resend(self, api_client, user):
        response = api_client.post(
            "/api/v1/auth/email/verify/request/",
            {"email": user.email},
            format="json",
        )
        assert response.status_code == 409
        assert response.json()["errors"][0]["code"] == "email_already_verified"

    def test_code_must_be_six_digits(self, api_client):
        register_and_extract_code(api_client, email="fmt@pharmacloud.test")

        response = api_client.post(
            VERIFY_URL,
            {"email": "fmt@pharmacloud.test", "code": "12345"},
            format="json",
        )
        assert response.status_code == 422
        assert response.json()["errors"][0]["code"] == "invalid_verification_code_format"


@pytest.mark.django_db
class TestPhoneVerification:
    def test_phone_verification_flow(self, authenticated_client, user):
        response = authenticated_client.post("/api/v1/auth/phone/verify/request/", {}, format="json")
        assert response.status_code == 200
        assert response.json()["data"]["sent"] is True

        code = extract_otp(get_email(user.email))
        confirm = authenticated_client.post(
            "/api/v1/auth/phone/verify/confirm/",
            {"code": code},
            format="json",
        )
        assert confirm.status_code == 200
        assert confirm.json()["data"]["phone_verified"] is True

        user.refresh_from_db()
        assert user.phone_verified is True

    def test_phone_verification_requires_phone(self, authenticated_client, user):
        user.phone = ""
        user.save()

        response = authenticated_client.post("/api/v1/auth/phone/verify/request/", {}, format="json")
        assert response.status_code == 422
        assert response.json()["errors"][0]["code"] == "phone_required"

    def test_phone_verification_requires_auth(self, api_client):
        response = api_client.post("/api/v1/auth/phone/verify/request/", {}, format="json")
        assert response.status_code == 401


@pytest.mark.django_db
class TestPasswordReset:
    def test_reset_request_sends_code(self, api_client, user):
        response = api_client.post(
            "/api/v1/auth/password/reset/request/",
            {"email": user.email},
            format="json",
        )
        assert response.status_code == 200

        message = get_email(user.email)
        assert "reset" in message.subject.lower()
        assert extract_otp(message)
        assert SecurityEvent.objects.filter(user=user, event_type="password_reset_requested").exists()

    def test_reset_request_unknown_email_returns_same_message(self, api_client):
        response = api_client.post(
            "/api/v1/auth/password/reset/request/",
            {"email": "ghost@pharmacloud.test"},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["data"]["message"] == "If the email is registered, a reset code has been sent."
        assert not mail.outbox

    def test_reset_confirm_changes_password(self, api_client, user):
        api_client.post(
            "/api/v1/auth/password/reset/request/",
            {"email": user.email},
            format="json",
        )
        code = extract_otp(get_email(user.email))

        response = api_client.post(
            "/api/v1/auth/password/reset/confirm/",
            {"email": user.email, "code": code, "new_password": "FreshPass!456"},
            format="json",
        )
        assert response.status_code == 200

        user.refresh_from_db()
        assert user.check_password("FreshPass!456") is True
        assert user.check_password("TestPass!123") is False
        assert PasswordHistory.objects.filter(user=user).count() == 1

    def test_reset_confirm_wrong_code(self, api_client, user):
        api_client.post("/api/v1/auth/password/reset/request/", {"email": user.email}, format="json")

        response = api_client.post(
            "/api/v1/auth/password/reset/confirm/",
            {"email": user.email, "code": "000000", "new_password": "FreshPass!456"},
            format="json",
        )
        assert response.status_code == 400
        assert response.json()["errors"][0]["code"] == "invalid_verification_code"

    def test_reset_unlocks_locked_account(self, api_client, user):
        user.lock_account()
        api_client.post("/api/v1/auth/password/reset/request/", {"email": user.email}, format="json")
        code = extract_otp(get_email(user.email))

        response = api_client.post(
            "/api/v1/auth/password/reset/confirm/",
            {"email": user.email, "code": code, "new_password": "FreshPass!456"},
            format="json",
        )
        assert response.status_code == 200

        user.refresh_from_db()
        assert user.is_active is True
        assert user.failed_login_attempts == 0

        assert (
            api_client.post(
                "/api/v1/auth/token/",
                {"email": user.email, "password": "FreshPass!456"},
                format="json",
            ).status_code
            == 200
        )

    def test_reset_confirm_unknown_email_same_error(self, api_client):
        response = api_client.post(
            "/api/v1/auth/password/reset/confirm/",
            {"email": "ghost@pharmacloud.test", "code": "123456", "new_password": "FreshPass!456"},
            format="json",
        )
        assert response.status_code == 400
        assert response.json()["errors"][0]["code"] == "invalid_verification_code"
