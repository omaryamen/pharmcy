"""Customer Medical Profile View for accessing and updating sensitive medical information."""

from __future__ import annotations

from rest_framework import generics, status
from rest_framework.response import Response

from apps.common.permissions import HasTenantContext, IsAuthenticatedAndActive
from apps.customers.exceptions import CustomerNotFoundError
from apps.customers.models import CustomerMedicalProfile
from apps.customers.permissions import CanManageCustomerMedicalProfile, CanViewCustomerMedicalProfile
from apps.customers.repositories import CustomerMedicalProfileRepository, CustomerRepository
from apps.customers.serializers import CustomerMedicalProfileSerializer
from apps.customers.services import CustomerService


class CustomerMedicalProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomerMedicalProfileSerializer
    permission_classes = [IsAuthenticatedAndActive, HasTenantContext]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.repository = CustomerMedicalProfileRepository()
        self.customer_repository = CustomerRepository()
        self.service = CustomerService()

    def get_permissions(self):
        if self.request.method in {"PUT", "PATCH"}:
            return [(IsAuthenticatedAndActive & HasTenantContext & CanManageCustomerMedicalProfile)()]
        return [(IsAuthenticatedAndActive & HasTenantContext & CanViewCustomerMedicalProfile)()]

    def get_object(self) -> CustomerMedicalProfile:
        tenant = self.request.tenant
        customer_pk = self.kwargs.get("customer_pk")
        customer = self.customer_repository.get_or_none(tenant=tenant, pk=customer_pk)
        if not customer:
            raise CustomerNotFoundError()

        medical_profile = self.repository.get_by_customer(tenant=tenant, customer_id=customer_pk)
        if not medical_profile:
            # Lazy creation on access
            medical_profile = CustomerMedicalProfile.objects.create(tenant=tenant, customer=customer)
        return medical_profile

    def update(self, request, *args, **kwargs):
        medical_profile = self.get_object()
        serializer = self.get_serializer(medical_profile, data=request.data, partial=kwargs.get("partial", False))
        serializer.is_valid(raise_exception=True)
        updated = self.service.update_medical_profile(request.tenant, medical_profile.customer, **serializer.validated_data)
        return Response(CustomerMedicalProfileSerializer(updated).data, status=status.HTTP_200_OK)
