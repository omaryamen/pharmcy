"""Medicine ViewSet for Enterprise Master Data management."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.medicines.permissions import CanManageMedicines, CanViewMedicines
from apps.medicines.selectors import MedicineSelector
from apps.medicines.serializers import (
    MedicineCreateSerializer,
    MedicineDetailSerializer,
    MedicineImportSerializer,
    MedicineSerializer,
)
from apps.medicines.services import MedicineService


@extend_schema_view(
    list=extend_schema(tags=["medicines"], summary="List medicine master catalog entries"),
    retrieve=extend_schema(tags=["medicines"], summary="Retrieve medicine master details"),
    create=extend_schema(tags=["medicines"], summary="Create new medicine master entry"),
)
class MedicineViewSet(viewsets.ModelViewSet):
    serializer_class = MedicineSerializer
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.selector = MedicineSelector()
        self.service = MedicineService()

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy", "activate", "deactivate", "restore", "import_medicines"}:
            return [(IsAuthenticatedAndActive & HasTenantContext & CanManageMedicines)()]
        return [(IsAuthenticatedAndActive & HasTenantContext & CanViewMedicines)()]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if not tenant:
            return self.selector.repository.model.objects.none()

        def parse_bool(val):
            if val is None:
                return None
            return str(val).lower() in {"true", "1", "yes"}

        return self.selector.list_medicines(
            tenant=tenant,
            company_id=self.request.query_params.get("company"),
            category=self.request.query_params.get("category"),
            dosage_form=self.request.query_params.get("dosage_form"),
            prescription_type=self.request.query_params.get("prescription_type"),
            status=self.request.query_params.get("status"),
            is_high_alert=parse_bool(self.request.query_params.get("is_high_alert")),
            is_refrigerated=parse_bool(self.request.query_params.get("is_refrigerated")),
            is_cold_chain_required=parse_bool(self.request.query_params.get("is_cold_chain_required")),
            search=self.request.query_params.get("search"),
        )

    def get_serializer_class(self):
        if self.action == "create":
            return MedicineCreateSerializer
        if self.action == "retrieve":
            return MedicineDetailSerializer
        if self.action == "import_medicines":
            return MedicineImportSerializer
        return MedicineSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        medicine = self.service.create_medicine(
            tenant=request.tenant,
            company=data.get("company"),
            code=data["code"],
            sku=data["sku"],
            arabic_name=data["arabic_name"],
            english_name=data["english_name"],
            barcode=data.get("barcode", ""),
            qr_code=data.get("qr_code", ""),
            generic_name=data.get("generic_name", ""),
            scientific_name=data.get("scientific_name", ""),
            brand_name=data.get("brand_name", ""),
            commercial_name=data.get("commercial_name", ""),
            short_name=data.get("short_name", ""),
            description=data.get("description", ""),
            image=data.get("image"),
            therapeutic_class=data.get("therapeutic_class", ""),
            pharmacological_class=data.get("pharmacological_class", ""),
            atc_code=data.get("atc_code", ""),
            category=data.get("category", ""),
            prescription_type=data.get("prescription_type", "prescription_only"),
            controlled_drug_schedule=data.get("controlled_drug_schedule", ""),
            medicine_type=data.get("medicine_type", "allopathic"),
            drug_classification=data.get("drug_classification", ""),
            drug_family=data.get("drug_family", ""),
            manufacturer_name=data.get("manufacturer_name", ""),
            country_of_origin=data.get("country_of_origin", "Yemen"),
            marketing_company=data.get("marketing_company", ""),
            registration_authority=data.get("registration_authority", ""),
            registration_number=data.get("registration_number", ""),
            approval_date=data.get("approval_date"),
            expiry_of_registration=data.get("expiry_of_registration"),
            dosage_form=data.get("dosage_form", "Tablet"),
            strength=data.get("strength", ""),
            strength_unit=data.get("strength_unit", ""),
            concentration=data.get("concentration", ""),
            route_of_administration=data.get("route_of_administration", "Oral"),
            package_size=data.get("package_size", 1),
            package_type=data.get("package_type", "Box"),
            unit_of_measure=data.get("unit_of_measure", "Pcs"),
            minimum_dispensing_unit=data.get("minimum_dispensing_unit", "Pcs"),
            indications=data.get("indications", ""),
            contraindications=data.get("contraindications", ""),
            warnings=data.get("warnings", ""),
            precautions=data.get("precautions", ""),
            side_effects=data.get("side_effects", ""),
            storage_conditions=data.get("storage_conditions", "Store below 25°C in a dry place"),
            pregnancy_category=data.get("pregnancy_category", "N"),
            lactation_warning=data.get("lactation_warning", ""),
            breastfeeding_safety=data.get("breastfeeding_safety", ""),
            pediatric_usage=data.get("pediatric_usage", ""),
            geriatric_usage=data.get("geriatric_usage", ""),
            maximum_daily_dose=data.get("maximum_daily_dose", ""),
            is_high_alert=data.get("is_high_alert", False),
            is_lasa=data.get("is_lasa", False),
            is_narcotic=data.get("is_narcotic", False),
            is_psychotropic=data.get("is_psychotropic", False),
            is_refrigerated=data.get("is_refrigerated", False),
            is_hazardous=data.get("is_hazardous", False),
            is_cold_chain_required=data.get("is_cold_chain_required", False),
            is_light_sensitive=data.get("is_light_sensitive", False),
            is_controlled_substance=data.get("is_controlled_substance", False),
            default_purchase_price=data.get("default_purchase_price", 0.00),
            default_selling_price=data.get("default_selling_price", 0.00),
            suggested_retail_price=data.get("suggested_retail_price", 0.00),
            tax_category=data.get("tax_category", "standard"),
            default_profit_margin=data.get("default_profit_margin", 0.00),
            is_insurance_eligible=data.get("is_insurance_eligible", True),
            is_discount_eligible=data.get("is_discount_eligible", True),
            is_return_eligible=data.get("is_return_eligible", True),
            is_price_editable=data.get("is_price_editable", True),
        )

        return Response(MedicineDetailSerializer(medicine).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, pk=None):
        medicine = self.get_object()
        updated = self.service.activate_medicine(medicine)
        return Response(MedicineSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate(self, request, pk=None):
        medicine = self.get_object()
        updated = self.service.deactivate_medicine(medicine)
        return Response(MedicineSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        medicine = self.get_object()
        updated = self.service.restore_medicine(medicine)
        return Response(MedicineSerializer(updated).data)

    @action(detail=False, methods=["get"], url_path="lookup/barcode")
    def lookup_barcode(self, request):
        barcode = request.query_params.get("barcode")
        if not barcode:
            return Response({"detail": "barcode query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        medicine = self.service.lookup_by_barcode(request.tenant, barcode)
        return Response(MedicineSerializer(medicine).data)

    @action(detail=False, methods=["get"], url_path="lookup/sku")
    def lookup_sku(self, request):
        sku = request.query_params.get("sku")
        if not sku:
            return Response({"detail": "sku query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        medicine = self.service.lookup_by_sku(request.tenant, sku)
        return Response(MedicineSerializer(medicine).data)

    @action(detail=False, methods=["post"], url_path="import")
    def import_medicines(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = self.service.bulk_import_medicines(request.tenant, None, serializer.validated_data["items"])
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="export")
    def export_medicines(self, request):
        qs = self.get_queryset()
        data = MedicineSerializer(qs, many=True).data
        return Response({"count": len(data), "medicines": data})

    def destroy(self, request, *args, **kwargs):
        medicine = self.get_object()
        self.service.soft_delete_medicine(medicine)
        return Response(status=status.HTTP_204_NO_CONTENT)
