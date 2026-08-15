"""Domain choices & enums for Mobile Application API Platform."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class DevicePlatform(models.TextChoices):
    ANDROID = "android", _("Android OS")
    IOS = "ios", _("Apple iOS")
    PWA = "pwa", _("Progressive Web App")
    DESKTOP_CLIENT = "desktop", _("Dedicated Desktop Client")


class SyncOperation(models.TextChoices):
    CREATE = "create", _("Create Entity")
    UPDATE = "update", _("Update Entity")
    DELETE = "delete", _("Delete Entity")


class SyncStatus(models.TextChoices):
    PENDING = "pending", _("Pending Server Processing")
    APPLIED = "applied", _("Applied Successfully")
    CONFLICT = "conflict", _("Version Conflict Detected")
    REJECTED = "rejected", _("Rejected by Business Logic")
