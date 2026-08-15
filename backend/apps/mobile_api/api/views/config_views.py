"""REST API View for Mobile Remote App Configuration."""

from rest_framework import permissions, status, views
from rest_framework.request import Request
from rest_framework.response import Response

from apps.mobile_api.services import MobileAppConfigService


class MobileConfigView(views.APIView):
    permission_classes = [permissions.AllowAny]
    config_service = MobileAppConfigService()

    def get(self, request: Request) -> Response:
        platform = request.query_params.get("platform", "android")
        tenant = getattr(request, "tenant", None)
        cfg = self.config_service.get_mobile_config(platform=platform, tenant=tenant)
        return Response(cfg, status=status.HTTP_200_OK)
