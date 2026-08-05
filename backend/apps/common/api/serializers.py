"""Base serializers: consistent read-only metadata fields across entities."""

from __future__ import annotations

from rest_framework import serializers


class BaseModelSerializer(serializers.ModelSerializer):
    """ModelSerializer exposing standard entity metadata as read-only."""

    id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class TenantAwareModelSerializer(BaseModelSerializer):
    """ModelSerializer that exposes the tenant id as read-only."""

    tenant = serializers.UUIDField(source="tenant_id", read_only=True)
