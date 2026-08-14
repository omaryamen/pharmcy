"""SystemHealthCheck model recording diagnostic checks across system components."""

from __future__ import annotations

from typing import Any
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel
from apps.platform_ops.models.enums import HealthStatus


class SystemHealthCheck(FullAuditModel):
    """Health status check log for infrastructure components (PostgreSQL, Redis, Celery, Storage)."""

    component_name = models.CharField(max_length=60, db_index=True, verbose_name=_("Component Name"))
    status = models.CharField(
        max_length=20,
        choices=HealthStatus.choices,
        default=HealthStatus.HEALTHY,
        db_index=True,
        verbose_name=_("Health Status"),
    )

    latency_ms = models.FloatField(default=0.0, verbose_name=_("Response Latency (ms)"))
    checked_at = models.DateTimeField(default=timezone.now, db_index=True, verbose_name=_("Checked Timestamp"))
    details = models.JSONField(default=dict, blank=True, verbose_name=_("Diagnostic Metadata Details"))
    error_message = models.TextField(blank=True, default="", verbose_name=_("Error Details"))

    class Meta:
        db_table = "platform_health_checks"
        verbose_name = _("System Health Check")
        verbose_name_plural = _("System Health Checks")
        ordering = ["-checked_at"]

    def __str__(self) -> str:
        return f"{self.component_name} [{self.status}] - {self.latency_ms:.1f}ms ({self.checked_at})"
