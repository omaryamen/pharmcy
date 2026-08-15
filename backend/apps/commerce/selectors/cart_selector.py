"""CartSelector calculating shopping cart totals, taxes, and shipping."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from apps.commerce.models import Cart


class CartSelector:
    """Selector calculating shopping cart item lines, subtotals, delivery fees, and grand totals."""

    def calculate_cart_summary(self, cart: Cart) -> dict[str, Any]:
        """Compute lines and aggregate financial breakdown for a shopping cart."""
        items_data = []
        subtotal = Decimal("0.00")

        for item in cart.items.select_related("product", "product__medicine").all():
            line_total = item.quantity * item.unit_price
            subtotal += line_total
            items_data.append(
                {
                    "item_id": item.pk,
                    "product_id": item.product.pk,
                    "display_name": item.product.display_name,
                    "quantity": float(item.quantity),
                    "unit_price": float(item.unit_price),
                    "line_total": float(line_total),
                    "is_prescription_required": item.product.is_prescription_required,
                }
            )

        delivery_fee = cart.store.delivery_fee
        if cart.store.free_delivery_threshold > 0 and subtotal >= cart.store.free_delivery_threshold:
            delivery_fee = Decimal("0.00")

        total = subtotal + delivery_fee

        return {
            "cart_id": cart.pk,
            "currency": cart.currency,
            "subtotal": float(subtotal),
            "delivery_fee": float(delivery_fee),
            "total": float(total),
            "items_count": len(items_data),
            "items": items_data,
        }
