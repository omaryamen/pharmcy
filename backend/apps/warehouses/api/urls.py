"""API URL routing configuration for Enterprise Warehouse Management module."""

from __future__ import annotations

from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.warehouses.api.views import StorageLocationViewSet, WarehouseViewSet

app_name = "warehouses"

router = DefaultRouter()
router.register(r"", WarehouseViewSet, basename="warehouse")

urlpatterns = [
    path(
        "<uuid:warehouse_pk>/locations/",
        StorageLocationViewSet.as_view({"get": "list", "post": "create"}),
        name="warehouse-locations-list",
    ),
    path(
        "<uuid:warehouse_pk>/locations/tree/",
        StorageLocationViewSet.as_view({"get": "tree"}),
        name="warehouse-locations-tree",
    ),
    path(
        "<uuid:warehouse_pk>/locations/<uuid:pk>/",
        StorageLocationViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}),
        name="warehouse-location-detail",
    ),
] + router.urls
