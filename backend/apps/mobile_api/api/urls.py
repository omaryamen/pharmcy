"""URL Routing Configuration for Mobile API Platform."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.mobile_api.api.views import (
    CustomerMobileDashboardView,
    DeviceViewSet,
    MobileConfigView,
    MobileSyncViewSet,
    PharmacyOwnerMobileDashboardView,
    PharmacistMobileQueueView,
)

router = DefaultRouter()
router.register(r"mobile/devices", DeviceViewSet, basename="mobile-devices")
router.register(r"mobile/sync", MobileSyncViewSet, basename="mobile-sync")

urlpatterns = router.urls + [
    path("mobile/config/", MobileConfigView.as_view(), name="mobile-config"),
    path("mobile/customer/dashboard/", CustomerMobileDashboardView.as_view(), name="mobile-customer-dashboard"),
    path("mobile/owner/dashboard/", PharmacyOwnerMobileDashboardView.as_view(), name="mobile-owner-dashboard"),
    path("mobile/pharmacist/queue/", PharmacistMobileQueueView.as_view(), name="mobile-pharmacist-queue"),
]
