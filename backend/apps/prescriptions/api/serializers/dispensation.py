"""REST API serializers for Pharmacy Dispensing logs."""

from rest_framework import serializers

from apps.prescriptions.models import PrescriptionDispense, PrescriptionDispenseLine


class PrescriptionDispenseLineSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source="medicine.english_name", read_only=True)
    batch_number = serializers.CharField(source="batch.batch_number", read_only=True)
    storage_location_name = serializers.CharField(source="storage_location.name", read_only=True)

    class Meta:
        model = PrescriptionDispenseLine
        fields = [
            "id",
            "dispense",
            "prescription_line",
            "medicine",
            "medicine_name",
            "batch",
            "batch_number",
            "warehouse",
            "storage_location",
            "storage_location_name",
            "dispensed_quantity",
            "unit_price",
            "total_price",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class PrescriptionDispenseSerializer(serializers.ModelSerializer):
    lines = PrescriptionDispenseLineSerializer(many=True, read_only=True)
    rx_number = serializers.CharField(source="prescription.rx_number", read_only=True)
    customer_name = serializers.CharField(source="prescription.customer.english_name", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)

    class Meta:
        model = PrescriptionDispense
        fields = [
            "id",
            "dispense_number",
            "company",
            "branch",
            "warehouse",
            "warehouse_name",
            "prescription",
            "rx_number",
            "customer_name",
            "sales_invoice",
            "dispensed_at",
            "status",
            "dispensed_by",
            "pharmacist_notes",
            "lines",
            "created_at",
        ]
        read_only_fields = ["id", "dispense_number", "status", "created_at"]


class DispensingLineItemCreateSerializer(serializers.Serializer):
    prescription_line_id = serializers.UUIDField()
    dispensed_quantity = serializers.DecimalField(max_digits=14, decimal_places=4)
    storage_location_id = serializers.UUIDField(required=False, allow_null=True)
    batch_id = serializers.UUIDField(required=False, allow_null=True)
    unit_price = serializers.DecimalField(max_digits=14, decimal_places=4, required=False, allow_null=True)


class DispensePrescriptionCreateSerializer(serializers.Serializer):
    warehouse_id = serializers.UUIDField()
    dispensing_lines = DispensingLineItemCreateSerializer(many=True)
    pharmacist_notes = serializers.CharField(required=False, allow_blank=True, default="")
