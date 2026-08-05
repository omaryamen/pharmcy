"""Base views / viewsets that wire services into the DRF stack."""

from __future__ import annotations

from django.core.exceptions import ImproperlyConfigured
from rest_framework import viewsets
from rest_framework.views import APIView

from apps.common.utils.context import get_request_id


class BaseAPIView(APIView):
    """Base API view with request correlation helpers."""

    @property
    def request_id(self) -> str | None:
        return get_request_id()


class BaseModelViewSet(viewsets.ModelViewSet):
    """ModelViewSet wired to a service layer.

    Subclasses MUST define ``service_class`` and ``serializer_class``.
    All create/update/delete operations flow through the service, which is
    responsible for business rules, tenant scoping and atomicity.
    """

    service_class = None
    serializer_class = None

    def get_service(self):
        if self.service_class is None:
            raise ImproperlyConfigured(f"{self.__class__.__name__} must define 'service_class'.")
        return self.service_class()

    def get_serializer_class(self):
        if self.serializer_class is None:
            raise ImproperlyConfigured(f"{self.__class__.__name__} must define 'serializer_class'.")
        return self.serializer_class

    def get_queryset(self):
        return self.get_service().list()

    def perform_create(self, serializer):
        serializer.instance = self.get_service().create(serializer.validated_data)

    def perform_update(self, serializer):
        service = self.get_service()
        serializer.instance = service.update(serializer.instance.pk, serializer.validated_data)

    def perform_destroy(self, instance):
        self.get_service().delete(instance.pk)


class BaseReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only viewset wired to a service layer."""

    service_class = None
    serializer_class = None

    def get_service(self):
        if self.service_class is None:
            raise ImproperlyConfigured(f"{self.__class__.__name__} must define 'service_class'.")
        return self.service_class()

    def get_serializer_class(self):
        if self.serializer_class is None:
            raise ImproperlyConfigured(f"{self.__class__.__name__} must define 'serializer_class'.")
        return self.serializer_class

    def get_queryset(self):
        return self.get_service().list()
