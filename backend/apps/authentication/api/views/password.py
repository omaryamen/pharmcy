"""Password change endpoint."""

from __future__ import annotations

from rest_framework.response import Response

from apps.common.api.viewsets import BaseAPIView

from ...serializers import ChangePasswordSerializer
from ...services import PasswordService


class ChangePasswordView(BaseAPIView):
    """Change the authenticated user's password.

    Revokes every live session (including this one); the client must sign in
    again afterwards.
    """

    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        PasswordService().change_password(
            user=request.user,
            current_password=serializer.validated_data["current_password"],
            new_password=serializer.validated_data["new_password"],
            request=request,
        )
        return Response({"message": "Password changed. All sessions were revoked — please sign in again."})
