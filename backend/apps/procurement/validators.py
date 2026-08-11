"""Domain validators for Enterprise Purchasing & Purchase Order Management."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.procurement.exceptions import (
    InactiveMedicineError,
    InactiveSupplierError,
    SelfApprovalForbiddenError,
)


def validate_positive_quantity(value: Decimal | float | int) -> Decimal:
    """Ensure purchase quantity is strictly positive (> 0)."""
    dec_val = Decimal(str(value))
    if dec_val <= Decimal("0"):
        raise ValidationError(_("Quantity must be greater than zero."))
    return dec_val


def validate_non_negative_amount(value: Decimal | float | int) -> Decimal:
    """Ensure monetary amount is non-negative (>= 0)."""
    dec_val = Decimal(str(value))
    if dec_val < Decimal("0"):
        raise ValidationError(_("Monetary amount cannot be negative."))
    return dec_val


def validate_supplier_eligible_for_procurement(supplier: Any, tenant: Any) -> None:
    """Verify that a supplier is active, non-blocked, non-suspended, and belongs to the specified tenant."""
    if not supplier:
        raise InactiveSupplierError(_("Supplier is required."))

    if getattr(supplier, "tenant_id", None) and getattr(supplier, "tenant_id") != getattr(tenant, "id", None):
        raise InactiveSupplierError(_("Supplier does not belong to the active tenant."))

    status_val = getattr(supplier, "status", getattr(supplier, "supplier_status", "active"))
    if status_val in ["inactive", "suspended", "blocked", "blacklisted", "archived"]:
        raise InactiveSupplierError(_("Supplier %s has status '%s' and is ineligible for procurement.") % (getattr(supplier, "legal_name", str(supplier)), status_val))

    if getattr(supplier, "is_blacklisted", False):
        raise InactiveSupplierError(_("Supplier %s is blacklisted.") % getattr(supplier, "legal_name", str(supplier)))


def validate_medicine_eligible_for_procurement(medicine: Any, tenant: Any) -> None:
    """Verify that a medicine is active and eligible for ordering."""
    if not medicine:
        raise InactiveMedicineError(_("Medicine is required."))

    if getattr(medicine, "tenant_id", None) and getattr(medicine, "tenant_id") != getattr(tenant, "id", None):
        raise InactiveMedicineError(_("Medicine does not belong to the active tenant."))

    status_val = getattr(medicine, "status", "active")
    if status_val in ["inactive", "discontinued", "archived", "draft"]:
        raise InactiveMedicineError(_("Medicine %s has status '%s' and is ineligible for procurement.") % (getattr(medicine, "english_name", str(medicine)), status_val))


def validate_po_approval_separation_of_duties(
    created_by: Any, approving_user: Any, is_superuser: bool = False
) -> None:
    """Enforce separation of duties: PO creator cannot approve their own order unless superuser."""
    if is_superuser:
        return
    if created_by and approving_user and getattr(created_by, "id", None) == getattr(approving_user, "id", None):
        raise SelfApprovalForbiddenError(_("Purchase Order creator cannot approve their own Purchase Order."))
