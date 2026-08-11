from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PurchaseReturnsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.purchase_returns"
    verbose_name = _("Enterprise Purchase Returns & Supplier Returns")
