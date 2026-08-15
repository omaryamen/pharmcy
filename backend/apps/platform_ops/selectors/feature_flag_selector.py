"""FeatureFlagSelector evaluating global feature flags against tenant attributes and rollout percentages."""

from __future__ import annotations

import hashlib
from typing import Any

from apps.core.models import Tenant
from apps.platform_ops.models import GlobalFeatureFlag


class FeatureFlagSelector:
    """Selector resolving whether a given feature flag is active for a specific tenant."""

    def is_feature_enabled(self, feature_key: str, tenant: Tenant | None = None) -> bool:
        """Evaluate feature flag rules (globally enabled, blacklists, whitelists, rollout hash)."""
        flag = GlobalFeatureFlag.objects.filter(feature_key=feature_key).first()
        if not flag:
            return False

        if not tenant:
            return flag.is_globally_enabled

        tenant_code = getattr(tenant, "code", "")
        tenant_slug = getattr(tenant, "slug", "")

        # Check blacklist
        if tenant_code in flag.blacklisted_tenants or tenant_slug in flag.blacklisted_tenants:
            return False

        # Check whitelist
        if tenant_code in flag.whitelisted_tenants or tenant_slug in flag.whitelisted_tenants:
            return True

        if flag.is_globally_enabled:
            return True

        # Percentage rollout hash based on tenant UUID/code
        if flag.rollout_percentage > 0:
            hash_val = int(hashlib.md5(f"{feature_key}:{tenant_code}".encode("utf-8")).hexdigest(), 16)
            bucket = hash_val % 100
            return bucket < flag.rollout_percentage

        return False
