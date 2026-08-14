"""SystemMaintenanceWindow model defining scheduled maintenance downtime."""

from __future__ import annotations

from typing import Any
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel


class SystemMaintenanceWindow(FullAuditModel):
    """Scheduled maintenance window during which non-admin tenant traffic is placed in maintenance mode."""

    title = models.CharField(max_length=150, verbose_name=_("Maintenance Title"))
    description = models.TextField(blank=True, default="", verbose_name=_("Maintenance Description"))

    start_time = models.DateTimeField(verbose_name=_("Start Time"))
    end_time = models.DateTimeField(verbose_name=_("End Time"))

    is_active = models.BooleanField(default=True, verbose_name=_("Is Maintenance Window Active"))
    bypass_key = models.CharField(max_length=64, blank=True, default="", verbose_name=_("Emergency Bypass Key"))
    affected_services = models.JSONField(default=list, blank=True, verbose_name=_("Affected Services List"))

    class Meta:
        db_table = "platform_maintenance_windows"
        verbose_name = _("System Maintenance Window")
        verbose_name_plural = _("System Maintenance Windows")
        ordering = ["-start_time"]

    def __str__(self) -> str:
        return f"{self.title} ({self.start_time} to {self.end_time}) [Active={self.is_active}]"

    @property
    def is_currently_in_effect(self) -> bool:
        now = timezone.now()
        return self.is_active and (self.start_time <= now <= self.end_time)
