"""Django admin configuration for Customer Domain."""

from __future__ import annotations

from django.contrib import admin

from apps.customers.models import Customer, CustomerAddress, CustomerMedicalProfile


class CustomerAddressInline(admin.TabularInline):
    model = CustomerAddress
    extra = 0


class CustomerMedicalProfileInline(admin.StackedInline):
    model = CustomerMedicalProfile
    extra = 0


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["code", "customer_number", "display_name", "customer_type", "status", "phone", "email", "tenant"]
    list_filter = ["status", "customer_type", "customer_group", "gender", "tenant"]
    search_fields = ["code", "customer_number", "arabic_name", "english_name", "first_name", "last_name", "phone", "email"]
    inlines = [CustomerAddressInline, CustomerMedicalProfileInline]


@admin.register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ["customer", "address_type", "city", "country", "is_primary"]
    list_filter = ["address_type", "is_primary", "country"]


@admin.register(CustomerMedicalProfile)
class CustomerMedicalProfileAdmin(admin.ModelAdmin):
    list_display = ["customer", "blood_type", "emergency_contact_name"]
