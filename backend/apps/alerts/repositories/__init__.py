"""Export repositories for apps.alerts."""

from apps.alerts.repositories.alert_repository import InventoryAlertRepository
from apps.alerts.repositories.recall_repository import BatchRecallRepository

__all__ = [
    "InventoryAlertRepository",
    "BatchRecallRepository",
]
