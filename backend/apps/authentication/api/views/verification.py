"""Email / phone verification and password-reset endpoints."""

from __future__ import annotations

from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.common.api.viewsets import BaseAPIView
from apps.common.exceptions import ValidationFailedError
from apps.core.models import User

from ...exceptions import EmailAlreadyVerifiedError, InvalidVerificationCodeError
from ...serializers import (
    EmailVerificationConfirmSerializer,
    EmailVerificationRequestSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    PhoneVerificationConfirmSerializer,
    PhoneVerificationRequestSerializer,
)
from ...services import VerificationService
from ...throttles import PasswordResetEmailThrottle


class EmailVerificationRequestView(BaseAPIView):
    """Request a new email verification code.

    Authenticated users may omit ``email``; anonymous requests must provide it.
    Unknown emails receive the same generic response (no enumeration).
    """

    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetEmailThrottle]
    serializer_class = EmailVerificationRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        if not email and request.user.is_authenticated:
            email = request.user.email
        if not email:
            raise ValidationFailedError("An email address is required.", code="email_required", field="email")

        user = User.objects.filter(email=email.strip().lower()).first()
        if user is None:
            return Response({"sent": False})

        if user.email_verified:
            raise EmailAlreadyVerifiedError()
        VerificationService().request_email_verification(user=user, request=request)
        return Response({"sent": True})


class EmailVerificationConfirmView(BaseAPIView):
    """Verify an email address with the delivered code."""

    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = EmailVerificationConfirmSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        if not email and request.user.is_authenticated:
            email = request.user.email
        if not email:
            raise ValidationFailedError("An email address is required.", code="email_required", field="email")

        user = User.objects.filter(email=email.strip().lower()).first()
        if user is None:
            raise InvalidVerificationCodeError()

        VerificationService().verify_email(
            user=user,
            code=serializer.validated_data["code"],
            request=request,
        )
        return Response({"email_verified": True})


class PhoneVerificationRequestView(BaseAPIView):
    """Request a phone verification code for the authenticated user."""

    serializer_class = PhoneVerificationRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        VerificationService().request_phone_verification(user=request.user, request=request)
        return Response({"sent": True})


class PhoneVerificationConfirmView(BaseAPIView):
    """Verify the authenticated user's phone number."""

    serializer_class = PhoneVerificationConfirmSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        VerificationService().verify_phone(
            user=request.user,
            code=serializer.validated_data["code"],
            request=request,
        )
        return Response({"phone_verified": True})


class PasswordResetRequestView(BaseAPIView):
    """Request a password-reset code.

    Always returns the same message whether or not the email exists, so the
    endpoint cannot be used to enumerate registered accounts.
    """

    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetEmailThrottle]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        VerificationService().request_password_reset(
            email=serializer.validated_data["email"],
            request=request,
        )
        return Response({"message": "If the email is registered, a reset code has been sent."})


class PasswordResetConfirmView(BaseAPIView):
    """Reset a password with the delivered code."""

    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        VerificationService().reset_password(
            email=serializer.validated_data["email"],
            code=serializer.validated_data["code"],
            new_password=serializer.validated_data["new_password"],
            request=request,
        )
        return Response({"message": "Password has been reset."})
