"""REST API serializers for BatchRecall entities."""

from rest_framework import serializers

from apps.alerts.models import BatchRecall


class BatchRecallSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source="company.legal_name")
    medicine_name = serializers.ReadOnlyField(source="medicine.english_name")
    medicine_sku = serializers.ReadOnlyField(source="medicine.sku")
    batch_number = serializers.ReadOnlyField(source="batch.batch_number")
    initiated_by_name = serializers.ReadOnlyField(source="initiated_by.get_full_name")
    completed_by_name = serializers.ReadOnlyField(source="completed_by.get_full_name")

    class Meta:
        model = BatchRecall
        fields = [
            "id",
            "recall_number",
            "company",
            "company_name",
            "medicine",
            "medicine_name",
            "medicine_sku",
            "batch",
            "batch_number",
            "recall_type",
            "recall_class",
            "status",
            "reason",
            "action_required",
            "regulatory_reference",
            "quarantined_quantity",
            "disposed_quantity",
            "returned_quantity",
            "initiated_at",
            "initiated_by",
            "initiated_by_name",
            "completed_at",
            "completed_by",
            "completed_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "recall_number",
            "quarantined_quantity",
            "initiated_at",
            "initiated_by",
            "completed_at",
            "completed_by",
            "created_at",
            "updated_at",
        ]


class RecallInitiateSerializer(serializers.Serializer):
    auto_quarantine = serializers.BooleanField(default=True)


class RecallCompleteSerializer(serializers.Serializer):
    disposed_quantity = serializers.DecimalField(max_digits=14, decimal_places=4, default=0)
    returned_quantity = serializers.DecimalField(max_digits=14, decimal_places=4, default=0)
