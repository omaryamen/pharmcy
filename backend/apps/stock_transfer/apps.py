"""App configuration for Stock Transfer module."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class StockTransferConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.stock_transfer"
    verbose_name = _("Enterprise Stock Transfer")
