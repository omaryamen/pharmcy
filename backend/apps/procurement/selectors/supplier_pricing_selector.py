"""Query selector layer for SupplierProductPrice search."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from apps.procurement.models import SupplierProductPrice


class SupplierProductPriceSelector:
    """Selector providing query methods for SupplierProductPrice."""

    def list_prices(
        self,
        tenant: Any,
        *,
        supplier_id: str | None = None,
        medicine_id: str | None = None,
        is_active: bool | None = None,
    ) -> QuerySet[SupplierProductPrice]:
        qs = (
            SupplierProductPrice.objects.filter(tenant=tenant)
            .select_related("supplier", "medicine")
        )

        if supplier_id:
            qs = qs.filter(supplier_id=supplier_id)
        if medicine_id:
            qs = qs.filter(medicine_id=medicine_id)
        if is_active is not None:
            qs = qs.filter(is_active=is_active)

        return qs
