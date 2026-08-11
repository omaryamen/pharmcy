from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SalesReturnsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.sales_returns"
    verbose_name = _("Enterprise Customer Sales Returns & Refund Management")
