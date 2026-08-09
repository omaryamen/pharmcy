"""Serializers for Batch / Lot entity and management lifecycle."""

from __future__ import annotations

from rest_framework import serializers

from apps.companies.models import Company
from apps.inventory.models import Batch
from apps.medicines.models import Medicine
from apps.suppliers.models import Supplier


class BatchSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source="medicine.name", read_only=True)
    supplier_name = serializers.CharField(source="supplier.legal_name", read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Batch
        fields = [
            "id",
            "tenant",
            "company",
            "medicine",
            "medicine_name",
            "supplier",
            "supplier_name",
            "batch_number",
            "lot_number",
            "manufacturing_date",
            "expiry_date",
            "registration_number",
            "country_of_origin",
            "status",
            "unit_cost",
            "selling_price",
            "initial_quantity",
            "current_quantity",
            "storage_requirements",
            "is_expired",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "tenant", "medicine_name", "supplier_name", "is_expired", "created_at", "updated_at"]


class BatchDetailSerializer(BatchSerializer):
    inventory_count = serializers.IntegerField(source="inventory_items.count", read_only=True)

    class Meta(BatchSerializer.Meta):
        fields = BatchSerializer.Meta.fields + ["inventory_count"]


class BatchCreateSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    medicine = serializers.PrimaryKeyRelatedField(queryset=Medicine.objects.all())
    supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Batch
        fields = [
            "company",
            "medicine",
            "supplier",
            "batch_number",
            "lot_number",
            "manufacturing_date",
            "expiry_date",
            "registration_number",
            "country_of_origin",
            "status",
            "unit_cost",
            "selling_price",
            "initial_quantity",
            "storage_requirements",
            "notes",
        ]


class BatchUpdateSerializer(serializers.ModelSerializer):
    supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Batch
        fields = [
            "supplier",
            "lot_number",
            "manufacturing_date",
            "expiry_date",
            "registration_number",
            "country_of_origin",
            "unit_cost",
            "selling_price",
            "storage_requirements",
            "notes",
        ]
