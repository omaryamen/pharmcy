"""Domain choices & enums for Enterprise SaaS Super Admin & Platform Operations Center."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class HealthStatus(models.TextChoices):
    HEALTHY = "healthy", _("Healthy")
    DEGRADED = "degraded", _("Degraded Performance")
    DOWN = "down", _("Service Down / Outage")


class AlertSeverity(models.TextChoices):
    INFO = "info", _("Informational")
    WARNING = "warning", _("Warning")
    ERROR = "error", _("Error")
    CRITICAL = "critical", _("Critical Outage / Security")


class AlertCategory(models.TextChoices):
    SECURITY = "security", _("Security & Authentication")
    BILLING = "billing", _("Subscription & Billing")
    PERFORMANCE = "performance", _("System Performance & Latency")
    INFRASTRUCTURE = "infrastructure", _("Database, Redis & Celery")
    COMPLIANCE = "compliance", _("Compliance & Regulatory")
