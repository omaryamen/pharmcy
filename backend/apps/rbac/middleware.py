"""Permission-context middleware.

Initializes the request-scoped RBAC context early so that any layer (DRF
permissions, decorators, service code) computes the effective permission set
exactly once per request. The heavy lifting stays in the engine; this
middleware only pre-creates the ``_rbac_effective`` slot and exposes a small
convenience attribute.
"""

from __future__ import annotations


class PermissionContextMiddleware:
    """Attach ``request.rbac_effective`` (lazily populated) to every request."""

    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request):
        request._rbac_effective = None
        return self.get_response(request)
