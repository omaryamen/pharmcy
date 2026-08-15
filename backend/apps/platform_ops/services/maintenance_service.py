"""MaintenanceModeService managing system-wide or scoped maintenance windows."""

from __future__ import annotations

import logging
import uuid
from typing import Any
from django.utils import timezone

from apps.platform_ops.models import SystemMaintenanceWindow

logger = logging.getLogger(__name__)


class MaintenanceModeService:
    """Service layer creating and toggling system maintenance windows."""

    def schedule_maintenance(
        self,
        title: str,
        start_time: Any,
        end_time: Any,
        *,
        description: str = "",
        affected_services: list[str] | None = None,
    ) -> SystemMaintenanceWindow:
        """Schedule a maintenance window with emergency bypass key."""
        bypass_key = f"maint_key_{uuid.uuid4().hex[:16]}"
        maint = SystemMaintenanceWindow.objects.create(
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            is_active=True,
            bypass_key=bypass_key,
            affected_services=affected_services or ["all"],
        )
        logger.warning("Scheduled Maintenance Window '%s' from %s to %s", title, start_time, end_time)
        return maint
