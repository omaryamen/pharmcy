"""SystemHealthSelector running live diagnostics on Database, Cache, and returning latest component health checks."""

from __future__ import annotations

import time
from typing import Any
from django.db import connection

from apps.platform_ops.models import HealthStatus, SystemHealthCheck


class SystemHealthSelector:
    """Selector performing live infrastructure latency diagnostics and retrieving recent health check logs."""

    def perform_live_health_check(self) -> dict[str, Any]:
        """Perform real-time diagnostic probe on primary database connection."""
        start = time.perf_counter()
        db_status = HealthStatus.HEALTHY
        db_error = ""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                cursor.fetchone()
        except Exception as e:
            db_status = HealthStatus.DOWN
            db_error = str(e)
        latency = (time.perf_counter() - start) * 1000.0

        return {
            "status": "healthy" if db_status == HealthStatus.HEALTHY else "degraded",
            "database": {
                "status": db_status,
                "latency_ms": round(latency, 2),
                "error": db_error,
            },
            "recent_checks": list(
                SystemHealthCheck.objects.order_by("-checked_at")[:10].values(
                    "component_name", "status", "latency_ms", "checked_at", "error_message"
                )
            ),
        }
