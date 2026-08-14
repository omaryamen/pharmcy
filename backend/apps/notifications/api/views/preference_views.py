"""REST API ViewSet for NotificationPreference management."""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.notifications.api.serializers import NotificationPreferenceSerializer
from apps.notifications.models import NotificationPreference
from apps.notifications.selectors import NotificationSelector


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationPreferenceSerializer
    selector = NotificationSelector()

    def get_queryset(self):
        tenant = getattr(self.request.user, "tenant", None)
        return self.selector.get_user_preferences(tenant, self.request.user)

    def perform_create(self, serializer):
        tenant = getattr(self.request.user, "tenant", None)
        serializer.save(tenant=tenant, user=self.request.user)
