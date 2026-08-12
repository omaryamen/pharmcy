"""REST API serializers for Prescription document management."""

from rest_framework import serializers

from apps.prescriptions.models import Prescription, PrescriptionLine


class PrescriptionLineSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source="medicine.english_name", read_only=True)
    substituted_medicine_name = serializers.CharField(source="substituted_medicine.english_name", read_only=True, default=None)

    class Meta:
        model = PrescriptionLine
        fields = [
            "id",
            "prescription",
            "medicine",
            "medicine_name",
            "prescribed_quantity",
            "dispensed_quantity",
            "dosage",
            "frequency",
            "duration_days",
            "instructions",
            "refills_allowed",
            "refills_remaining",
            "status",
            "is_substituted",
            "substituted_medicine",
            "substituted_medicine_name",
            "substitution_reason",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class PrescriptionSerializer(serializers.ModelSerializer):
    lines = PrescriptionLineSerializer(many=True, read_only=True)
    company_name = serializers.CharField(source="company.legal_name", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    customer_name = serializers.CharField(source="customer.english_name", read_only=True)

    class Meta:
        model = Prescription
        fields = [
            "id",
            "rx_number",
            "company",
            "company_name",
            "branch",
            "branch_name",
            "customer",
            "customer_name",
            "rx_date",
            "expiry_date",
            "status",
            "rx_type",
            "doctor_name",
            "doctor_license_number",
            "clinic_hospital_name",
            "diagnosis_code",
            "diagnosis_description",
            "is_verified",
            "verified_by",
            "verified_at",
            "dispensed_at",
            "dispensed_by",
            "notes",
            "lines",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "rx_number", "status", "is_verified", "created_at", "updated_at"]


class PrescriptionLineCreateSerializer(serializers.Serializer):
    medicine_id = serializers.UUIDField()
    prescribed_quantity = serializers.DecimalField(max_digits=14, decimal_places=4, default=1.0)
    dosage = serializers.CharField(required=False, allow_blank=True, default="")
    frequency = serializers.CharField(required=False, allow_blank=True, default="")
    duration_days = serializers.IntegerField(required=False, default=1)
    instructions = serializers.CharField(required=False, allow_blank=True, default="")
    refills_allowed = serializers.IntegerField(required=False, default=0)
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class PrescriptionCreateSerializer(serializers.Serializer):
    company_id = serializers.UUIDField()
    branch_id = serializers.UUIDField()
    customer_id = serializers.UUIDField()
    rx_date = serializers.DateField()
    expiry_date = serializers.DateField()
    doctor_name = serializers.CharField()
    doctor_license_number = serializers.CharField(required=False, allow_blank=True, default="")
    clinic_hospital_name = serializers.CharField(required=False, allow_blank=True, default="")
    rx_type = serializers.CharField(required=False, default="regular")
    diagnosis_code = serializers.CharField(required=False, allow_blank=True, default="")
    diagnosis_description = serializers.CharField(required=False, allow_blank=True, default="")
    idempotency_key = serializers.CharField(required=False, allow_blank=True, default="")
    notes = serializers.CharField(required=False, allow_blank=True, default="")
    lines = PrescriptionLineCreateSerializer(many=True)
