"""REST API View for Super Admin Platform Overview Dashboard."""

from rest_framework import status, views
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from apps.platform_ops.selectors import PlatformOverviewSelector


class PlatformOverviewView(views.APIView):
    permission_classes = [IsAdminUser]
    selector = PlatformOverviewSelector()

    def get(self, request: Request) -> Response:
        overview = self.selector.get_platform_overview()
        return Response(overview, status=status.HTTP_200_OK)
