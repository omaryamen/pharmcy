"""Reference API ViewSets."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.references.permissions import CanManageReferences, CanViewReferences
from apps.references.selectors import ReferenceSelector
from apps.references.serializers import (
    AtcClassificationSerializer,
    DosageFormSerializer,
    ManufacturerSerializer,
    MedicineCategorySerializer,
    PackageTypeSerializer,
    RouteOfAdministrationSerializer,
    StorageConditionSerializer,
    StrengthUnitSerializer,
    TaxCategorySerializer,
    UnitOfMeasureSerializer,
)
from apps.references.services import ReferenceDataService


class MedicineCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = MedicineCategorySerializer
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.selector = ReferenceSelector()
        self.service = ReferenceDataService()

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [(IsAuthenticatedAndActive & HasTenantContext & CanManageReferences)()]
        return [(IsAuthenticatedAndActive & HasTenantContext & CanViewReferences)()]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if not tenant:
            return self.selector.list_categories(tenant).none()
        return self.selector.list_categories(tenant, search=self.request.query_params.get("search"))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        category = self.service.create_category(
            tenant=request.tenant,
            code=data["code"],
            name_en=data["name_en"],
            name_ar=data["name_ar"],
            parent=data.get("parent"),
            icon=data.get("icon", ""),
            display_order=data.get("display_order", 0),
        )
        return Response(MedicineCategorySerializer(category).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="tree")
    def tree(self, request):
        tree_data = self.selector.get_category_tree(request.tenant)
        return Response(tree_data)


class ManufacturerViewSet(viewsets.ModelViewSet):
    serializer_class = ManufacturerSerializer
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.selector = ReferenceSelector()
        self.service = ReferenceDataService()

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [(IsAuthenticatedAndActive & HasTenantContext & CanManageReferences)()]
        return [(IsAuthenticatedAndActive & HasTenantContext & CanViewReferences)()]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if not tenant:
            return self.selector.list_manufacturers(tenant).none()
        return self.selector.list_manufacturers(tenant, search=self.request.query_params.get("search"))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        manufacturer = self.service.create_manufacturer(
            tenant=request.tenant,
            code=data["code"],
            legal_name=data["legal_name"],
            display_name=data["display_name"],
            country_of_origin=data.get("country_of_origin", "Yemen"),
            address=data.get("address", ""),
            website=data.get("website", ""),
            contact_email=data.get("contact_email", ""),
            contact_phone=data.get("contact_phone", ""),
            registration_number=data.get("registration_number", ""),
        )
        return Response(ManufacturerSerializer(manufacturer).data, status=status.HTTP_201_CREATED)


class DosageFormViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DosageFormSerializer
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext, CanViewReferences]

    def get_queryset(self):
        return ReferenceSelector().list_dosage_forms(self.request.tenant)


class StrengthUnitViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StrengthUnitSerializer
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext, CanViewReferences]

    def get_queryset(self):
        return ReferenceSelector().list_strength_units(self.request.tenant)


class UnitOfMeasureViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UnitOfMeasureSerializer
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext, CanViewReferences]

    def get_queryset(self):
        return ReferenceSelector().list_units_of_measure(self.request.tenant)


class PackageTypeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PackageTypeSerializer
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext, CanViewReferences]

    def get_queryset(self):
        return ReferenceSelector().list_package_types(self.request.tenant)


class RouteOfAdministrationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RouteOfAdministrationSerializer
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext, CanViewReferences]

    def get_queryset(self):
        return ReferenceSelector().list_routes(self.request.tenant)


class AtcClassificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AtcClassificationSerializer
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext, CanViewReferences]

    def get_queryset(self):
        level = self.request.query_params.get("level")
        return ReferenceSelector().list_atc_classifications(self.request.tenant, level=int(level) if level else None)


class StorageConditionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StorageConditionSerializer
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext, CanViewReferences]

    def get_queryset(self):
        return ReferenceSelector().list_storage_conditions(self.request.tenant)


class TaxCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TaxCategorySerializer
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext, CanViewReferences]

    def get_queryset(self):
        return ReferenceSelector().list_tax_categories(self.request.tenant)


class ReferenceSeedView(APIView):
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext, CanManageReferences]

    @extend_schema(tags=["references"], summary="Seed standard pharmaceutical reference data")
    def post(self, request):
        result = ReferenceDataService().seed_system_defaults(request.tenant)
        return Response({"message": "Successfully seeded reference defaults.", "result": result}, status=status.HTTP_200_OK)
