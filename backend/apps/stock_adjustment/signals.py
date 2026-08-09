"""Signals for Enterprise Stock Adjustment & Stock Count module."""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.stock_adjustment.models import StockCount

logger = logging.getLogger(__name__)


@receiver(post_save, sender=StockCount)
def on_stock_count_status_change(sender, instance: StockCount, created: bool, **kwargs):
    if not created:
        logger.debug("StockCount %s status: %s", instance.count_number, instance.count_status)
