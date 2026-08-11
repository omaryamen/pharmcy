"""Collision-safe sequence number generator for procurement documents."""

from __future__ import annotations

from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.procurement.models import PurchaseOrder, PurchaseOrderAmendment, PurchaseRequisition, SupplierQuotation


class ProcurementNumberGenerator:
    """Generates sequential document numbers for requisitions (PR-), POs (PO-), amendments (AMD-), and quotations (QUO-)."""

    @transaction.atomic
    def generate_requisition_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"PR-{year}-"

        last_req = (
            PurchaseRequisition.objects.filter(tenant=tenant, requisition_number__startswith=prefix)
            .order_by("-requisition_number")
            .select_for_update()
            .first()
        )

        if not last_req:
            seq = 1
        else:
            try:
                seq = int(last_req.requisition_number.split("-")[-1]) + 1
            except (ValueError, IndexError):
                seq = 1

        return f"{prefix}{seq:06d}"

    @transaction.atomic
    def generate_po_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"PO-{year}-"

        last_po = (
            PurchaseOrder.objects.filter(tenant=tenant, po_number__startswith=prefix)
            .order_by("-po_number")
            .select_for_update()
            .first()
        )

        if not last_po:
            seq = 1
        else:
            try:
                seq = int(last_po.po_number.split("-")[-1]) + 1
            except (ValueError, IndexError):
                seq = 1

        return f"{prefix}{seq:06d}"

    @transaction.atomic
    def generate_amendment_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"AMD-{year}-"

        last_amd = (
            PurchaseOrderAmendment.objects.filter(tenant=tenant, amendment_number__startswith=prefix)
            .order_by("-amendment_number")
            .select_for_update()
            .first()
        )

        if not last_amd:
            seq = 1
        else:
            try:
                seq = int(last_amd.amendment_number.split("-")[-1]) + 1
            except (ValueError, IndexError):
                seq = 1

        return f"{prefix}{seq:06d}"

    @transaction.atomic
    def generate_quotation_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"QUO-{year}-"

        last_quo = (
            SupplierQuotation.objects.filter(tenant=tenant, quotation_number__startswith=prefix)
            .order_by("-quotation_number")
            .select_for_update()
            .first()
        )

        if not last_quo:
            seq = 1
        else:
            try:
                seq = int(last_quo.quotation_number.split("-")[-1]) + 1
            except (ValueError, IndexError):
                seq = 1

        return f"{prefix}{seq:06d}"
