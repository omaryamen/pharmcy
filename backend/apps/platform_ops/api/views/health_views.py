"""REST API View for Infrastructure Health Status and Probes."""

from rest_framework import status, views
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from apps.platform_ops.selectors import SystemHealthSelector


class SystemHealthView(views.APIView):
    permission_classes = [IsAdminUser]
    selector = SystemHealthSelector()

    def get(self, request: Request) -> Response:
        health_data = self.selector.perform_live_health_check()
        return Response(health_data, status=status.HTTP_200_OK)
