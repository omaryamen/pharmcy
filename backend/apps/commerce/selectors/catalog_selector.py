"""StoreCatalogSelector retrieving published products and live stock positions."""

from __future__ import annotations

from decimal import Decimal
from typing import Any
from django.db.models import Q, Sum

from apps.commerce.models import StoreProduct, TenantStore
from apps.inventory.models import InventoryItem


class StoreCatalogSelector:
    """Selector querying digital storefront catalog items, category filters, and live stock positions."""

    def list_published_products(
        self,
        store: TenantStore,
        *,
        category_id: str | None = None,
        search_query: str | None = None,
        is_featured: bool | None = None,
    ) -> list[dict[str, Any]]:
        """List active published products with calculated available stock across all store warehouses."""
        qs = StoreProduct.objects.filter(store=store, is_published=True).select_related("medicine")

        if category_id:
            qs = qs.filter(medicine__category_id=category_id)

        if is_featured is not None:
            qs = qs.filter(is_featured=is_featured)

        if search_query:
            qs = qs.filter(
                Q(display_name__icontains=search_query)
                | Q(medicine__english_name__icontains=search_query)
                | Q(medicine__arabic_name__icontains=search_query)
                | Q(medicine__generic_name__icontains=search_query)
                | Q(medicine__barcode__icontains=search_query)
            )

        results = []
        for p in qs:
            available_qty = (
                InventoryItem.objects.filter(
                    tenant=store.tenant,
                    medicine=p.medicine,
                    is_deleted=False,
                ).aggregate(total=Sum("on_hand_quantity"))["total"]
                or Decimal("0.0")
            )

            results.append(
                {
                    "id": p.pk,
                    "display_name": p.display_name,
                    "description": p.description,
                    "retail_price": float(p.retail_price),
                    "b2b_price": float(p.b2b_price),
                    "is_prescription_required": p.is_prescription_required,
                    "min_order_qty": p.min_order_qty,
                    "max_order_qty": p.max_order_qty,
                    "medicine_id": p.medicine.pk,
                    "medicine_name": p.medicine.english_name,
                    "generic_name": p.medicine.generic_name,
                    "available_stock": float(available_qty),
                }
            )
        return results
