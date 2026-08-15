"""DRF Serializer for OrderPrescription."""

from rest_framework import serializers
from apps.commerce.models import OrderPrescription


class OrderPrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderPrescription
        fields = [
            "id",
            "order",
            "customer",
            "file_url",
            "file_type",
            "review_status",
            "reviewed_by",
            "reviewed_at",
            "pharmacist_notes",
            "created_at",
        ]
        read_only_fields = ["id", "reviewed_by", "reviewed_at", "created_at"]
