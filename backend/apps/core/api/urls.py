"""API routes for the core app (versioned under /api/v1/)."""

from __future__ import annotations

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from .views import LivenessView, MeView, ReadinessView

app_name = "core"

urlpatterns = [
    # --- Health ---
    path("health/liveness/", LivenessView.as_view(), name="health-liveness"),
    path("health/readiness/", ReadinessView.as_view(), name="health-readiness"),
    # --- Authentication (JWT) ---
    path("auth/token/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token-verify"),
    path("auth/me/", MeView.as_view(), name="me"),
]
