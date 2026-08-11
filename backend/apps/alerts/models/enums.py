"""Domain choices & enums for Enterprise Expiry, Recall & Inventory Alert Management."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class AlertType(models.TextChoices):
    LOW_STOCK = "low_stock", _("Low Stock Warning")
    REORDER_POINT = "reorder_point", _("Reorder Point Reached")
    OUT_OF_STOCK = "out_of_stock", _("Out of Stock Critical")
    OVERSTOCK = "overstock", _("Overstock Alert")
    EXPIRY_WARNING = "expiry_warning", _("Near Expiry Warning")
    EXPIRED = "expired", _("Stock Expired Critical")
    BATCH_RECALL = "batch_recall", _("Batch Recall Notice")
    QUARANTINE_NOTICE = "quarantine_notice", _("Quarantine Notice")
    TEMPERATURE_EXCURSION = "temperature_excursion", _("Temperature Excursion")
    CUSTOM = "custom", _("Custom Operational Alert")


class AlertSeverity(models.TextChoices):
    INFO = "info", _("Informational")
    LOW = "low", _("Low Severity")
    MEDIUM = "medium", _("Medium Severity")
    HIGH = "high", _("High Severity")
    CRITICAL = "critical", _("Critical Action Required")


class AlertStatus(models.TextChoices):
    ACTIVE = "active", _("Active Alert")
    ACKNOWLEDGED = "acknowledged", _("Acknowledged")
    IN_PROGRESS = "in_progress", _("Resolution In Progress")
    RESOLVED = "resolved", _("Resolved")
    DISMISSED = "dismissed", _("Dismissed")
    SUPPRESSED = "suppressed", _("Suppressed")


class RecallType(models.TextChoices):
    VOLUNTARY_MANUFACTURER = "voluntary_manufacturer", _("Voluntary Manufacturer Recall")
    REGULATORY_FDA = "regulatory_fda", _("FDA Regulatory Order")
    SFDA_DIRECTIVE = "sfda_directive", _("SFDA Regulatory Directive")
    QUALITY_DEFECT = "quality_defect", _("Quality Defect Investigation")
    SAFETY_WARNING = "safety_warning", _("Safety Warning & Withdrawal")


class RecallClass(models.TextChoices):
    CLASS_1_CRITICAL = "class_1", _("Class I (High Risk of Severe Adverse Health Consequences)")
    CLASS_2_URGENT = "class_2", _("Class II (Temporary or Medically Reversible Health Risk)")
    CLASS_3_NORMAL = "class_3", _("Class III (Unlikely to Cause Adverse Health Consequences)")


class RecallStatus(models.TextChoices):
    DRAFT = "draft", _("Draft Recall")
    INITIATED = "initiated", _("Recall Initiated")
    QUARANTINE_IN_PROGRESS = "quarantine_in_progress", _("Stock Quarantining In Progress")
    QUARANTINED = "quarantined", _("Stock Fully Quarantined")
    COMPLETED = "completed", _("Recall Completed & Closed")
    CANCELLED = "cancelled", _("Recall Cancelled")
