"""Self-service registration endpoint."""

from __future__ import annotations

from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.common.api.viewsets import BaseAPIView
from apps.core.api.serializers import UserSerializer

from ...serializers import RegisterSerializer
from ...services import RegistrationService
from ...throttles import RegisterIPThrottle


class RegisterView(BaseAPIView):
    """Create a new account and (when required) send the verification code."""

    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [RegisterIPThrottle]
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = RegistrationService().register(
            email=serializer.validated_data["email"],
            first_name=serializer.validated_data["first_name"],
            last_name=serializer.validated_data.get("last_name", ""),
            phone=serializer.validated_data.get("phone", ""),
            password=serializer.validated_data["password"],
            request=request,
        )
        return Response(
            {
                "user": UserSerializer(result["user"]).data,
                "verification_sent": result["verification_sent"],
            },
            status=201,
        )
