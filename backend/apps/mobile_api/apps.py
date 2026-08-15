from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MobileApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.mobile_api"
    verbose_name = _("Enterprise Customer & Pharmacy Mobile Application API Platform")
