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
    path("api/v1/tenants/", include("apps.tenants.api.urls")),
    path("api/v1/companies/", include("apps.companies.api.urls")),
    path("api/v1/branches/", include("apps.branches.api.urls")),
    path("api/v1/users/", include("apps.users.api.urls")),
    path("api/v1/medicines/", include("apps.medicines.api.urls")),
    path("api/v1/references/", include("apps.references.api.urls")),
    path("api/v1/suppliers/", include("apps.suppliers.api.urls")),
    path("api/v1/customers/", include("apps.customers.api.urls")),
    path("api/v1/warehouses/", include("apps.warehouses.api.urls")),
    path("api/v1/storage-locations/", include("apps.warehouses.api.urls_locations")),
    path("api/v1/inventory/", include("apps.inventory.api.urls")),
    path("api/v1/batches/", include("apps.inventory.api.urls_batches")),
    path("api/v1/inventory-transactions/", include("apps.inventory.api.urls_transactions")),
    path("api/v1/", include("apps.stock_movement.api.urls")),
    path("api/v1/", include("apps.stock_adjustment.api.urls")),
    path("api/v1/", include("apps.stock_transfer.api.urls")),
    path("api/v1/", include("apps.alerts.api.urls")),
    path("api/v1/", include("apps.procurement.api.urls")),
    path("api/v1/", include("apps.goods_receipt.api.urls")),
    path("api/v1/", include("apps.purchase_returns.api.urls")),
    path("api/v1/", include("apps.accounts_payable.api.urls")),
    path("api/v1/", include("apps.sales.api.urls")),
    path("api/v1/", include("apps.sales_returns.api.urls")),
    path("api/v1/", include("apps.prescriptions.api.urls")),
    path("api/v1/", include("apps.accounts_receivable.api.urls")),
    path("api/v1/", include("apps.general_ledger.api.urls")),
    path("api/v1/", include("apps.cash_and_bank.api.urls")),
    path("api/v1/", include("apps.expenses.api.urls")),
    path("api/v1/", include("apps.reports.api.urls")),
    path("api/v1/", include("apps.notifications.api.urls")),
    path("api/v1/", include("apps.saas.api.urls")),
    path("api/v1/", include("apps.platform_ops.api.urls")),
    path("api/v1/", include("apps.commerce.api.urls")),
    path("api/v1/", include("apps.mobile_api.api.urls")),
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
