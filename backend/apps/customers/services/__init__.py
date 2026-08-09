"""Customer services package."""

from apps.customers.services.customer import CustomerService
from apps.customers.services.duplicate_detector import CustomerDuplicateDetector

__all__ = ["CustomerService", "CustomerDuplicateDetector"]
