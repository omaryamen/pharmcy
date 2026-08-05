"""Security audit trail endpoint."""

from __future__ import annotations

from rest_framework.response import Response

from apps.common.api.viewsets import BaseAPIView

from ...serializers import SecurityEventSerializer
from ...services import SecurityEventService


class SecurityEventListView(BaseAPIView):
    """List the authenticated user's recent security events."""

    def get(self, request):
        events = SecurityEventService().list_events(user=request.user, limit=100)
        return Response(SecurityEventSerializer(events, many=True).data)
