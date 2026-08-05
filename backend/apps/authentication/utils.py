"""Helpers shared across the authentication module."""

from __future__ import annotations

import logging

from django.conf import settings
from rest_framework.request import Request

from .models import SessionDeviceType

logger = logging.getLogger(__name__)

_MOBILE_HINTS = ("mobile", "android", "iphone", "ipad", "windows phone", "blackberry")


def client_ip(request: Request | None) -> str | None:
    """Best-effort client IP, honoring reverse-proxy forwarding."""
    if request is None:
        return None
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def parse_user_agent(user_agent: str) -> tuple[str, str]:
    """Best-effort ``(device_name, device_type)`` from a User-Agent string."""
    user_agent = (user_agent or "").strip()
    if not user_agent:
        return "", SessionDeviceType.API

    lower = user_agent.lower()
    if any(hint in lower for hint in _MOBILE_HINTS):
        device_type = SessionDeviceType.MOBILE
        if "ipad" in lower:
            device_type = SessionDeviceType.TABLET
    elif any(keyword in lower for keyword in ("macintosh", "windows nt", "x11", "linux")):
        device_type = SessionDeviceType.DESKTOP
    else:
        device_type = SessionDeviceType.WEB

    name = user_agent.split("/", 1)[0].strip()[:255]
    return name, device_type


def deliver_phone_code(phone: str, code: str) -> bool:
    """Deliver a phone verification code.

    Uses the pluggable ``AUTH_SMS_BACKEND`` when configured (a dotted import
    of a ``send_sms(phone, message)`` callable). Without a provider the code is
    written to the application log — development/audit only, never production.
    """
    backend_path = getattr(settings, "AUTH_SMS_BACKEND", "")
    if not backend_path:
        logger.warning("Phone verification code for %s: %s (no AUTH_SMS_BACKEND configured)", phone, code)
        return False

    from django.utils.module_loading import import_string

    send_sms = import_string(backend_path)
    send_sms(phone, f"Your PharmaCloud verification code is {code}.")
    return True
