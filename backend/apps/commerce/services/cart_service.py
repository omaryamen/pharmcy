"""CartService managing shopping cart line modifications and guest-to-customer cart merging."""

from __future__ import annotations

from decimal import Decimal
from typing import Any
from django.db import transaction

from apps.commerce.models import Cart, CartItem, StoreProduct, TenantStore


class CartService:
    """Service layer managing cart item operations and guest cart merging upon login."""

    def get_or_create_cart(
        self,
        store: TenantStore,
        *,
        customer: Any | None = None,
        session_key: str = "",
    ) -> Cart:
        """Find or initialize shopping cart for a customer or guest session."""
        if customer:
            cart, _ = Cart.objects.get_or_create(
                tenant=store.tenant,
                store=store,
                customer=customer,
                defaults={"currency": store.currency},
            )
            return cart

        cart, _ = Cart.objects.get_or_create(
            tenant=store.tenant,
            store=store,
            session_key=session_key,
            customer=None,
            defaults={"currency": store.currency},
        )
        return cart

    @transaction.atomic
    def add_to_cart(
        self,
        cart: Cart,
        product: StoreProduct,
        quantity: Decimal = Decimal("1"),
    ) -> CartItem:
        """Add product to cart or increment quantity if already present."""
        unit_price = product.retail_price
        item, created = CartItem.objects.get_or_create(
            tenant=cart.tenant,
            cart=cart,
            product=product,
            defaults={"quantity": quantity, "unit_price": unit_price},
        )
        if not created:
            item.quantity += quantity
            item.unit_price = unit_price
            item.save(update_fields=["quantity", "unit_price", "updated_at"])
        return item

    @transaction.atomic
    def merge_guest_cart(self, guest_cart: Cart, customer_cart: Cart) -> None:
        """Merge items from a guest cart into a customer cart, preventing duplicate items."""
        for item in guest_cart.items.all():
            existing = customer_cart.items.filter(product=item.product).first()
            if existing:
                existing.quantity += item.quantity
                existing.save(update_fields=["quantity", "updated_at"])
                item.delete()
            else:
                item.cart = customer_cart
                item.save(update_fields=["cart", "updated_at"])
        guest_cart.delete()
