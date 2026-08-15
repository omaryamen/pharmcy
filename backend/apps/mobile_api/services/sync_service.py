"""MobileSyncService processing offline client mutations and reporting delta changes."""

from __future__ import annotations

import logging
from typing import Any
from django.db import transaction
from django.utils import timezone

from apps.mobile_api.exceptions import SyncConflictError
from apps.mobile_api.models import MobileSyncQueue, SyncOperation, SyncStatus

logger = logging.getLogger(__name__)


class MobileSyncService:
    """Service layer processing offline mutation items and resolving version conflicts."""

    @transaction.atomic
    def process_sync_item(
        self,
        tenant: Any,
        user: Any,
        *,
        entity_type: str,
        client_mutation_id: str,
        operation: str,
        payload: dict[str, Any],
        client_version: int = 1,
    ) -> MobileSyncQueue:
        """Process an offline mutation item, validating duplicate mutation IDs and conflict states."""
        # 1. Idempotency Check
        existing = MobileSyncQueue.objects.filter(tenant=tenant, client_mutation_id=client_mutation_id).first()
        if existing:
            return existing

        # 2. Version Conflict Check (if client is mutating a stale record version)
        server_expected_version = payload.get("server_expected_version")
        if server_expected_version is not None and client_version < server_expected_version:
            sync_item = MobileSyncQueue.objects.create(
                tenant=tenant,
                user=user,
                entity_type=entity_type,
                client_mutation_id=client_mutation_id,
                operation=operation,
                payload=payload,
                client_version=client_version,
                status=SyncStatus.CONFLICT,
                conflict_reason=f"Client version {client_version} is behind server version {server_expected_version}",
            )
            raise SyncConflictError(sync_item.conflict_reason)

        # 3. Successful sync entry
        sync_item = MobileSyncQueue.objects.create(
            tenant=tenant,
            user=user,
            entity_type=entity_type,
            client_mutation_id=client_mutation_id,
            operation=operation,
            payload=payload,
            client_version=client_version,
            status=SyncStatus.APPLIED,
            synced_at=timezone.now(),
        )
        logger.info("Processed offline sync item %s for %s (%s)", client_mutation_id, user, entity_type)
        return sync_item
