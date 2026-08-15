"""MobileAppConfigService providing version enforcement and feature flags to mobile apps."""

from __future__ import annotations

from typing import Any
from apps.mobile_api.models import DevicePlatform, MobileAppVersion
from apps.platform_ops.selectors import FeatureFlagSelector


class MobileAppConfigService:
    """Service layer resolving app configuration, minimum version checks, and tenant feature flags."""

    def __init__(self, feature_selector: FeatureFlagSelector | None = None) -> None:
        self.feature_selector = feature_selector or FeatureFlagSelector()

    def get_mobile_config(self, platform: str = DevicePlatform.ANDROID, *, tenant: Any | None = None) -> dict[str, Any]:
        """Fetch version policies, maintenance mode, and feature flags for mobile clients."""
        version_policy = MobileAppVersion.objects.filter(platform=platform).first()

        flags = {
            "ai_prescription_scanner": self.feature_selector.is_feature_enabled("ai_prescription_scanner", tenant=tenant),
            "offline_pos_sync": self.feature_selector.is_feature_enabled("offline_pos_sync", tenant=tenant),
            "instant_courier_tracking": self.feature_selector.is_feature_enabled("instant_courier_tracking", tenant=tenant),
        }

        return {
            "platform": platform,
            "min_version": version_policy.min_version if version_policy else "1.0.0",
            "recommended_version": version_policy.recommended_version if version_policy else "1.0.0",
            "is_force_update": version_policy.is_force_update if version_policy else False,
            "maintenance_mode": version_policy.maintenance_mode if version_policy else False,
            "maintenance_message": version_policy.maintenance_message if version_policy else "",
            "feature_flags": flags,
        }
