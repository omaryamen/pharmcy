from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PlatformOpsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.platform_ops"
    verbose_name = _("Enterprise SaaS Super Admin & Platform Operations Center")
