"""Customer Address Model supporting multi-address capabilities."""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import FullAuditModel
from apps.common.models.tenancy import TenantAwareModel
from apps.customers.models.enums import AddressType


class CustomerAddress(FullAuditModel, TenantAwareModel):
    """Customer physical, billing, and delivery address entity."""

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name=_("Customer"),
        db_index=True,
    )
    address_type = models.CharField(
        max_length=30,
        choices=AddressType.choices,
        default=AddressType.HOME,
        verbose_name=_("Address type"),
    )
    is_primary = models.BooleanField(default=False, verbose_name=_("Is primary address"))
    is_default_billing = models.BooleanField(default=False, verbose_name=_("Is default billing address"))
    is_default_delivery = models.BooleanField(default=False, verbose_name=_("Is default delivery address"))

    country = models.CharField(max_length=100, default="Yemen", verbose_name=_("Country"))
    state = models.CharField(max_length=100, blank=True, default="", verbose_name=_("State"))
    city = models.CharField(max_length=100, default="Sanaa", verbose_name=_("City"))
    district = models.CharField(max_length=100, blank=True, default="", verbose_name=_("District"))
    street = models.CharField(max_length=255, blank=True, default="", verbose_name=_("Street"))
    building = models.CharField(max_length=100, blank=True, default="", verbose_name=_("Building"))
    postal_code = models.CharField(max_length=20, blank=True, default="", verbose_name=_("Postal code"))
    additional_info = models.TextField(blank=True, default="", verbose_name=_("Additional information"))

    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True, verbose_name=_("Latitude"))
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True, verbose_name=_("Longitude"))
    google_maps_url = models.URLField(blank=True, default="", verbose_name=_("Google Maps URL"))

    class Meta:
        ordering = ["-is_primary", "-created_at"]
        verbose_name = "Customer Address"
        verbose_name_plural = "Customer Addresses"
        indexes = [
            models.Index(fields=["customer", "address_type"]),
            models.Index(fields=["tenant", "customer"]),
        ]

    def __str__(self) -> str:
        return f"{self.customer.code} - {self.get_address_type_display()} ({self.city})"

    def save(self, *args, **kwargs) -> None:
        if self.is_primary:
            CustomerAddress.objects.filter(customer=self.customer, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        if self.is_default_billing:
            CustomerAddress.objects.filter(customer=self.customer, is_default_billing=True).exclude(pk=self.pk).update(
                is_default_billing=False
            )
        if self.is_default_delivery:
            CustomerAddress.objects.filter(customer=self.customer, is_default_delivery=True).exclude(pk=self.pk).update(
                is_default_delivery=False
            )
        super().save(*args, **kwargs)
