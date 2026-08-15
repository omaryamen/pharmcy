"""CustomerDashboardSelector aggregating live mobile home screen data for retail/B2B customers."""

from __future__ import annotations

from typing import Any
from apps.commerce.models import CommerceOrder, CommerceOrderStatus, OrderPrescription, PrescriptionReviewStatus, StoreProduct
from apps.customers.models import Customer
from apps.notifications.models import Notification


class CustomerDashboardSelector:
    """Selector calculating aggregated mobile dashboard payload for an authenticated customer."""

    def get_customer_dashboard(self, customer: Customer) -> dict[str, Any]:
        """Aggregate active orders count, recent orders list, pending prescriptions, and notifications."""
        # 1. Orders
        orders_qs = CommerceOrder.objects.filter(customer=customer).order_by("-created_at")
        active_orders_count = orders_qs.exclude(
            status__in=[CommerceOrderStatus.COMPLETED, CommerceOrderStatus.CANCELLED, CommerceOrderStatus.REFUNDED]
        ).count()
        recent_orders = list(
            orders_qs[:5].values(
                "id", "order_number", "total_amount", "currency", "status", "payment_status", "created_at"
            )
        )

        # 2. Prescriptions
        prescriptions_qs = OrderPrescription.objects.filter(customer=customer)
        pending_rx_count = prescriptions_qs.filter(
            review_status__in=[PrescriptionReviewStatus.UPLOADED, PrescriptionReviewStatus.UNDER_REVIEW]
        ).count()

        # 3. Unread Notifications
        user = getattr(customer, "user", None)
        unread_notifications_count = (
            Notification.objects.filter(user=user, is_read=False).count() if user else 0
        )

        # 4. Featured Products (from tenant stores)
        featured_products = list(
            StoreProduct.objects.filter(tenant=customer.tenant, is_published=True, is_featured=True)[:6].values(
                "id", "display_name", "retail_price", "is_prescription_required"
            )
        )

        return {
            "customer_id": str(customer.pk),
            "customer_name": f"{customer.first_name} {customer.last_name}".strip(),
            "active_orders_count": active_orders_count,
            "pending_prescriptions_count": pending_rx_count,
            "unread_notifications_count": unread_notifications_count,
            "recent_orders": recent_orders,
            "featured_products": featured_products,
        }
