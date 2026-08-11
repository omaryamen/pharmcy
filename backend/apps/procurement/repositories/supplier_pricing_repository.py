"""Repository layer for SupplierProductPrice persistence."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from apps.procurement.models import SupplierProductPrice


class SupplierProductPriceRepository:
    """Repository encapsulating persistence operations for SupplierProductPrice."""

    def get_queryset(self, tenant: Any) -> QuerySet[SupplierProductPrice]:
        return SupplierProductPrice.objects.filter(tenant=tenant)

    def find_by_supplier_and_medicine(self, tenant: Any, supplier_id: str, medicine_id: str) -> SupplierProductPrice | None:
        return self.get_queryset(tenant).filter(supplier_id=supplier_id, medicine_id=medicine_id, is_active=True).first()

    def create_or_update(self, tenant: Any, supplier: Any, medicine: Any, **kwargs: Any) -> SupplierProductPrice:
        price_obj, _ = SupplierProductPrice.objects.update_or_create(
            tenant=tenant,
            supplier=supplier,
            medicine=medicine,
            defaults=kwargs,
        )
        return price_obj
