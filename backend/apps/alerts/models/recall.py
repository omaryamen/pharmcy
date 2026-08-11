"""Batch Recall entity tracking regulatory, manufacturer, and quality recall orders."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.alerts.models.enums import RecallClass, RecallStatus, RecallType
from apps.common.models import FullAuditModel, TenantAwareModel


class BatchRecall(TenantAwareModel, FullAuditModel):
    """Pharmaceutical Batch Recall document tracking regulatory directives and stock quarantine execution."""

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="batch_recalls",
        verbose_name=_("Company"),
        db_index=True,
    )
    medicine = models.ForeignKey(
        "medicines.Medicine",
        on_delete=models.CASCADE,
        related_name="batch_recalls",
        verbose_name=_("Medicine"),
        db_index=True,
    )
    batch = models.ForeignKey(
        "inventory.Batch",
        on_delete=models.CASCADE,
        related_name="recalls",
        verbose_name=_("Recalled Batch"),
        db_index=True,
    )

    recall_number = models.CharField(max_length=60, db_index=True, verbose_name=_("Recall Order Number"))

    recall_type = models.CharField(
        max_length=40,
        choices=RecallType.choices,
        default=RecallType.VOLUNTARY_MANUFACTURER,
        verbose_name=_("Recall Type"),
    )
    recall_class = models.CharField(
        max_length=20,
        choices=RecallClass.choices,
        default=RecallClass.CLASS_2_URGENT,
        verbose_name=_("Recall Class"),
    )
    status = models.CharField(
        max_length=30,
        choices=RecallStatus.choices,
        default=RecallStatus.DRAFT,
        db_index=True,
        verbose_name=_("Recall Status"),
    )

    reason = models.TextField(verbose_name=_("Reason for Recall"))
    action_required = models.TextField(blank=True, default="", verbose_name=_("Action Required"))
    regulatory_reference = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Regulatory Reference / Notice No."))

    quarantined_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Quarantined Quantity"))
    disposed_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Disposed Quantity"))
    returned_quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("0.0000"), verbose_name=_("Returned Quantity"))

    initiated_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Initiated At"))
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="initiated_recalls",
        null=True,
        blank=True,
        verbose_name=_("Initiated By"),
    )

    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Completed At"))
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="completed_recalls",
        null=True,
        blank=True,
        verbose_name=_("Completed By"),
    )

    class Meta:
        db_table = "batch_recalls"
        verbose_name = _("Batch Recall")
        verbose_name_plural = _("Batch Recalls")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "recall_number"],
                name="batch_recall_tenant_number_uniq",
            )
        ]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "batch"]),
            models.Index(fields=["tenant", "medicine"]),
        ]

    def __str__(self) -> str:
        return f"[{self.recall_class.upper()}] {self.recall_number} - Batch {self.batch.batch_number}"
