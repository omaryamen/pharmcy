"""Company Settings service."""

from __future__ import annotations

import logging

from django.db import transaction

from apps.companies.models import CompanySettings
from apps.companies.repositories import CompanySettingsRepository

logger = logging.getLogger(__name__)


class CompanySettingsService:
    def __init__(self) -> None:
        self.repository = CompanySettingsRepository()

    @transaction.atomic
    def update_settings(self, company, **setting_fields) -> CompanySettings:
        settings_obj, _ = self.repository.get_or_create(company=company, defaults={"tenant": company.tenant})

        for key, val in setting_fields.items():
            if hasattr(settings_obj, key) and isinstance(val, dict):
                current_val = getattr(settings_obj, key) or {}
                if isinstance(current_val, dict):
                    setattr(settings_obj, key, {**current_val, **val})
                else:
                    setattr(settings_obj, key, val)
            elif hasattr(settings_obj, key):
                setattr(settings_obj, key, val)

        settings_obj.save()
        logger.info("Updated settings for company %s", company.code)
        return settings_obj
