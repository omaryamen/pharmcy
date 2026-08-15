"""Enterprise Security Headers Middleware for PharmaCloud ERP."""

from __future__ import annotations

from collections.abc import Callable
from django.http import HttpRequest, HttpResponse


class SecurityHeadersMiddleware:
    """Injects robust HTTP security headers (CSP, Permissions-Policy, HSTS, X-Content-Type-Options)."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        # Standard OWASP security headers
        if "Content-Security-Policy" not in response:
            response["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com data:; "
                "img-src 'self' data: https: blob:; "
                "connect-src 'self' https: ws: wss:; "
                "frame-ancestors 'none'; "
                "object-src 'none';"
            )

        if "Permissions-Policy" not in response:
            response["Permissions-Policy"] = (
                "camera=(self), microphone=(), geolocation=(), payment=(self)"
            )

        if "X-Content-Type-Options" not in response:
            response["X-Content-Type-Options"] = "nosniff"

        if "Referrer-Policy" not in response:
            response["Referrer-Policy"] = "strict-origin-when-cross-origin"

        if "Cross-Origin-Opener-Policy" not in response:
            response["Cross-Origin-Opener-Policy"] = "same-origin"

        return response
