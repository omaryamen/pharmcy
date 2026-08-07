"""Branch Settings service."""

from __future__ import annotations

import logging

from django.db import transaction

from apps.branches.models import BranchSettings
from apps.branches.repositories import BranchSettingsRepository

logger = logging.getLogger(__name__)


class BranchSettingsService:
    def __init__(self) -> None:
        self.repository = BranchSettingsRepository()

    @transaction.atomic
    def update_settings(self, branch, **setting_fields) -> BranchSettings:
        settings_obj, _ = self.repository.get_or_create(
            branch=branch,
            defaults={"company": branch.company, "tenant": branch.tenant},
        )

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
        logger.info("Updated settings for branch %s", branch.code)
        return settings_obj
