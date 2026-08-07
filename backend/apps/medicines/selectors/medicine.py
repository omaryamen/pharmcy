"""Medicine selector functions for tenant & company-scoped queries."""

from __future__ import annotations

from typing import Any

from django.db.models import Q, QuerySet

from apps.medicines.models import Medicine
from apps.medicines.repositories import MedicineRepository


class MedicineSelector:
    def __init__(self) -> None:
        self.repository = MedicineRepository()

    def list_medicines(
        self,
        tenant,
        *,
        company_id: str | None = None,
        category: str | None = None,
        dosage_form: str | None = None,
        prescription_type: str | None = None,
        status: str | None = None,
        is_high_alert: bool | None = None,
        is_refrigerated: bool | None = None,
        is_cold_chain_required: bool | None = None,
        search: str | None = None,
    ) -> QuerySet[Medicine]:
        qs = self.repository.filter(tenant=tenant).select_related("company", "tenant")

        if company_id:
            qs = qs.filter(company_id=company_id)
        if category:
            qs = qs.filter(category__icontains=category)
        if dosage_form:
            qs = qs.filter(dosage_form__icontains=dosage_form)
        if prescription_type:
            qs = qs.filter(prescription_type=prescription_type)
        if status:
            qs = qs.filter(status=status)
        if is_high_alert is not None:
            qs = qs.filter(is_high_alert=is_high_alert)
        if is_refrigerated is not None:
            qs = qs.filter(is_refrigerated=is_refrigerated)
        if is_cold_chain_required is not None:
            qs = qs.filter(is_cold_chain_required=is_cold_chain_required)

        if search:
            qs = qs.filter(
                Q(english_name__icontains=search)
                | Q(arabic_name__icontains=search)
                | Q(generic_name__icontains=search)
                | Q(scientific_name__icontains=search)
                | Q(commercial_name__icontains=search)
                | Q(brand_name__icontains=search)
                | Q(code__icontains=search)
                | Q(sku__icontains=search)
                | Q(barcode__icontains=search)
                | Q(atc_code__icontains=search)
                | Q(manufacturer_name__icontains=search)
                | Q(category__icontains=search)
                | Q(therapeutic_class__icontains=search)
                | Q(search_keywords__icontains=search)
            )

        return qs

    def get_medicine_detail(self, tenant, medicine_id) -> Medicine | None:
        return self.repository.get_or_none(tenant=tenant, pk=medicine_id)

    def get_medicine_stats(self, tenant) -> dict[str, Any]:
        total_medicines = self.repository.filter(tenant=tenant).count()
        active_medicines = self.repository.filter(tenant=tenant, status="active").count()
        refrigerated_medicines = self.repository.filter(tenant=tenant, is_refrigerated=True).count()
        narcotics_medicines = self.repository.filter(tenant=tenant, is_narcotic=True).count()
        cold_chain_medicines = self.repository.filter(tenant=tenant, is_cold_chain_required=True).count()

        return {
            "tenant_id": str(tenant.pk),
            "total_medicines": total_medicines,
            "active_medicines": active_medicines,
            "refrigerated_medicines": refrigerated_medicines,
            "narcotic_medicines": narcotics_medicines,
            "cold_chain_medicines": cold_chain_medicines,
        }
