"""Customer serializers package."""

from apps.customers.serializers.address import CustomerAddressSerializer
from apps.customers.serializers.customer import (
    CustomerCreateSerializer,
    CustomerDetailSerializer,
    CustomerSerializer,
    CustomerUpdateSerializer,
    DuplicateCheckRequestSerializer,
)
from apps.customers.serializers.medical_profile import CustomerMedicalProfileSerializer

__all__ = [
    "CustomerSerializer",
    "CustomerDetailSerializer",
    "CustomerCreateSerializer",
    "CustomerUpdateSerializer",
    "CustomerAddressSerializer",
    "CustomerMedicalProfileSerializer",
    "DuplicateCheckRequestSerializer",
]
