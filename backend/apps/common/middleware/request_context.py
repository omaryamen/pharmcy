"""Thread-local request context middleware.

Attaches a ``request_id`` to every request (from the ``X-Request-ID`` header
or a generated UUID) and exposes the current request/request_id to non-request
code paths (audit stamps, logging filters, services) via
``apps.common.utils.context``.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

from apps.common.utils import context as context_utils


class RequestContextMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request.request_id = request.META.get("HTTP_X_REQUEST_ID") or str(uuid.uuid4())
        context_utils.set_request(request)
        try:
            response = self.get_response(request)
        finally:
            context_utils.clear()
        response["X-Request-ID"] = request.request_id
        return response
