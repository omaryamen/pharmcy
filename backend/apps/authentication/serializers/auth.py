"""Serializers for the JWT session endpoints (login / refresh / verify / logout).

These are thin data contracts: they validate request shape and let the views
drive the corresponding services, which own business rules and raise typed
errors that the API exception handler maps to the response envelope.
"""

from __future__ import annotations

from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    remember_me = serializers.BooleanField(required=False, default=False)


class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField(write_only=True)


class VerifyTokenSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(write_only=True)
