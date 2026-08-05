"""Core app — platform foundations.

Contains the custom user model (email login, JWT-ready), the tenant model
(multi-tenant SaaS), authentication endpoints and health checks.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    label = "core"
    verbose_name = "Core"
