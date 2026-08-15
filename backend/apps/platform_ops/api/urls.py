"""URL Routing Configuration for Super Admin & Platform Operations REST API."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.platform_ops.api.views import (
    GlobalFeatureFlagViewSet,
    PlatformAlertViewSet,
    PlatformOverviewView,
    PlatformTenantAdminViewSet,
    SystemHealthView,
    SystemMaintenanceWindowViewSet,
)

router = DefaultRouter()
router.register(r"platform/tenants", PlatformTenantAdminViewSet, basename="platform-tenants")
router.register(r"platform/maintenance", SystemMaintenanceWindowViewSet, basename="platform-maintenance")
router.register(r"platform/feature-flags", GlobalFeatureFlagViewSet, basename="platform-feature-flags")
router.register(r"platform/alerts", PlatformAlertViewSet, basename="platform-alerts")

urlpatterns = router.urls + [
    path("platform/overview/", PlatformOverviewView.as_view(), name="platform-overview"),
    path("platform/health/", SystemHealthView.as_view(), name="platform-health"),
]
