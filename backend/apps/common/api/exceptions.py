"""Central exception handler.

Normalizes DRF / Django exceptions into the error structure consumed by the
``ApiRenderer`` envelope and guarantees every error response carries the
same shape. Unexpected exceptions become a logged 500.
"""

from __future__ import annotations

import logging

from django.db import IntegrityError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from apps.common.exceptions import PharmaCloudError

logger = logging.getLogger(__name__)


def normalize_errors(data) -> list[dict]:
    """Normalize DRF error payloads into [{'code', 'field', 'message'}]."""
    if isinstance(data, dict):
        # PharmaCloudError payload shape: {"code", "message", "field"?}.
        if "code" in data and "message" in data:
            return [
                {
                    "code": data["code"],
                    "field": data.get("field"),
                    "message": data["message"],
                }
            ]
        errors = []
        for field, value in data.items():
            if field == "detail":
                errors.append({"code": "error", "field": None, "message": str(value)})
            elif field == "non_field_errors":
                errors.append(
                    {
                        "code": "validation_error",
                        "field": None,
                        "message": str(value[0]) if isinstance(value, (list, tuple)) and value else str(value),
                    }
                )
            elif isinstance(value, (list, tuple)):
                errors.append(
                    {
                        "code": "validation_error",
                        "field": field,
                        "message": str(value[0]) if value else str(value),
                        "details": [str(item) for item in value],
                    }
                )
            else:
                errors.append({"code": "validation_error", "field": field, "message": str(value)})
        return errors
    if isinstance(data, (list, tuple)):
        return [{"code": "error", "field": None, "message": str(item)} for item in data]
    return [{"code": "error", "field": None, "message": str(data)}]


def api_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if response is None:
        # Only unexpected exceptions reach here (Http404 is handled by DRF).
        if isinstance(exc, PharmaCloudError):
            logger.info("Domain error during request: %s [%s]", exc.code, exc.status_code)
            response = Response(exc.to_payload(), status=exc.status_code)
        elif isinstance(exc, IntegrityError):
            logger.warning("IntegrityError during request: %s", exc)
            response = Response({"detail": "The operation would violate data integrity."}, status=400)
        else:
            logger.exception("Unhandled exception during request", exc_info=exc)
            response = Response({"detail": "Internal server error."}, status=500)
    elif response.status_code >= 500:
        logger.error("API %s response for %s: %s", response.status_code, type(exc).__name__, exc)

    response.data = normalize_errors(response.data)
    return response
