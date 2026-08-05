"""Common app — shared, framework-agnostic infrastructure.

Contains base models (UUID / timestamp / soft-delete / audit), tenant
awareness, request context, permissions, exceptions, repositories,
services, the API envelope renderer, pagination, and storage backends.
Business modules import from here and never re-implement these concerns.
"""

from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.common"
    label = "common"
    verbose_name = "Common"
