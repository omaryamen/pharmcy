"""Customer repository for data access layer."""

from __future__ import annotations

from apps.common.repositories.base import BaseRepository
from apps.customers.models import Customer


class CustomerRepository(BaseRepository[Customer]):
    model = Customer

    def get_by_code(self, tenant, code: str) -> Customer | None:
        return self.get_or_none(tenant=tenant, code=code.lower().strip())

    def get_by_number(self, tenant, customer_number: str) -> Customer | None:
        return self.get_or_none(tenant=tenant, customer_number=customer_number.strip())

    def get_by_phone(self, tenant, phone: str) -> Customer | None:
        return self.get_or_none(tenant=tenant, phone=phone.strip())

    def for_tenant(self, tenant) -> list[Customer]:
        return list(self.filter(tenant=tenant))
