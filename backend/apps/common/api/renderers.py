"""Unified API response envelope renderer.

Every JSON response is wrapped in a stable contract::

    {
      "success": true,
      "status_code": 200,
      "message": "Success",
      "data": {...},
      "errors": [],
      "meta": {"request_id": "...", "timestamp": "...", "version": "v1"}
    }

Non-JSON responses (file downloads, OpenAPI schema, Swagger HTML) are
passed through untouched — the renderer only wraps when it produced the
accepted renderer for the response.
"""

from __future__ import annotations

import json

from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from rest_framework.renderers import JSONRenderer

from apps.common.utils.context import get_request_id


def _extract_message(data) -> str:
    if isinstance(data, dict):
        detail = data.get("detail")
        if detail:
            if isinstance(detail, (list, tuple)) and detail:
                return str(detail[0])
            return str(detail)
    return "Request failed."


class ApiRenderer(JSONRenderer):
    media_type = "application/json"
    format = "json"
    charset = "utf-8"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        renderer_context = renderer_context or {}
        response = renderer_context.get("response")

        # Skip wrapping for non-envelope renderers (browsable API, OpenAPI, files)
        # and for responses explicitly opted out via the X-Envelope: skip header
        # (e.g. health probes consumed directly by orchestrators).
        if response is None or not isinstance(getattr(response, "accepted_renderer", None), ApiRenderer):
            return super().render(data, accepted_media_type, renderer_context)
        if response.get("X-Envelope") == "skip":
            return super().render(data, accepted_media_type, renderer_context)

        status_code = response.status_code
        success = 200 <= status_code < 300

        payload = {
            "success": success,
            "status_code": status_code,
            "message": "Success" if success else _extract_message(data),
            "data": data if success else None,
            "errors": [] if success else data,
            "meta": {
                "request_id": get_request_id(),
                "timestamp": timezone.now().isoformat(),
                "version": "v1",
            },
        }
        return json.dumps(payload, ensure_ascii=False, cls=DjangoJSONEncoder).encode(self.charset)
