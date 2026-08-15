"""DeviceRegistrationService managing push tokens, device registration, and session revocations."""

from __future__ import annotations

import logging
from typing import Any
from django.db import transaction
from django.utils import timezone

from apps.mobile_api.models import Device, DevicePlatform

logger = logging.getLogger(__name__)


class DeviceRegistrationService:
    """Service layer registering mobile devices, storing push tokens, and revoking devices upon logout."""

    @transaction.atomic
    def register_device(
        self,
        user: Any,
        tenant: Any,
        *,
        device_identifier: str,
        platform: str = DevicePlatform.ANDROID,
        push_token: str = "",
        app_version: str = "1.0.0",
        os_version: str = "",
    ) -> Device:
        """Register or update mobile device with latest push token and OS metadata."""
        device, created = Device.objects.get_or_create(
            user=user,
            device_identifier=device_identifier,
            defaults={
                "tenant": tenant,
                "platform": platform,
                "push_token": push_token,
                "app_version": app_version,
                "os_version": os_version,
                "is_active": True,
                "last_seen": timezone.now(),
            },
        )
        if not created:
            device.tenant = tenant
            device.platform = platform
            device.push_token = push_token
            device.app_version = app_version
            device.os_version = os_version
            device.is_active = True
            device.last_seen = timezone.now()
            device.save(update_fields=["tenant", "platform", "push_token", "app_version", "os_version", "is_active", "last_seen", "updated_at"])

        logger.info("Registered mobile device %s for user %s (%s)", device_identifier, user, platform)
        return device

    def revoke_device(self, user: Any, device_identifier: str) -> bool:
        """Deactivate a mobile device, invalidating push dispatches and active sessions."""
        device = Device.objects.filter(user=user, device_identifier=device_identifier).first()
        if device:
            device.is_active = False
            device.save(update_fields=["is_active", "updated_at"])
            logger.info("Revoked mobile device %s for user %s", device_identifier, user)
            return True
        return False
