"""API tests for the authenticated password change flow."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from apps.authentication.models import LoginSession, SecurityEvent
from apps.core.models import User, UserStatus
from tests.helpers import register_and_extract_code


@pytest.mark.django_db
class TestChangePassword:
    def _client_for(self, user) -> APIClient:
        from rest_framework_simplejwt.tokens import RefreshToken

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(user).access_token}")
        return client

    def test_change_password_wrong_current(self, user):
        client = self._client_for(user)

        response = client.post(
            "/api/v1/auth/password/change/",
            {"current_password": "not-the-password", "new_password": "FreshPass!456"},
            format="json",
        )
        assert response.status_code == 400
        assert response.json()["errors"][0]["code"] == "incorrect_current_password"
        assert response.json()["errors"][0]["field"] == "current_password"

    def test_change_password_success_revokes_all_sessions(self, api_client, user):
        # Open a real ledger session via the API.
        data = api_client.post(
            "/api/v1/auth/token/",
            {"email": user.email, "password": "TestPass!123"},
            format="json",
        ).json()["data"]

        client = self._client_for(user)
        response = client.post(
            "/api/v1/auth/password/change/",
            {"current_password": "TestPass!123", "new_password": "FreshPass!456"},
            format="json",
        )
        assert response.status_code == 200

        session = LoginSession.objects.get(pk=data["session_id"])
        assert session.is_active is False

        # The old refresh token can no longer be used.
        refreshed = api_client.post(
            "/api/v1/auth/token/refresh/",
            {"refresh": data["refresh"]},
            format="json",
        )
        assert refreshed.status_code == 401

        user.refresh_from_db()
        assert user.check_password("FreshPass!456") is True
        assert SecurityEvent.objects.filter(user=user, event_type="password_changed").exists()

        # New credentials work.
        assert (
            api_client.post(
                "/api/v1/auth/token/",
                {"email": user.email, "password": "FreshPass!456"},
                format="json",
            ).status_code
            == 200
        )

    def test_change_password_rejects_history_reuse(self, api_client):
        register_and_extract_code(api_client, email="reuse@pharmacloud.test")
        user = User.objects.get(email="reuse@pharmacloud.test")
        user.email_verified = True
        user.status = UserStatus.ACTIVE
        user.save()
        client = self._client_for(user)

        response = client.post(
            "/api/v1/auth/password/change/",
            {"current_password": "StrongPass!123", "new_password": "StrongPass!123"},
            format="json",
        )
        assert response.status_code == 422
        assert response.json()["errors"][0]["code"] == "password_reuse"
        assert response.json()["errors"][0]["field"] == "new_password"

    def test_change_password_rejects_weak_password(self, user):
        client = self._client_for(user)

        response = client.post(
            "/api/v1/auth/password/change/",
            {"current_password": "TestPass!123", "new_password": "short"},
            format="json",
        )
        assert response.status_code == 422
        assert response.json()["errors"][0]["code"] == "weak_password"

    def test_change_password_requires_auth(self, api_client):
        response = api_client.post(
            "/api/v1/auth/password/change/",
            {"current_password": "TestPass!123", "new_password": "FreshPass!456"},
            format="json",
        )
        assert response.status_code == 401
