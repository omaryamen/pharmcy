"""Medicine serializers for Master Data management."""

from __future__ import annotations

from rest_framework import serializers

from apps.medicines.models import Medicine


class MedicineSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.legal_name", read_only=True)
    category_ref_name = serializers.CharField(source="category_ref.name_en", read_only=True)
    manufacturer_ref_name = serializers.CharField(source="manufacturer_ref.display_name", read_only=True)

    class Meta:
        model = Medicine
        fields = [
            "id",
            "company",
            "company_name",
            "code",
            "sku",
            "barcode",
            "qr_code",
            "arabic_name",
            "english_name",
            "generic_name",
            "scientific_name",
            "brand_name",
            "commercial_name",
            "short_name",
            "slug",
            "search_keywords",
            "status",
            "therapeutic_class",
            "pharmacological_class",
            "atc_code",
            "category",
            "category_ref",
            "category_ref_name",
            "prescription_type",
            "controlled_drug_schedule",
            "medicine_type",
            "drug_classification",
            "drug_family",
            "manufacturer_name",
            "manufacturer_ref",
            "manufacturer_ref_name",
            "country_of_origin",
            "marketing_company",
            "registration_authority",
            "registration_number",
            "approval_date",
            "expiry_of_registration",
            "dosage_form",
            "dosage_form_ref",
            "strength",
            "strength_unit",
            "concentration",
            "route_of_administration",
            "package_size",
            "package_type",
            "unit_of_measure",
            "unit_of_measure_ref",
            "minimum_dispensing_unit",
            "indications",
            "contraindications",
            "warnings",
            "precautions",
            "side_effects",
            "storage_conditions",
            "pregnancy_category",
            "lactation_warning",
            "breastfeeding_safety",
            "pediatric_usage",
            "geriatric_usage",
            "maximum_daily_dose",
            "is_high_alert",
            "is_lasa",
            "is_narcotic",
            "is_psychotropic",
            "is_refrigerated",
            "is_hazardous",
            "is_cold_chain_required",
            "is_light_sensitive",
            "is_controlled_substance",
            "default_purchase_price",
            "default_selling_price",
            "suggested_retail_price",
            "tax_category",
            "tax_category_ref",
            "default_profit_margin",
            "is_insurance_eligible",
            "is_discount_eligible",
            "is_return_eligible",
            "is_price_editable",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]


class MedicineCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = [
            "company",
            "code",
            "sku",
            "barcode",
            "qr_code",
            "arabic_name",
            "english_name",
            "generic_name",
            "scientific_name",
            "brand_name",
            "commercial_name",
            "short_name",
            "description",
            "image",
            "therapeutic_class",
            "pharmacological_class",
            "atc_code",
            "category",
            "category_ref",
            "prescription_type",
            "controlled_drug_schedule",
            "medicine_type",
            "drug_classification",
            "drug_family",
            "manufacturer_name",
            "manufacturer_ref",
            "country_of_origin",
            "marketing_company",
            "registration_authority",
            "registration_number",
            "approval_date",
            "expiry_of_registration",
            "dosage_form",
            "dosage_form_ref",
            "strength",
            "strength_unit",
            "concentration",
            "route_of_administration",
            "package_size",
            "package_type",
            "unit_of_measure",
            "unit_of_measure_ref",
            "minimum_dispensing_unit",
            "indications",
            "contraindications",
            "warnings",
            "precautions",
            "side_effects",
            "storage_conditions",
            "pregnancy_category",
            "lactation_warning",
            "breastfeeding_safety",
            "pediatric_usage",
            "geriatric_usage",
            "maximum_daily_dose",
            "is_high_alert",
            "is_lasa",
            "is_narcotic",
            "is_psychotropic",
            "is_refrigerated",
            "is_hazardous",
            "is_cold_chain_required",
            "is_light_sensitive",
            "is_controlled_substance",
            "default_purchase_price",
            "default_selling_price",
            "suggested_retail_price",
            "tax_category",
            "tax_category_ref",
            "default_profit_margin",
            "is_insurance_eligible",
            "is_discount_eligible",
            "is_return_eligible",
            "is_price_editable",
        ]


class MedicineDetailSerializer(MedicineSerializer):
    pass


class MedicineImportItemSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
    sku = serializers.CharField(max_length=100)
    arabic_name = serializers.CharField(max_length=255)
    english_name = serializers.CharField(max_length=255)
    scientific_name = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    barcode = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    dosage_form = serializers.CharField(max_length=100, required=False, default="Tablet")
    strength = serializers.CharField(max_length=50, required=False, allow_blank=True, default="")
    default_purchase_price = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=0.00)
    default_selling_price = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=0.00)


class MedicineImportSerializer(serializers.Serializer):
    items = serializers.ListField(child=MedicineImportItemSerializer())
