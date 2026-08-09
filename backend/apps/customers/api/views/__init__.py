"""Customer API Views package."""

from apps.customers.api.views.address import CustomerAddressViewSet
from apps.customers.api.views.customer import CustomerViewSet
from apps.customers.api.views.medical_profile import CustomerMedicalProfileView

__all__ = [
    "CustomerViewSet",
    "CustomerAddressViewSet",
    "CustomerMedicalProfileView",
]
