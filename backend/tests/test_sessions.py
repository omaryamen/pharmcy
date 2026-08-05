"""API tests for the session ledger, security audit trail and profile."""

from __future__ import annotations

import uuid

import pytest
from django.test import override_settings

from apps.authentication.models import LoginSession, SecurityEvent
from apps.core.models import User


def api_login(api_client, user):
    response = api_client.post(
        "/api/v1/auth/token/",
        {"email": user.email, "password": "TestPass!123"},
        format="json",
    )
    assert response.status_code == 200
    data = response.json()["data"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {data['access']}")
    return data


@pytest.mark.django_db
class TestSessions:
    def test_list_sessions_after_login(self, api_client, user):
        data = api_login(api_client, user)
        response = api_client.get("/api/v1/auth/sessions/")

        assert response.status_code == 200
        sessions = response.json()["data"]
        assert len(sessions) == 1
        assert sessions[0]["id"] == data["session_id"]
        assert sessions[0]["is_active"] is True
        assert sessions[0]["device_type"] == "api"  # no User-Agent sent by the test client

    def test_list_sessions_requires_auth(self, api_client):
        response = api_client.get("/api/v1/auth/sessions/")
        assert response.status_code == 401

    def test_revoke_single_session_invalidates_refresh(self, api_client, user):
        data = api_login(api_client, user)

        response = api_client.post(
            f"/api/v1/auth/sessions/{data['session_id']}/revoke/",
            {},
            format="json",
        )
        assert response.status_code == 200

        session = LoginSession.objects.get(pk=data["session_id"])
        assert session.is_active is False

        refreshed = api_client.post(
            "/api/v1/auth/token/refresh/",
            {"refresh": data["refresh"]},
            format="json",
        )
        assert refreshed.status_code == 401
        assert refreshed.json()["errors"][0]["code"] == "token_revoked"

    def test_revoke_unknown_session_returns_404(self, api_client, user):
        api_login(api_client, user)
        response = api_client.post(
            f"/api/v1/auth/sessions/{uuid.uuid4()}/revoke/",
            {},
            format="json",
        )
        assert response.status_code == 404
        assert response.json()["errors"][0]["code"] == "not_found"

    def test_cannot_revoke_another_users_session(self, api_client, user, db):
        api_login(api_client, user)

        other = User.objects.create_user(
            email="other@pharmacloud.test",
            password="TestPass!123",
            first_name="Other",
            email_verified=True,
        )
        other_data = api_login(api_client, other)
        api_login(api_client, user)  # restore credentials as the first user

        response = api_client.post(
            f"/api/v1/auth/sessions/{other_data['session_id']}/revoke/",
            {},
            format="json",
        )
        assert response.status_code == 404

        other_session = LoginSession.objects.get(pk=other_data["session_id"])
        assert other_session.is_active is True

    def test_revoke_all_sessions(self, api_client, user):
        first = api_login(api_client, user)
        second = api_login(api_client, user)
        assert first["session_id"] != second["session_id"]

        response = api_client.post("/api/v1/auth/sessions/revoke-all/", {}, format="json")
        assert response.status_code == 200
        assert response.json()["data"]["revoked"] == 2

        assert LoginSession.objects.filter(user=user, is_active=True).count() == 0
        for refresh in (first["refresh"], second["refresh"]):
            assert (
                api_client.post(
                    "/api/v1/auth/token/refresh/",
                    {"refresh": refresh},
                    format="json",
                ).status_code
                == 401
            )

    @override_settings(AUTH_MAX_ACTIVE_SESSIONS=2)
    def test_session_cap_revokes_oldest(self, api_client, user):
        first = api_login(api_client, user)
        second = api_login(api_client, user)
        third = api_login(api_client, user)

        first_session = LoginSession.objects.get(pk=first["session_id"])
        assert first_session.is_active is False  # evicted by the cap
        assert LoginSession.objects.filter(user=user, is_active=True).count() == 2
        assert second["session_id"] != third["session_id"]

    def test_revoke_records_security_event(self, api_client, user):
        data = api_login(api_client, user)
        api_client.post(f"/api/v1/auth/sessions/{data['session_id']}/revoke/", {}, format="json")

        event = SecurityEvent.objects.get(user=user, event_type="session_revoked")
        assert event.details == {"action": "revoke_one"}


@pytest.mark.django_db
class TestSecurityEvents:
    def test_events_listed_after_activity(self, api_client, user):
        api_login(api_client, user)
        api_client.post(
            "/api/v1/auth/token/",
            {"email": user.email, "password": "bad-password"},
            format="json",
        )

        response = api_client.get("/api/v1/auth/security/events/")
        assert response.status_code == 200

        events = response.json()["data"]
        event_types = [event["event_type"] for event in events]
        assert event_types[0] == "login_failed"  # most recent first
        assert "login_success" in event_types
        assert all(event["ip_address"] in ("127.0.0.1", None) for event in events)

    def test_events_are_scoped_to_authenticated_user(self, api_client, user, db):
        other = User.objects.create_user(
            email="other@pharmacloud.test",
            password="TestPass!123",
            first_name="Other",
            email_verified=True,
        )
        mine = SecurityEvent.objects.create(user=other, event_type="login_success")
        theirs = SecurityEvent.objects.create(user=user, event_type="login_success")
        api_login(api_client, other)

        response = api_client.get("/api/v1/auth/security/events/")
        assert response.status_code == 200
        ids = {event["id"] for event in response.json()["data"]}
        assert str(mine.pk) in ids
        assert str(theirs.pk) not in ids

    def test_events_requires_auth(self, api_client):
        response = api_client.get("/api/v1/auth/security/events/")
        assert response.status_code == 401


@pytest.mark.django_db
class TestProfile:
    def test_profile_get_returns_current_user(self, authenticated_client, user):
        response = authenticated_client.get("/api/v1/auth/me/")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["email"] == user.email
        assert data["id"] == str(user.pk)

    def test_profile_patch_updates_editable_fields(self, authenticated_client, user):
        response = authenticated_client.patch(
            "/api/v1/auth/profile/",
            {"first_name": "Updated", "last_name": "Person", "timezone": "Asia/Aden"},
            format="json",
        )
        assert response.status_code == 200

        user.refresh_from_db()
        assert user.first_name == "Updated"
        assert user.timezone == "Asia/Aden"
        assert SecurityEvent.objects.filter(user=user, event_type="profile_updated").exists()

    def test_profile_patch_rejects_invalid_timezone(self, authenticated_client, user):
        response = authenticated_client.patch(
            "/api/v1/auth/profile/",
            {"timezone": "Not/AZone"},
            format="json",
        )
        assert response.status_code == 400
        assert response.json()["errors"][0]["field"] == "timezone"

    def test_profile_patch_does_not_expose_email_or_status(self, authenticated_client, user):
        response = authenticated_client.patch(
            "/api/v1/auth/profile/",
            {"email": "hijack@pharmacloud.test", "status": "active"},
            format="json",
        )
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.email != "hijack@pharmacloud.test"
