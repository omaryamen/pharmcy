"""Repository layer for Prescription & Dispensation persistence."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from apps.prescriptions.models import Prescription, PrescriptionDispense, PrescriptionLine


class PrescriptionRepository:
    """Repository encapsulating persistence operations for Prescription entity."""

    def get_queryset(self, tenant: Any) -> QuerySet[Prescription]:
        return Prescription.objects.filter(tenant=tenant)

    def find_by_id(self, tenant: Any, rx_id: str) -> Prescription | None:
        return self.get_queryset(tenant).filter(pk=rx_id).first()

    def find_by_idempotency_key(self, tenant: Any, key: str) -> Prescription | None:
        if not key:
            return None
        return self.get_queryset(tenant).filter(idempotency_key=key).first()

    def create(self, tenant: Any, **kwargs: Any) -> Prescription:
        return Prescription.objects.create(tenant=tenant, **kwargs)


class PrescriptionDispenseRepository:
    """Repository encapsulating persistence operations for PrescriptionDispense entity."""

    def get_queryset(self, tenant: Any) -> QuerySet[PrescriptionDispense]:
        return PrescriptionDispense.objects.filter(tenant=tenant)

    def create(self, tenant: Any, **kwargs: Any) -> PrescriptionDispense:
        return PrescriptionDispense.objects.create(tenant=tenant, **kwargs)
