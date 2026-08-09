"""App configuration for Enterprise Stock Movement Engine."""

from django.apps import AppConfig


class StockMovementConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.stock_movement"
    verbose_name = "Enterprise Stock Movement Engine"

    def ready(self):
        try:
            import apps.stock_movement.signals  # noqa: F401
        except ImportError:
            pass
