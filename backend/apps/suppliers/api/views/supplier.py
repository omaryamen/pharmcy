"""Supplier ViewSet for Enterprise Vendor Management APIs."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.suppliers.permissions import CanManageSuppliers, CanViewSuppliers
from apps.suppliers.selectors import SupplierSelector
from apps.suppliers.serializers import (
    SupplierCreateSerializer,
    SupplierDetailSerializer,
    SupplierImportSerializer,
    SupplierSerializer,
)
from apps.suppliers.services import SupplierService


@extend_schema_view(
    list=extend_schema(tags=["suppliers"], summary="List suppliers for active tenant"),
    retrieve=extend_schema(tags=["suppliers"], summary="Retrieve supplier details"),
    create=extend_schema(tags=["suppliers"], summary="Create new supplier profile"),
)
class SupplierViewSet(viewsets.ModelViewSet):
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.selector = SupplierSelector()
        self.service = SupplierService()

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy", "activate", "suspend", "blacklist", "restore", "import_suppliers"}:
            return [(IsAuthenticatedAndActive & HasTenantContext & CanManageSuppliers)()]
        return [(IsAuthenticatedAndActive & HasTenantContext & CanViewSuppliers)()]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if not tenant:
            return self.selector.repository.model.objects.none()

        def parse_bool(val):
            if val is None:
                return None
            return str(val).lower() in {"true", "1", "yes"}

        return self.selector.list_suppliers(
            tenant=tenant,
            company_id=self.request.query_params.get("company"),
            supplier_type=self.request.query_params.get("supplier_type"),
            risk_level=self.request.query_params.get("risk_level"),
            status=self.request.query_params.get("status"),
            is_preferred=parse_bool(self.request.query_params.get("is_preferred")),
            is_blacklisted=parse_bool(self.request.query_params.get("is_blacklisted")),
            search=self.request.query_params.get("search"),
        )

    def get_serializer_class(self):
        if self.action == "create":
            return SupplierCreateSerializer
        if self.action == "retrieve":
            return SupplierDetailSerializer
        if self.action == "import_suppliers":
            return SupplierImportSerializer
        return SupplierSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        supplier = self.service.create_supplier(
            tenant=request.tenant,
            company=data.get("company"),
            code=data["code"],
            legal_name=data["legal_name"],
            display_name=data.get("display_name", ""),
            supplier_type=data.get("supplier_type", "distributor"),
            supplier_category=data.get("supplier_category", "Pharmaceuticals"),
            registration_number=data.get("registration_number", ""),
            tax_number=data.get("tax_number", ""),
            vat_number=data.get("vat_number", ""),
            logo=data.get("logo"),
            website=data.get("website", ""),
            description=data.get("description", ""),
            primary_contact_name=data.get("primary_contact_name", ""),
            secondary_contact_name=data.get("secondary_contact_name", ""),
            phone=data.get("phone", ""),
            mobile=data.get("mobile", ""),
            whatsapp=data.get("whatsapp", ""),
            email=data.get("email", ""),
            support_email=data.get("support_email", ""),
            fax=data.get("fax", ""),
            country=data.get("country", "Yemen"),
            state=data.get("state", ""),
            city=data.get("city", "Sanaa"),
            district=data.get("district", ""),
            postal_code=data.get("postal_code", ""),
            street=data.get("street", ""),
            building=data.get("building", ""),
            google_maps_url=data.get("google_maps_url", ""),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            default_currency=data.get("default_currency", "YER"),
            payment_terms=data.get("payment_terms", "Net 30"),
            credit_limit=data.get("credit_limit", 0.00),
            opening_balance=data.get("opening_balance", 0.00),
            preferred_payment_method=data.get("preferred_payment_method", "bank_transfer"),
            bank_name=data.get("bank_name", ""),
            bank_account=data.get("bank_account", ""),
            iban=data.get("iban", ""),
            swift=data.get("swift", ""),
            tax_category=data.get("tax_category", "standard"),
            business_license=data.get("business_license", ""),
            commercial_registration=data.get("commercial_registration", ""),
            drug_license=data.get("drug_license", ""),
            license_expiry_date=data.get("license_expiry_date"),
            insurance_info=data.get("insurance_info", ""),
            is_preferred=data.get("is_preferred", False),
            rating=data.get("rating", 5.00),
            risk_level=data.get("risk_level", "low"),
            notes=data.get("notes", ""),
        )

        return Response(SupplierDetailSerializer(supplier).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, pk=None):
        supplier = self.get_object()
        updated = self.service.activate_supplier(supplier)
        return Response(SupplierSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="suspend")
    def suspend(self, request, pk=None):
        supplier = self.get_object()
        updated = self.service.suspend_supplier(supplier)
        return Response(SupplierSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="blacklist")
    def blacklist(self, request, pk=None):
        supplier = self.get_object()
        updated = self.service.blacklist_supplier(supplier)
        return Response(SupplierSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        supplier = self.get_object()
        updated = self.service.restore_supplier(supplier)
        return Response(SupplierSerializer(updated).data)

    @action(detail=False, methods=["post"], url_path="import")
    def import_suppliers(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = self.service.bulk_import_suppliers(request.tenant, None, serializer.validated_data["items"])
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="export")
    def export_suppliers(self, request):
        qs = self.get_queryset()
        data = SupplierSerializer(qs, many=True).data
        return Response({"count": len(data), "suppliers": data})

    def destroy(self, request, *args, **kwargs):
        supplier = self.get_object()
        self.service.soft_delete_supplier(supplier)
        return Response(status=status.HTTP_204_NO_CONTENT)
