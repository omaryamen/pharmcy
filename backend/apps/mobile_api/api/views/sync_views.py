"""REST API ViewSet for Mobile Offline Sync."""

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.mobile_api.api.serializers import MobileSyncQueueSerializer
from apps.mobile_api.models import MobileSyncQueue
from apps.mobile_api.services import MobileSyncService


class MobileSyncViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    sync_service = MobileSyncService()

    @action(detail=False, methods=["post"], url_path="push")
    def push_offline_mutation(self, request: Request) -> Response:
        entity_type = request.data.get("entity_type")
        mutation_id = request.data.get("client_mutation_id")
        operation = request.data.get("operation", "create")
        payload = request.data.get("payload", {})
        client_v = int(request.data.get("client_version", 1))

        if not entity_type or not mutation_id:
            return Response({"error": "entity_type and client_mutation_id are required."}, status=status.HTTP_400_BAD_REQUEST)

        tenant = getattr(request, "tenant", None) or getattr(request.user, "tenant", None)
        if not tenant:
            return Response({"error": "Tenant context required."}, status=status.HTTP_400_BAD_REQUEST)

        sync_item = self.sync_service.process_sync_item(
            tenant=tenant,
            user=request.user,
            entity_type=entity_type,
            client_mutation_id=mutation_id,
            operation=operation,
            payload=payload,
            client_version=client_v,
        )
        return Response(MobileSyncQueueSerializer(sync_item).data, status=status.HTTP_200_OK)
