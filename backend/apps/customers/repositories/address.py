"""Customer Address repository for data access layer."""

from __future__ import annotations

from apps.common.repositories.base import BaseRepository
from apps.customers.models import CustomerAddress


class CustomerAddressRepository(BaseRepository[CustomerAddress]):
    model = CustomerAddress

    def get_for_customer(self, tenant, customer_id) -> list[CustomerAddress]:
        return list(self.filter(tenant=tenant, customer_id=customer_id))
