"""CommerceOrderSelector querying order histories and delivery tracking."""

from __future__ import annotations

from typing import Any

from apps.commerce.models import CommerceOrder, OrderDelivery, OrderPrescription


class CommerceOrderSelector:
    """Selector retrieving full order tracking, prescriptions, and status timeline."""

    def get_order_tracking_details(self, order: CommerceOrder) -> dict[str, Any]:
        """Format complete public/customer tracking data for an order."""
        delivery = getattr(order, "delivery_record", None)
        rx = order.prescriptions.first()

        lines_data = [
            {
                "product_name": line.product.display_name,
                "quantity": float(line.quantity),
                "unit_price": float(line.unit_price),
                "total_amount": float(line.total_amount),
            }
            for line in order.lines.select_related("product").all()
        ]

        return {
            "order_number": order.order_number,
            "status": order.status,
            "payment_status": order.payment_status,
            "delivery_method": order.delivery_method,
            "total_amount": float(order.total_amount),
            "currency": order.currency,
            "shipping_address": order.shipping_address,
            "created_at": order.created_at.isoformat(),
            "tracking_number": delivery.tracking_number if delivery else None,
            "courier_name": delivery.courier_name if delivery else None,
            "prescription_review_status": rx.review_status if rx else None,
            "lines": lines_data,
        }
