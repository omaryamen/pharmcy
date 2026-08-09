"""Signals for Enterprise Customer Management module."""

from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.customers.models import Customer, CustomerMedicalProfile


@receiver(post_save, sender=Customer)
def ensure_customer_medical_profile(sender, instance: Customer, created: bool, **kwargs) -> None:
    """Ensure every created customer has an associated medical profile foundation."""
    if created and not hasattr(instance, "medical_profile"):
        CustomerMedicalProfile.objects.get_or_create(tenant=instance.tenant, customer=instance)
