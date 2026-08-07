"""Tenant Settings service for managing domain configuration objects."""

from __future__ import annotations

import logging

from django.db import transaction

from apps.tenants.repositories import TenantSettingsRepository

logger = logging.getLogger(__name__)


class TenantSettingsService:
    def __init__(self) -> None:
        self.settings_repository = TenantSettingsRepository()

    @transaction.atomic
    def update_settings(self, tenant, **setting_fields) -> dict:
        settings_obj, _ = self.settings_repository.get_or_create(tenant=tenant)

        for key, val in setting_fields.items():
            if hasattr(settings_obj, key) and isinstance(val, dict):
                current_val = getattr(settings_obj, key) or {}
                if isinstance(current_val, dict):
                    merged = {**current_val, **val}
                    setattr(settings_obj, key, merged)
                else:
                    setattr(settings_obj, key, val)
            elif hasattr(settings_obj, key):
                setattr(settings_obj, key, val)

        settings_obj.save()
        logger.info("Updated settings for tenant %s", tenant.slug)
        return settings_obj
