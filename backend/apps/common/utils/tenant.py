"""Tenant resolution for the current request.

Caches the tenant id in Redis by identifier to keep header lookups fast and
cheap. Negative lookups are cached briefly to avoid DB hammering.
"""

from __future__ import annotations

import logging

from django.core.cache import cache

logger = logging.getLogger(__name__)

TENANT_CACHE_TIMEOUT = 300  # seconds
NEGATIVE_CACHE_TIMEOUT = 30  # seconds


def resolve_tenant(request):
    """Resolve ``request.tenant`` from ``X-Tenant-ID`` or ``X-Tenant-Slug``."""
    tenant_id_header = request.headers.get("X-Tenant-ID")
    tenant_slug_header = request.headers.get("X-Tenant-Slug")
    identifier = tenant_id_header or tenant_slug_header
    if not identifier:
        return None

    cache_key = f"tenant:resolve:{identifier}"
    cached = cache.get(cache_key)
    if cached is not None:
        if cached is False:
            return None
        from apps.core.models import Tenant

        return Tenant.objects.filter(pk=cached).first()

    from apps.core.models import Tenant

    tenant = None
    try:
        if tenant_id_header:
            tenant = Tenant.objects.filter(pk=identifier).first()
        else:
            tenant = Tenant.objects.filter(slug=tenant_slug_header).first()
    except (ValueError, TypeError):
        tenant = None

    cache.set(
        cache_key,
        tenant.pk if tenant else False,
        timeout=TENANT_CACHE_TIMEOUT if tenant else NEGATIVE_CACHE_TIMEOUT,
    )
    return tenant
