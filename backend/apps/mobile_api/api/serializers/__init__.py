"""Export serializers for apps.mobile_api."""

from apps.mobile_api.api.serializers.device import DeviceSerializer
from apps.mobile_api.api.serializers.sync import MobileSyncQueueSerializer

__all__ = [
    "DeviceSerializer",
    "MobileSyncQueueSerializer",
]
