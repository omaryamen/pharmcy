"""Health check endpoint tests."""

from __future__ import annotations


def test_liveness_returns_ok(api_client):
    response = api_client.get("/api/v1/health/liveness/")

    assert response.status_code == 200
    assert response["X-Envelope"] == "skip"
    assert response.json() == {"status": "ok"}


def test_readiness_reports_dependency_checks(db, api_client):
    response = api_client.get("/api/v1/health/readiness/")

    assert response.status_code in (200, 503)
    body = response.json()
    assert body["status"] in ("ready", "not_ready")
    assert set(body["checks"]) >= {"database", "cache", "celery"}


def test_liveness_is_public_without_authentication(api_client):
    response = api_client.get("/api/v1/health/liveness/")
    assert response.status_code == 200
