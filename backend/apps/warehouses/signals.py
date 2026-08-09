"""Signals for Enterprise Warehouse Management module."""

from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.warehouses.models import Warehouse


@receiver(post_save, sender=Warehouse)
def warehouse_post_save_handler(sender, instance: Warehouse, created: bool, **kwargs) -> None:
    """Handle post save events for Warehouse (e.g. audit log notification)."""
    pass
