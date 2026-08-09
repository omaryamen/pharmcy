"""API URL routing configuration for Enterprise Customer Management module."""

from __future__ import annotations

from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.customers.api.views import CustomerAddressViewSet, CustomerMedicalProfileView, CustomerViewSet

app_name = "customers"

router = DefaultRouter()
router.register(r"", CustomerViewSet, basename="customer")

urlpatterns = [
    path(
        "<uuid:customer_pk>/addresses/",
        CustomerAddressViewSet.as_view({"get": "list", "post": "create"}),
        name="customer-addresses-list",
    ),
    path(
        "<uuid:customer_pk>/addresses/<uuid:pk>/",
        CustomerAddressViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}),
        name="customer-address-detail",
    ),
    path(
        "<uuid:customer_pk>/medical-profile/",
        CustomerMedicalProfileView.as_view(),
        name="customer-medical-profile",
    ),
] + router.urls
