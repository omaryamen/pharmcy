"""Verification / password-reset serializers."""

from __future__ import annotations

from django.conf import settings
from rest_framework import serializers

from ..validators import validate_verification_code


class EmailVerificationRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)


class EmailVerificationConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    code = serializers.CharField(write_only=True)

    def validate_code(self, value: str) -> str:
        return validate_verification_code(value, length=settings.AUTH_VERIFICATION_CODE_LENGTH)


class PhoneVerificationRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(required=False, allow_blank=True)


class PhoneVerificationConfirmSerializer(serializers.Serializer):
    code = serializers.CharField(write_only=True)

    def validate_code(self, value: str) -> str:
        return validate_verification_code(value, length=settings.AUTH_VERIFICATION_CODE_LENGTH)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_code(self, value: str) -> str:
        return validate_verification_code(value, length=settings.AUTH_VERIFICATION_CODE_LENGTH)
