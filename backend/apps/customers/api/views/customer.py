"""Customer ViewSet for Enterprise Customer Management APIs."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.customers.permissions import CanManageCustomers, CanViewCustomers
from apps.customers.selectors import CustomerSelector
from apps.customers.serializers import (
    CustomerCreateSerializer,
    CustomerDetailSerializer,
    CustomerSerializer,
    CustomerUpdateSerializer,
    DuplicateCheckRequestSerializer,
)
from apps.customers.services import CustomerDuplicateDetector, CustomerService


@extend_schema_view(
    list=extend_schema(tags=["customers"], summary="List customers for active tenant"),
    retrieve=extend_schema(tags=["customers"], summary="Retrieve customer details"),
    create=extend_schema(tags=["customers"], summary="Create new customer profile"),
    update=extend_schema(tags=["customers"], summary="Update customer profile"),
    partial_update=extend_schema(tags=["customers"], summary="Partially update customer profile"),
    destroy=extend_schema(tags=["customers"], summary="Soft delete customer profile"),
)
class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.selector = CustomerSelector()
        self.service = CustomerService()
        self.duplicate_detector = CustomerDuplicateDetector()

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy", "activate", "deactivate", "block", "unblock", "suspend", "restore"}:
            return [(IsAuthenticatedAndActive & HasTenantContext & CanManageCustomers)()]
        return [(IsAuthenticatedAndActive & HasTenantContext & CanViewCustomers)()]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if not tenant:
            return self.selector.repository.model.objects.none()

        def parse_bool(val):
            if val is None:
                return None
            return str(val).lower() in {"true", "1", "yes"}

        return self.selector.list_customers(
            tenant=tenant,
            company_id=self.request.query_params.get("company"),
            branch_id=self.request.query_params.get("branch"),
            customer_type=self.request.query_params.get("customer_type"),
            status=self.request.query_params.get("status"),
            customer_group=self.request.query_params.get("customer_group"),
            credit_allowed=parse_bool(self.request.query_params.get("credit_allowed")),
            search=self.request.query_params.get("search"),
        )

    def get_serializer_class(self):
        if self.action == "create":
            return CustomerCreateSerializer
        if self.action in {"update", "partial_update"}:
            return CustomerUpdateSerializer
        if self.action == "retrieve":
            return CustomerDetailSerializer
        if self.action == "duplicates":
            return DuplicateCheckRequestSerializer
        return CustomerSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        customer = self.service.create_customer(
            tenant=request.tenant,
            company=data.get("company"),
            preferred_branch=data.get("preferred_branch"),
            code=data.get("code"),
            customer_number=data.get("customer_number"),
            customer_type=data.get("customer_type", "individual"),
            first_name=data.get("first_name", ""),
            middle_name=data.get("middle_name", ""),
            last_name=data.get("last_name", ""),
            arabic_name=data.get("arabic_name", ""),
            english_name=data.get("english_name", ""),
            preferred_name=data.get("preferred_name", ""),
            gender=data.get("gender", "unspecified"),
            date_of_birth=data.get("date_of_birth"),
            national_id=data.get("national_id", ""),
            passport_number=data.get("passport_number", ""),
            nationality=data.get("nationality", "Yemeni"),
            occupation=data.get("occupation", ""),
            profile_photo=data.get("profile_photo"),
            phone=data.get("phone", ""),
            secondary_phone=data.get("secondary_phone", ""),
            mobile=data.get("mobile", ""),
            whatsapp=data.get("whatsapp", ""),
            email=data.get("email", ""),
            alternative_email=data.get("alternative_email", ""),
            preferred_contact_method=data.get("preferred_contact_method", "phone"),
            preferred_communication_language=data.get("preferred_communication_language", "en"),
            preferred_language=data.get("preferred_language", "en"),
            preferred_currency=data.get("preferred_currency", "YER"),
            preferred_payment_method=data.get("preferred_payment_method", "cash"),
            sms_notifications=data.get("sms_notifications", True),
            email_notifications=data.get("email_notifications", True),
            whatsapp_notifications=data.get("whatsapp_notifications", True),
            marketing_consent=data.get("marketing_consent", False),
            notification_preferences=data.get("notification_preferences", {}),
            credit_allowed=data.get("credit_allowed", False),
            credit_limit=data.get("credit_limit", 0.00),
            payment_terms=data.get("payment_terms", "Immediate"),
            opening_balance=data.get("opening_balance", 0.00),
            current_balance=data.get("current_balance", 0.00),
            credit_status=data.get("credit_status", "normal"),
            default_payment_method=data.get("default_payment_method", "cash"),
            tax_category=data.get("tax_category", "standard"),
            discount_eligibility=data.get("discount_eligibility", True),
            discount_percentage=data.get("discount_percentage", 0.00),
            price_list=data.get("price_list", ""),
            customer_group=data.get("customer_group", "regular"),
            customer_segment=data.get("customer_segment", ""),
            customer_category=data.get("customer_category", ""),
            loyalty_account_number=data.get("loyalty_account_number", ""),
            loyalty_points_balance=data.get("loyalty_points_balance", 0.00),
            membership_level=data.get("membership_level", "bronze"),
            membership_number=data.get("membership_number", ""),
            loyalty_enrollment_date=data.get("loyalty_enrollment_date"),
            loyalty_expiration_date=data.get("loyalty_expiration_date"),
            insurance_provider_name=data.get("insurance_provider_name", ""),
            insurance_policy_number=data.get("insurance_policy_number", ""),
            insurance_member_number=data.get("insurance_member_number", ""),
            insurance_coverage_status=data.get("insurance_coverage_status", "none"),
            insurance_coverage_start_date=data.get("insurance_coverage_start_date"),
            insurance_coverage_end_date=data.get("insurance_coverage_end_date"),
            insurance_category=data.get("insurance_category", ""),
            notes=data.get("notes", ""),
            medical_profile_data=data.get("medical_profile_data"),
            addresses_data=data.get("addresses_data"),
        )

        return Response(CustomerDetailSerializer(customer).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        customer = self.get_object()
        serializer = self.get_serializer(customer, data=request.data, partial=kwargs.get("partial", False))
        serializer.is_valid(raise_exception=True)
        updated = self.service.update_customer(customer, **serializer.validated_data)
        return Response(CustomerDetailSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, pk=None):
        customer = self.get_object()
        updated = self.service.activate_customer(customer)
        return Response(CustomerSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate(self, request, pk=None):
        customer = self.get_object()
        updated = self.service.deactivate_customer(customer)
        return Response(CustomerSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="block")
    def block(self, request, pk=None):
        customer = self.get_object()
        updated = self.service.block_customer(customer)
        return Response(CustomerSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="unblock")
    def unblock(self, request, pk=None):
        customer = self.get_object()
        updated = self.service.unblock_customer(customer)
        return Response(CustomerSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="suspend")
    def suspend(self, request, pk=None):
        customer = self.get_object()
        updated = self.service.suspend_customer(customer)
        return Response(CustomerSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        customer = self.get_object()
        updated = self.service.restore_customer(customer)
        return Response(CustomerSerializer(updated).data)

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        stats_data = self.selector.get_customer_stats(request.tenant)
        return Response(stats_data)

    @action(detail=False, methods=["get"], url_path="search")
    def fast_search(self, request):
        query = request.query_params.get("q", "").strip()
        customers = self.selector.search_customers(request.tenant, query)
        return Response(CustomerSerializer(customers, many=True).data)

    @action(detail=False, methods=["post"], url_path="duplicates")
    def duplicates(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        results = self.duplicate_detector.detect_duplicates(request.tenant, **serializer.validated_data)
        return Response({"count": len(results), "duplicates": results})

    def destroy(self, request, *args, **kwargs):
        customer = self.get_object()
        self.service.soft_delete_customer(customer)
        return Response(status=status.HTTP_204_NO_CONTENT)
