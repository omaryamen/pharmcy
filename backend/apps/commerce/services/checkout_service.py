"""CheckoutService executing robust, idempotent digital order checkout."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any
from django.db import transaction
from django.db.models import Sum

from apps.commerce.exceptions import (
    CreditLimitExceededError,
    InvalidCouponError,
    PrescriptionRequiredError,
    StockUnavailableError,
)
from apps.commerce.models import (
    Cart,
    CommerceOrder,
    CommerceOrderLine,
    CommerceOrderStatus,
    CommercePaymentStatus,
    CouponDiscountType,
    DeliveryMethod,
    OrderPrescription,
    PrescriptionReviewStatus,
    StoreCoupon,
)
from apps.commerce.services.number_generator import CommerceNumberGenerator
from apps.inventory.models import InventoryItem
from apps.notifications.services import EventPublisherService

logger = logging.getLogger(__name__)


class CheckoutService:
    """Service layer validating carts, calculating authoritative pricing, and placing commerce orders."""

    def __init__(self, event_publisher: EventPublisherService | None = None) -> None:
        self.event_publisher = event_publisher or EventPublisherService()

    @transaction.atomic
    def checkout_cart(
        self,
        cart: Cart,
        *,
        customer: Any,
        shipping_address: str = "",
        delivery_method: str = DeliveryMethod.STANDARD_DELIVERY,
        coupon_code: str | None = None,
        idempotency_key: str = "",
        prescription_file_url: str | None = None,
        branch: Any | None = None,
        warehouse: Any | None = None,
    ) -> CommerceOrder:
        """Execute authoritative checkout, calculating server-side prices and issuing an order."""
        if idempotency_key:
            existing = CommerceOrder.objects.filter(
                tenant=cart.tenant,
                idempotency_key=idempotency_key,
            ).first()
            if existing:
                return existing

        items = list(cart.items.select_related("product", "product__medicine").all())
        if not items:
            raise StockUnavailableError("Cannot checkout an empty shopping cart.")

        # 1. Authoritative Pricing & Inventory Verification
        is_b2b = getattr(customer, "customer_type", "") in ["pharmacy", "hospital", "clinic", "wholesaler", "distributor"]
        subtotal = Decimal("0.00")
        has_prescription_items = False

        for item in items:
            prod = item.product
            # Price Resolution
            unit_price = prod.b2b_price if is_b2b else prod.retail_price
            item.unit_price = unit_price
            subtotal += item.quantity * unit_price

            if prod.is_prescription_required:
                has_prescription_items = True

            # Stock Verification
            available_qty = (
                InventoryItem.objects.filter(
                    tenant=cart.tenant,
                    medicine=prod.medicine,
                    is_deleted=False,
                ).aggregate(total=Sum("on_hand_quantity"))["total"]
                or Decimal("0.0")
            )
            if available_qty < item.quantity:
                raise StockUnavailableError(f"Insufficient stock for product '{prod.display_name}'.")

        # 2. Coupon Validation
        discount_amount = Decimal("0.00")
        if coupon_code:
            coupon = StoreCoupon.objects.filter(
                tenant=cart.tenant,
                store=cart.store,
                code=coupon_code,
            ).first()
            if not coupon or not coupon.is_valid_now:
                raise InvalidCouponError("The provided coupon is invalid or expired.")
            if subtotal < coupon.min_order_amount:
                raise InvalidCouponError(f"Coupon requires a minimum order subtotal of {coupon.min_order_amount}.")

            if coupon.discount_type == CouponDiscountType.PERCENTAGE:
                discount_amount = (subtotal * coupon.discount_value) / Decimal("100.00")
            else:
                discount_amount = min(coupon.discount_value, subtotal)

            coupon.times_used += 1
            coupon.save(update_fields=["times_used", "updated_at"])

        # 3. Delivery Fee
        delivery_fee = cart.store.delivery_fee
        if cart.store.free_delivery_threshold > 0 and subtotal >= cart.store.free_delivery_threshold:
            delivery_fee = Decimal("0.00")

        total_amount = subtotal - discount_amount + delivery_fee

        # 4. B2B Credit Limit Check
        if is_b2b and getattr(customer, "credit_limit", Decimal("0.0")) > 0:
            current_balance = getattr(customer, "current_balance", Decimal("0.0"))
            credit_limit = getattr(customer, "credit_limit", Decimal("0.0"))
            if current_balance + total_amount > credit_limit:
                raise CreditLimitExceededError(
                    f"Order total ({total_amount}) exceeds available credit limit ({credit_limit - current_balance})."
                )

        # 5. Prescription Requirement Check
        order_status = CommerceOrderStatus.PENDING
        if has_prescription_items and not prescription_file_url:
            raise PrescriptionRequiredError("Order contains prescription drugs; please upload a valid prescription.")

        # 6. Create Commerce Order & Lines
        order_number = CommerceNumberGenerator.generate_order_number()
        order = CommerceOrder.objects.create(
            tenant=cart.tenant,
            store=cart.store,
            customer=customer,
            branch=branch,
            warehouse=warehouse,
            order_number=order_number,
            status=order_status,
            payment_status=CommercePaymentStatus.PENDING,
            delivery_method=delivery_method,
            subtotal=subtotal,
            discount_amount=discount_amount,
            tax_amount=Decimal("0.00"),
            shipping_fee=delivery_fee,
            total_amount=total_amount,
            currency=cart.currency,
            shipping_address=shipping_address,
            idempotency_key=idempotency_key,
        )

        for item in items:
            line_total = item.quantity * item.unit_price
            CommerceOrderLine.objects.create(
                tenant=cart.tenant,
                order=order,
                product=item.product,
                medicine=item.product.medicine,
                quantity=item.quantity,
                unit_price=item.unit_price,
                discount_amount=Decimal("0.00"),
                tax_amount=Decimal("0.00"),
                total_amount=line_total,
            )

        if has_prescription_items and prescription_file_url:
            OrderPrescription.objects.create(
                tenant=cart.tenant,
                order=order,
                customer=customer,
                file_url=prescription_file_url,
                review_status=PrescriptionReviewStatus.UPLOADED,
            )

        # Empty the cart
        cart.items.all().delete()

        # Publish Event
        self.event_publisher.publish_event(
            tenant=cart.tenant,
            event_type="order.created",
            source_module="commerce",
            source_object_id=str(order.pk),
            payload={
                "order_number": order.order_number,
                "customer_id": str(customer.pk),
                "total_amount": float(order.total_amount),
            },
        )
        logger.info("Placed Commerce Order %s for %s (%s %s)", order.order_number, customer, order.total_amount, order.currency)
        return order
