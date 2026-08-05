"""Caching for effective permissions.

Correctness model: a monotonically increasing global version number is
stored in the cache. Every effective-permission cache key embeds the version,
so any RBAC mutation (``PermissionCache.invalidate``) atomically makes every
previously computed result stale. Expired entries are simply never read and
are cleaned by the backend TTL.
"""

from __future__ import annotations

from contextlib import suppress

from django.conf import settings
from django.core.cache import cache


class PermissionCache:
    VERSION_KEY = "rbac:cache:version"

    def __init__(self, cache_backend=cache) -> None:
        self.backend = cache_backend

    def current_version(self) -> int:
        try:
            version = self.backend.get(self.VERSION_KEY)
            if version is None:
                version = 1
                self.backend.set(self.VERSION_KEY, version, settings.RBAC_CACHE_TTL_SECONDS)
            return version
        except Exception:
            # Cache backend unavailable: disable caching (always miss).
            return 0

    def invalidate(self) -> None:
        """Invalidate every effective-permission result."""
        try:
            try:
                self.backend.incr(self.VERSION_KEY)
            except ValueError:
                self.backend.set(self.VERSION_KEY, 2, settings.RBAC_CACHE_TTL_SECONDS)
        except Exception:
            pass

    def key_for(self, user_id, tenant_id) -> str:
        return f"rbac:effective:{self.current_version()}:{user_id}:{tenant_id}"

    def get_effective(self, user_id, tenant_id) -> set | None:
        try:
            raw = self.backend.get(self.key_for(user_id, tenant_id))
            return set(raw) if raw else None
        except Exception:
            return None

    def set_effective(self, user_id, tenant_id, codes: set) -> None:
        with suppress(Exception):
            self.backend.set(self.key_for(user_id, tenant_id), list(codes), settings.RBAC_CACHE_TTL_SECONDS)
