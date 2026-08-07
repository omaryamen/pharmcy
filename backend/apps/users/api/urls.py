"""User API URL Routing."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.users.api.views import UserStatsView, UserViewSet

router = DefaultRouter()
router.register(r"", UserViewSet, basename="enterprise-user")

urlpatterns = [
    path("stats/", UserStatsView.as_view(), name="user-stats"),
    path("", include(router.urls)),
]
