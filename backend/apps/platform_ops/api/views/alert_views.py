"""REST API ViewSet for Platform Alerts (Resolve, View)."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from apps.platform_ops.api.serializers import PlatformAlertSerializer
from apps.platform_ops.models import PlatformAlert


class PlatformAlertViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = PlatformAlertSerializer
    queryset = PlatformAlert.objects.all().order_by("-created_at")

    @action(detail=True, methods=["post"], url_path="resolve")
    def resolve(self, request: Request, pk: str = None) -> Response:
        alert = self.get_object()
        alert.resolve(request.user)
        return Response(PlatformAlertSerializer(alert).data, status=status.HTTP_200_OK)
