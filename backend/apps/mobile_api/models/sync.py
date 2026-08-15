"""MobileSyncQueue model tracking offline mutations and conflict resolutions."""

from __future__ import annotations

from typing import Any
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel, TenantAwareModel
from apps.mobile_api.models.enums import SyncOperation, SyncStatus


class MobileSyncQueue(TenantAwareModel, FullAuditModel):
    """Queue of offline mutations sent from mobile clients awaiting conflict resolution and execution."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mobile_sync_items",
        verbose_name=_("User"),
    )

    entity_type = models.CharField(max_length=60, db_index=True, verbose_name=_("Entity Domain Name (e.g. order, count_item)"))
    client_mutation_id = models.CharField(max_length=120, db_index=True, verbose_name=_("Client Generated Mutation UUID"))
    operation = models.CharField(
        max_length=20,
        choices=SyncOperation.choices,
        default=SyncOperation.CREATE,
        verbose_name=_("Sync Operation"),
    )

    payload = models.JSONField(default=dict, verbose_name=_("Client Mutation Payload"))
    client_version = models.IntegerField(default=1, verbose_name=_("Client Entity Version Snapshot"))

    status = models.CharField(
        max_length=20,
        choices=SyncStatus.choices,
        default=SyncStatus.PENDING,
        db_index=True,
        verbose_name=_("Sync Processing Status"),
    )

    conflict_reason = models.TextField(blank=True, default="", verbose_name=_("Conflict Error Details"))
    synced_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Processed Timestamp"))

    class Meta:
        db_table = "mobile_sync_queues"
        verbose_name = _("Mobile Sync Item")
        verbose_name_plural = _("Mobile Sync Queue")
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "client_mutation_id"],
                name="mobile_sync_client_mutation_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"Sync [{self.entity_type}:{self.operation}] - {self.client_mutation_id} ({self.status})"
