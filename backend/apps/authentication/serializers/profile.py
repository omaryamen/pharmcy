"""Profile update serializer (editable subset of the User model)."""

from __future__ import annotations

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from rest_framework import serializers

from apps.core.models import User


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Fields the user may update on their own profile."""

    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone", "language", "timezone", "avatar")

    def validate_timezone(self, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exc:
            raise serializers.ValidationError("Unknown timezone.") from exc
        return value
