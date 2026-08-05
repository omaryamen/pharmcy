"""Tenant identification middleware.

Resolves the tenant for the current request from the ``X-Tenant-ID`` (UUID)
or ``X-Tenant-Slug`` header and attaches it to ``request.tenant``.
Tenant membership enforcement is delegated to permissions
(``HasTenantContext`` / ``IsTenantMember``) and to the repository/service layer.
"""

from __future__ import annotations

from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

from apps.common.utils.tenant import resolve_tenant


class TenantIdentificationMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request.tenant = resolve_tenant(request)
        return self.get_response(request)
