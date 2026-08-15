"""Export views for apps.mobile_api."""

from apps.mobile_api.api.views.config_views import MobileConfigView
from apps.mobile_api.api.views.customer_views import CustomerMobileDashboardView
from apps.mobile_api.api.views.device_views import DeviceViewSet
from apps.mobile_api.api.views.owner_views import PharmacyOwnerMobileDashboardView
from apps.mobile_api.api.views.pharmacist_views import PharmacistMobileQueueView
from apps.mobile_api.api.views.sync_views import MobileSyncViewSet

__all__ = [
    "DeviceViewSet",
    "MobileConfigView",
    "CustomerMobileDashboardView",
    "PharmacyOwnerMobileDashboardView",
    "PharmacistMobileQueueView",
    "MobileSyncViewSet",
]
