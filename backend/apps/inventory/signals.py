"""Signals for Enterprise Inventory & Batch Management module."""

from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.inventory.models import InventoryItem


@receiver(post_save, sender=InventoryItem)
def inventory_item_post_save_handler(sender, instance: InventoryItem, created: bool, **kwargs) -> None:
    """Handle post save events for InventoryItem (e.g. reorder alerts)."""
    pass
