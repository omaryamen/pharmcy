"""Thread-local request context accessors.

Used by audit fields, logging filters and services to reach the current
request / user / tenant / request_id outside of view code.
"""

from __future__ import annotations

import threading

_local = threading.local()


def set_request(request) -> None:
    _local.request = request


def clear() -> None:
    _local.request = None


def get_current_request():
    return getattr(_local, "request", None)


def get_current_user():
    request = get_current_request()
    return getattr(request, "user", None) if request is not None else None


def get_current_tenant():
    request = get_current_request()
    return getattr(request, "tenant", None) if request is not None else None


def get_request_id() -> str | None:
    request = get_current_request()
    return getattr(request, "request_id", None) if request is not None else None
