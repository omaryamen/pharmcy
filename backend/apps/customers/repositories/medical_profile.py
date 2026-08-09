"""Customer Medical Profile repository for data access layer."""

from __future__ import annotations

from apps.common.repositories.base import BaseRepository
from apps.customers.models import CustomerMedicalProfile


class CustomerMedicalProfileRepository(BaseRepository[CustomerMedicalProfile]):
    model = CustomerMedicalProfile

    def get_by_customer(self, tenant, customer_id) -> CustomerMedicalProfile | None:
        return self.get_or_none(tenant=tenant, customer_id=customer_id)
