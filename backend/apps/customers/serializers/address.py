"""Serializers for Customer Address sub-resource."""

from __future__ import annotations

from rest_framework import serializers

from apps.customers.models import CustomerAddress


class CustomerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAddress
        fields = [
            "id",
            "customer",
            "address_type",
            "is_primary",
            "is_default_billing",
            "is_default_delivery",
            "country",
            "state",
            "city",
            "district",
            "street",
            "building",
            "postal_code",
            "additional_info",
            "latitude",
            "longitude",
            "google_maps_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "customer", "created_at", "updated_at"]
