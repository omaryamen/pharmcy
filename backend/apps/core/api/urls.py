"""API routes for the core app (versioned under /api/v1/)."""

from __future__ import annotations

from django.urls import path

from .views import LivenessView, ReadinessView

app_name = "core"

urlpatterns = [
    path("health/liveness/", LivenessView.as_view(), name="health-liveness"),
    path("health/readiness/", ReadinessView.as_view(), name="health-readiness"),
]
