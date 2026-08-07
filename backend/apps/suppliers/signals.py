"""Signals for Enterprise Supplier Management events."""

from __future__ import annotations

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.suppliers.models import Supplier

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Supplier)
def supplier_post_save(sender, instance: Supplier, created: bool, **kwargs):
    if created:
        logger.info("Supplier created: %s (%s)", instance.display_name, instance.code)
    else:
        logger.info("Supplier updated: %s (%s)", instance.display_name, instance.code)
