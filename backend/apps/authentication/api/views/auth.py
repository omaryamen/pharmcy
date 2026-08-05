"""JWT session endpoints: login, refresh, verify, logout.

These replace the SimpleJWT default views so every flow is recorded in the
session ledger and the audit trail, with brute-force throttling applied.
"""

from __future__ import annotations

from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.common.api.viewsets import BaseAPIView
from apps.core.api.serializers import UserSerializer

from ...exceptions import InvalidTokenError
from ...serializers import LoginSerializer, LogoutSerializer, RefreshSerializer, VerifyTokenSerializer
from ...services import AuthService
from ...throttles import LoginEmailThrottle, LoginIPThrottle
from ...utils import parse_user_agent


class LoginView(BaseAPIView):
    """Obtain access + refresh tokens for valid credentials."""

    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [LoginEmailThrottle, LoginIPThrottle]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_agent = request.META.get("HTTP_USER_AGENT", "")
        device_name, device_type = parse_user_agent(user_agent)
        data = AuthService().login(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            request=request,
            remember_me=serializer.validated_data.get("remember_me", False),
            device_name=device_name,
            device_type=device_type,
            user_agent=user_agent,
        )

        return Response(
            {
                "access": data["access"],
                "refresh": data["refresh"],
                "user": UserSerializer(data["user"]).data,
                "session_id": data["session_id"],
                "expires_at": data["expires_at"],
            }
        )


class RefreshView(BaseAPIView):
    """Rotate the refresh token and return a fresh access token."""

    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = RefreshSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = AuthService().refresh(
            refresh_token=serializer.validated_data["refresh"],
            request=request,
        )
        return Response(
            {
                "access": data["access"],
                "refresh": data["refresh"],
                "session_id": data["session_id"],
                "expires_at": data["expires_at"],
            }
        )


class VerifyTokenView(BaseAPIView):
    """Confirm an access token is currently valid (not expired / revoked)."""

    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = VerifyTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not AuthService().verify_token(access_token=serializer.validated_data["token"]):
            raise InvalidTokenError()
        return Response({})


class LogoutView(BaseAPIView):
    """Revoke the supplied refresh token (idempotent)."""

    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = LogoutSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        AuthService().logout(
            refresh_token=serializer.validated_data["refresh"],
            request=request,
        )
        return Response({"message": "Logged out successfully."})
