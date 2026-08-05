"""Health check endpoints (liveness + readiness)."""

from __future__ import annotations

import logging

from django.core.cache import cache
from django.db import connection
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

LIVENESS_OK = {"status": "ok"}


class HealthAPIView(APIView):
    """Base for health probes.

    Returns raw JSON (no envelope) so orchestrators / load balancers can
    parse it directly; the ``X-Envelope: skip`` header opts out of the
    standard response envelope.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def finalize_response(self, request, response, *args, **kwargs):
        response["X-Envelope"] = "skip"
        return super().finalize_response(request, response, *args, **kwargs)


class LivenessView(HealthAPIView):
    """Liveness probe — confirms the process is up.

    Does not touch external dependencies.
    """

    def get(self, request):
        return Response(LIVENESS_OK)


class ReadinessView(HealthAPIView):
    """Readiness probe — confirms database, cache and Celery are reachable.

    Returns 503 with per-dependency status when any dependency is down.
    """

    def get(self, request):
        checks: dict[str, str] = {}
        ready = True

        # --- Database ---
        try:
            connection.ensure_connection()
            connection.close()
            checks["database"] = "ok"
        except Exception as exc:  # noqa: BLE001
            logger.error("Readiness check failed [database]: %s", exc)
            checks["database"] = "error"
            ready = False

        # --- Cache (Redis) ---
        try:
            probe = f"readiness:{request.request_id}"
            cache.set(probe, "ok", timeout=5)
            if cache.get(probe) == "ok":
                checks["cache"] = "ok"
            else:
                checks["cache"] = "error"
                ready = False
        except Exception as exc:  # noqa: BLE001
            logger.error("Readiness check failed [cache]: %s", exc)
            checks["cache"] = "error"
            ready = False

        # --- Celery worker ---
        try:
            from config.celery import app as celery_app

            ping = celery_app.control.ping(timeout=2)
            checks["celery"] = "ok" if ping else "error"
            if not ping:
                ready = False
        except Exception as exc:  # noqa: BLE001
            logger.error("Readiness check failed [celery]: %s", exc)
            checks["celery"] = "error"
            ready = False

        return Response(
            {"status": "ready" if ready else "not_ready", "checks": checks},
            status=200 if ready else 503,
        )
