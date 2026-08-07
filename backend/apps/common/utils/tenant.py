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
    """Resolve ``request.tenant`` from ``X-Tenant-ID``, ``X-Tenant-Slug``, or Host domain/subdomain."""
    tenant_id_header = request.headers.get("X-Tenant-ID")
    tenant_slug_header = request.headers.get("X-Tenant-Slug")
    identifier = tenant_id_header or tenant_slug_header

    # Extract host domain if header is absent
    host_identifier = None
    if not identifier:
        host = request.get_host().split(":")[0].lower()
        if host and host not in {"localhost", "127.0.0.1", "0.0.0.0"}:
            # Subdomain resolution (e.g., demo.pharmacloud.local -> demo)
            parts = host.split(".")
            if len(parts) >= 3:
                host_identifier = parts[0]
            else:
                host_identifier = host  # custom domain e.g. pharmacy.com

    identifier = identifier or host_identifier
    if not identifier:
        return None

    cache_key = f"tenant:resolve:{identifier}"
    cached = cache.get(cache_key)
    if cached is not None:
        if cached is False:
            return None
        from apps.core.models import Tenant

        return Tenant.objects.filter(pk=cached, is_deleted=False).first()

    from apps.core.models import Tenant

    tenant = None
    try:
        if tenant_id_header:
            tenant = Tenant.objects.filter(pk=identifier, is_deleted=False).first()
        elif tenant_slug_header or host_identifier:
            slug_candidate = tenant_slug_header or host_identifier
            tenant = Tenant.objects.filter(slug=slug_candidate, is_deleted=False).first()
            if not tenant:
                # Custom domain lookup
                try:
                    from apps.tenants.models import TenantDomain

                    domain_obj = TenantDomain.objects.filter(domain_name=slug_candidate, is_verified=True).first()
                    if domain_obj:
                        tenant = domain_obj.tenant
                except Exception:
                    tenant = None
    except (ValueError, TypeError):
        tenant = None

    cache.set(
        cache_key,
        tenant.pk if tenant else False,
        timeout=TENANT_CACHE_TIMEOUT if tenant else NEGATIVE_CACHE_TIMEOUT,
    )
    return tenant

