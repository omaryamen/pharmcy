"""Logging utilities: request-context filter and JSON formatter.

The ``RequestContextFilter`` enriches every record with the current
request_id / tenant / user so all loggers are correlation-ready.
The ``JsonFormatter`` produces machine-parseable log lines (production).
"""

from __future__ import annotations

import json
import logging
from typing import Any

from .context import get_current_request


class RequestContextFilter(logging.Filter):
    """Add request correlation fields to log records (when available)."""

    def filter(self, record: logging.LogRecord) -> bool:
        request = get_current_request()
        if request is None:
            return True
        record.request_id = getattr(request, "request_id", None)
        tenant = getattr(request, "tenant", None)
        record.tenant_id = getattr(tenant, "id", None)
        user = getattr(request, "user", None)
        record.user_id = getattr(user, "pk", None)
        record.method = getattr(request, "method", None)
        record.path = getattr(request, "path", None)
        return True


class JsonFormatter(logging.Formatter):
    """Structured JSON log formatter for production environments."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        for attr in ("request_id", "tenant_id", "user_id", "method", "path"):
            value = getattr(record, attr, None)
            if value is not None:
                payload[attr] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)
