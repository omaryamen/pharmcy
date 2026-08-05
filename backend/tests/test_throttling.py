"""Rate-limiting tests for authentication endpoints.

The throttle classes are configured with high limits in the testing settings,
so these tests tighten the limits directly on the classes and assert the
DRF 429 envelope kicks in past the boundary.
"""

from __future__ import annotations

import pytest
from django.core.cache import cache

from apps.authentication.throttles import (
    LoginEmailThrottle,
    LoginIPThrottle,
    PasswordResetEmailThrottle,
)


@pytest.fixture(autouse=True)
def _reset_throttle_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.mark.django_db
class TestLoginThrottling:
    def test_email_scoped_throttle_blocks_past_limit(self, api_client, monkeypatch):
        monkeypatch.setattr(LoginEmailThrottle, "THROTTLE_RATES", {"auth_login_email": "2/min"})
        monkeypatch.setattr(LoginIPThrottle, "THROTTLE_RATES", {"auth_login_ip": "10000/min"})

        payload = {"email": "throttle@pharmacloud.test", "password": "wrong"}
        assert api_client.post("/api/v1/auth/token/", payload, format="json").status_code == 401
        assert api_client.post("/api/v1/auth/token/", payload, format="json").status_code == 401

        blocked = api_client.post("/api/v1/auth/token/", payload, format="json")
        assert blocked.status_code == 429
        assert blocked.json()["errors"][0]["code"] == "throttled"

    def test_throttle_is_scoped_per_email(self, api_client, user, monkeypatch):
        monkeypatch.setattr(LoginEmailThrottle, "THROTTLE_RATES", {"auth_login_email": "1/min"})
        monkeypatch.setattr(LoginIPThrottle, "THROTTLE_RATES", {"auth_login_ip": "10000/min"})

        payload = {"email": user.email, "password": "wrong"}
        assert api_client.post("/api/v1/auth/token/", payload, format="json").status_code == 401
        assert api_client.post("/api/v1/auth/token/", payload, format="json").status_code == 429

        # A different email is unaffected by the exhausted budget of the first.
        other = {"email": "someone-else@pharmacloud.test", "password": "wrong"}
        assert api_client.post("/api/v1/auth/token/", other, format="json").status_code == 401


@pytest.mark.django_db
class TestPasswordResetThrottling:
    def test_reset_email_throttle_blocks_past_limit(self, api_client, user, monkeypatch):
        monkeypatch.setattr(
            PasswordResetEmailThrottle,
            "THROTTLE_RATES",
            {"auth_password_reset_email": "1/hour"},
        )

        url = "/api/v1/auth/password/reset/request/"
        assert api_client.post(url, {"email": user.email}, format="json").status_code == 200

        blocked = api_client.post(url, {"email": user.email}, format="json")
        assert blocked.status_code == 429
        assert blocked.json()["errors"][0]["code"] == "throttled"
