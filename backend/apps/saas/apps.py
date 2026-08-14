from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SaaSConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.saas"
    verbose_name = _("Enterprise SaaS Subscription, Billing & Licensing Platform")
