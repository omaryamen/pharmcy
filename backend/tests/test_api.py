"""API envelope + JWT authentication contract tests."""

from __future__ import annotations


class TestResponseEnvelope:
    def test_success_response_is_wrapped(self, authenticated_client, user):
        response = authenticated_client.get("/api/v1/auth/me/")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["status_code"] == 200
        assert body["data"]["email"] == user.email
        assert body["errors"] == []
        assert body["meta"]["request_id"] is not None
        assert body["meta"]["version"] == "v1"

    def test_validation_error_is_normalized(self, api_client):
        response = api_client.post("/api/v1/auth/token/", {}, format="json")

        assert response.status_code == 400
        body = response.json()
        assert body["success"] is False
        assert body["data"] is None
        assert isinstance(body["errors"], list)
        assert all("message" in error for error in body["errors"])

    def test_unauthenticated_request_returns_401_envelope(self, api_client):
        response = api_client.get("/api/v1/auth/me/")

        assert response.status_code == 401
        body = response.json()
        assert body["success"] is False
        assert body["errors"]

    def test_unknown_route_returns_404_envelope(self, api_client):
        response = api_client.get("/api/v1/does-not-exist/")

        assert response.status_code == 404
        body = response.json()
        assert body["success"] is False
        assert body["status_code"] == 404


class TestJWTAuthentication:
    def test_token_obtain_returns_access_and_refresh(self, api_client, user):
        response = api_client.post(
            "/api/v1/auth/token/",
            {"email": user.email, "password": "TestPass!123"},
            format="json",
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert "access" in data
        assert "refresh" in data

    def test_token_obtain_rejects_bad_credentials(self, api_client, user):
        response = api_client.post(
            "/api/v1/auth/token/",
            {"email": user.email, "password": "wrong-password"},
            format="json",
        )
        assert response.status_code == 401

    def test_refresh_cycle(self, api_client, user):
        obtain = api_client.post(
            "/api/v1/auth/token/",
            {"email": user.email, "password": "TestPass!123"},
            format="json",
        )
        refresh = obtain.json()["data"]["refresh"]

        refreshed = api_client.post("/api/v1/auth/token/refresh/", {"refresh": refresh}, format="json")
        assert refreshed.status_code == 200
        assert "access" in refreshed.json()["data"]

    def test_me_returns_authenticated_user(self, authenticated_client, user):
        response = authenticated_client.get("/api/v1/auth/me/")
        assert response.json()["data"]["email"] == user.email
