"""Root URL configuration for PharmaCloud ERP."""

from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpRequest, JsonResponse
from django.urls import include, path
from django.utils import timezone
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from apps.common.utils.context import get_request_id

urlpatterns = [
    path("admin/", admin.site.urls),
    # Versioned API v1
    path("api/v1/", include("apps.core.api.urls")),
    path("api/v1/", include("apps.authentication.api.urls")),
    path("api/v1/", include("apps.rbac.api.urls")),
    # OpenAPI schema & documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]


def _envelope_error(request: HttpRequest, status_code: int, message: str, code: str) -> JsonResponse:
    payload = {
        "success": False,
        "status_code": status_code,
        "message": message,
        "data": None,
        "errors": [{"code": code, "message": message}],
        "meta": {
            "request_id": get_request_id(),
            "timestamp": timezone.now().isoformat(),
            "version": "v1",
        },
    }
    return JsonResponse(payload, encoder=DjangoJSONEncoder, status=status_code)


def api_404(request: HttpRequest, exception=None) -> JsonResponse:
    """Unmatched routes (and any other 404) return the envelope as JSON."""
    return _envelope_error(request, 404, "Not Found", "not_found")


def api_500(request: HttpRequest) -> JsonResponse:
    return _envelope_error(request, 500, "Internal Server Error", "internal_server_error")


handler404 = "config.urls.api_404"
handler500 = "config.urls.api_500"

if settings.DEBUG:
    # Serve uploaded media during development only.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
