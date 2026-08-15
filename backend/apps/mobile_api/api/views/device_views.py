"""REST API ViewSet for Device registration and push token management."""

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.mobile_api.api.serializers import DeviceSerializer
from apps.mobile_api.models import Device
from apps.mobile_api.services import DeviceRegistrationService


class DeviceViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    device_service = DeviceRegistrationService()

    @action(detail=False, methods=["post"], url_path="register")
    def register_device(self, request: Request) -> Response:
        dev_id = request.data.get("device_identifier")
        platform = request.data.get("platform", "android")
        push_token = request.data.get("push_token", "")
        app_v = request.data.get("app_version", "1.0.0")
        os_v = request.data.get("os_version", "")

        if not dev_id:
            return Response({"error": "device_identifier is required."}, status=status.HTTP_400_BAD_REQUEST)

        tenant = getattr(request, "tenant", None) or getattr(request.user, "tenant", None)
        if not tenant:
            return Response({"error": "Tenant context required."}, status=status.HTTP_400_BAD_REQUEST)

        device = self.device_service.register_device(
            user=request.user,
            tenant=tenant,
            device_identifier=dev_id,
            platform=platform,
            push_token=push_token,
            app_version=app_v,
            os_version=os_v,
        )
        return Response(DeviceSerializer(device).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="revoke")
    def revoke_device(self, request: Request) -> Response:
        dev_id = request.data.get("device_identifier")
        if not dev_id:
            return Response({"error": "device_identifier is required."}, status=status.HTTP_400_BAD_REQUEST)

        revoked = self.device_service.revoke_device(request.user, dev_id)
        if revoked:
            return Response({"message": f"Device '{dev_id}' revoked successfully."}, status=status.HTTP_200_OK)
        return Response({"error": "Device not found."}, status=status.HTTP_404_NOT_FOUND)
