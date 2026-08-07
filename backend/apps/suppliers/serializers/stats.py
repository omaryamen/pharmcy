"""Supplier statistics serializer."""

from __future__ import annotations

from rest_framework import serializers


class SupplierStatsSerializer(serializers.Serializer):
    tenant_id = serializers.UUIDField()
    total_suppliers = serializers.IntegerField()
    active_suppliers = serializers.IntegerField()
    preferred_suppliers = serializers.IntegerField()
    blacklisted_suppliers = serializers.IntegerField()
