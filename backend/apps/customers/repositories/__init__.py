"""Customer repositories package."""

from apps.customers.repositories.address import CustomerAddressRepository
from apps.customers.repositories.customer import CustomerRepository
from apps.customers.repositories.medical_profile import CustomerMedicalProfileRepository

__all__ = [
    "CustomerRepository",
    "CustomerAddressRepository",
    "CustomerMedicalProfileRepository",
]
