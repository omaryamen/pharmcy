"""Customer Address ViewSet for managing customer addresses."""

from __future__ import annotations

from rest_framework import status, viewsets
from rest_framework.response import Response

from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.customers.exceptions import CustomerNotFoundError
from apps.customers.models import CustomerAddress
from apps.customers.permissions import CanManageCustomers, CanViewCustomers
from apps.customers.repositories import CustomerAddressRepository, CustomerRepository
from apps.customers.serializers import CustomerAddressSerializer
from apps.customers.services import CustomerService


class CustomerAddressViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerAddressSerializer
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.repository = CustomerAddressRepository()
        self.customer_repository = CustomerRepository()
        self.service = CustomerService()

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [(IsAuthenticatedAndActive & HasTenantContext & CanManageCustomers)()]
        return [(IsAuthenticatedAndActive & HasTenantContext & CanViewCustomers)()]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if not tenant:
            return CustomerAddress.objects.none()

        customer_pk = self.kwargs.get("customer_pk")
        if customer_pk:
            return self.repository.filter(tenant=tenant, customer_id=customer_pk)
        return self.repository.filter(tenant=tenant)

    def create(self, request, *args, **kwargs):
        tenant = request.tenant
        customer_pk = self.kwargs.get("customer_pk") or request.data.get("customer")
        customer = self.customer_repository.get_or_none(tenant=tenant, pk=customer_pk)
        if not customer:
            raise CustomerNotFoundError()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        address = self.service.add_address(tenant, customer, **serializer.validated_data)
        return Response(CustomerAddressSerializer(address).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        address = self.get_object()
        serializer = self.get_serializer(address, data=request.data, partial=kwargs.get("partial", False))
        serializer.is_valid(raise_exception=True)
        updated = self.service.update_address(address, **serializer.validated_data)
        return Response(CustomerAddressSerializer(updated).data)

    def destroy(self, request, *args, **kwargs):
        address = self.get_object()
        self.service.delete_address(address)
        return Response(status=status.HTTP_204_NO_CONTENT)
