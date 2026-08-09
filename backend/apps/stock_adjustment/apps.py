"""AppConfig for Enterprise Stock Adjustment & Stock Count module."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class StockAdjustmentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.stock_adjustment"
    verbose_name = _("Stock Adjustment & Stock Count Engine")

    def ready(self):
        try:
            import apps.stock_adjustment.signals  # noqa: F401
        except ImportError:
            pass
