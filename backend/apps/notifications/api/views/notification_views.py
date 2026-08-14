"""REST API ViewSet for Notification Center (In-App notifications, read, mark read, unread count)."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.notifications.api.serializers import NotificationSerializer
from apps.notifications.models import Notification, NotificationStatus
from apps.notifications.selectors import NotificationSelector


class NotificationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    selector = NotificationSelector()

    def get_queryset(self):
        tenant = getattr(self.request.user, "tenant", None)
        return self.selector.get_user_notifications(
            tenant=tenant,
            user=self.request.user,
            status_filter=self.request.query_params.get("status"),
            priority_filter=self.request.query_params.get("priority"),
        )

    @action(detail=False, methods=["get"], url_path="unread")
    def unread_summary(self, request: Request) -> Response:
        tenant = getattr(request.user, "tenant", None)
        count = self.selector.get_unread_count(tenant, request.user)
        return Response({"unread_count": count}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="read")
    def mark_read(self, request: Request, pk: str = None) -> Response:
        notif = self.get_object()
        notif.mark_as_read()
        return Response(NotificationSerializer(notif).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="read-all")
    def mark_all_read(self, request: Request) -> Response:
        tenant = getattr(request.user, "tenant", None)
        qs = self.selector.get_user_notifications(tenant, request.user).filter(read_at__isnull=True)
        updated_count = qs.update(read_at=request.user.updated_at or request.user.date_joined, status=NotificationStatus.READ)
        return Response({"marked_read_count": updated_count}, status=status.HTTP_200_OK)
