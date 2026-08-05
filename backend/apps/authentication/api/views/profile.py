"""Profile (me) endpoints: read and update the authenticated user."""

from __future__ import annotations

from rest_framework.response import Response

from apps.common.api.viewsets import BaseAPIView
from apps.core.api.serializers import UserSerializer

from ...models import SecurityEventType
from ...serializers.profile import ProfileUpdateSerializer
from ...services import SecurityEventService
from ...services.events import record_event


class ProfileView(BaseAPIView):
    """Read the current user's profile and update editable preferences."""

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        record_event(
            SecurityEventService().events,
            user=request.user,
            event_type=SecurityEventType.PROFILE_UPDATED,
            request=request,
            details=serializer.validated_data,
        )
        return Response(UserSerializer(request.user).data)
