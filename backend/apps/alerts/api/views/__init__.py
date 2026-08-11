"""Export viewsets for apps.alerts.api."""

from apps.alerts.api.views.alert import InventoryAlertViewSet
from apps.alerts.api.views.recall import BatchRecallViewSet

__all__ = [
    "InventoryAlertViewSet",
    "BatchRecallViewSet",
]
