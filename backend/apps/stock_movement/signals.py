"""Signals for Enterprise Stock Movement Engine."""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.stock_movement.models import StockMovement, MovementStatus

logger = logging.getLogger(__name__)


@receiver(post_save, sender=StockMovement)
def on_stock_movement_status_change(sender, instance: StockMovement, created: bool, **kwargs):
    if not created:
        logger.debug("StockMovement %s status: %s", instance.movement_number, instance.movement_status)
