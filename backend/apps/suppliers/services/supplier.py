"""Supplier service managing supplier profiles, vendor onboarding, and compliance lifecycle."""

from __future__ import annotations

import logging

from django.db import transaction

from apps.suppliers.exceptions import (
    DuplicateSupplierCodeError,
    DuplicateSupplierLegalNameError,
    SupplierDeleteForbiddenError,
)
from apps.suppliers.models import Supplier, SupplierStatus
from apps.suppliers.repositories import SupplierRepository

logger = logging.getLogger(__name__)


class SupplierService:
    def __init__(self) -> None:
        self.repository = SupplierRepository()

    @transaction.atomic
    def create_supplier(
        self,
        tenant,
        *,
        code: str,
        legal_name: str,
        display_name: str = "",
        company=None,
        supplier_type: str = "distributor",
        supplier_category: str = "Pharmaceuticals",
        registration_number: str = "",
        tax_number: str = "",
        vat_number: str = "",
        email: str = "",
        phone: str = "",
        mobile: str = "",
        country: str = "Yemen",
        city: str = "Sanaa",
        default_currency: str = "YER",
        payment_terms: str = "Net 30",
        credit_limit=0.00,
        **extra_fields,
    ) -> Supplier:
        clean_code = code.lower().strip()
        clean_legal_name = legal_name.strip()
        clean_display_name = display_name.strip() or clean_legal_name

        if self.repository.exists(tenant=tenant, code=clean_code):
            raise DuplicateSupplierCodeError(f"A supplier with code '{clean_code}' already exists in this tenant.")
        if self.repository.exists(tenant=tenant, legal_name=clean_legal_name):
            raise DuplicateSupplierLegalNameError(f"A supplier with legal name '{clean_legal_name}' already exists in this tenant.")

        supplier = self.repository.create(
            tenant=tenant,
            company=company,
            code=clean_code,
            legal_name=clean_legal_name,
            display_name=clean_display_name,
            supplier_type=supplier_type,
            supplier_category=supplier_category,
            registration_number=registration_number,
            tax_number=tax_number,
            vat_number=vat_number,
            email=email,
            phone=phone,
            mobile=mobile,
            country=country,
            city=city,
            default_currency=default_currency,
            payment_terms=payment_terms,
            credit_limit=credit_limit,
            status=SupplierStatus.ACTIVE,
            **extra_fields,
        )

        logger.info("Created supplier %s (%s) for tenant %s", supplier.display_name, supplier.code, tenant.slug)
        return supplier

    @transaction.atomic
    def update_supplier(self, supplier: Supplier, **fields) -> Supplier:
        return self.repository.update(supplier, **fields)

    @transaction.atomic
    def activate_supplier(self, supplier: Supplier) -> Supplier:
        supplier.activate()
        logger.info("Activated supplier %s", supplier.code)
        return supplier

    @transaction.atomic
    def suspend_supplier(self, supplier: Supplier) -> Supplier:
        supplier.suspend()
        logger.info("Suspended supplier %s", supplier.code)
        return supplier

    @transaction.atomic
    def blacklist_supplier(self, supplier: Supplier) -> Supplier:
        supplier.blacklist()
        logger.info("Blacklisted supplier %s", supplier.code)
        return supplier

    @transaction.atomic
    def restore_supplier(self, supplier: Supplier) -> Supplier:
        supplier.restore()
        logger.info("Restored supplier %s", supplier.code)
        return supplier

    @transaction.atomic
    def soft_delete_supplier(self, supplier: Supplier) -> Supplier:
        # Dependency check for active POs, Invoices, Payments, Inventory Transactions
        has_pos = getattr(supplier, "purchase_orders", None) and supplier.purchase_orders.filter(is_deleted=False).exists()
        has_invoices = getattr(supplier, "invoices", None) and supplier.invoices.filter(is_deleted=False).exists()
        has_payments = getattr(supplier, "payments", None) and supplier.payments.filter(is_deleted=False).exists()

        if has_pos or has_invoices or has_payments:
            raise SupplierDeleteForbiddenError("Cannot delete supplier linked to active purchase orders, invoices, or payments.")

        self.repository.delete(supplier)
        logger.info("Soft deleted supplier %s", supplier.code)
        return supplier

    @transaction.atomic
    def bulk_import_suppliers(self, tenant, company, items: list[dict]) -> dict:
        created_count = 0
        errors: list[dict] = []

        for idx, item in enumerate(items):
            try:
                self.create_supplier(
                    tenant=tenant,
                    company=company,
                    code=item["code"],
                    legal_name=item["legal_name"],
                    display_name=item.get("display_name", ""),
                    supplier_type=item.get("supplier_type", "distributor"),
                    email=item.get("email", ""),
                    phone=item.get("phone", ""),
                    country=item.get("country", "Yemen"),
                    city=item.get("city", "Sanaa"),
                )
                created_count += 1
            except Exception as exc:  # noqa: BLE001 - collect import failures
                errors.append({"row": idx + 1, "code": item.get("code", ""), "error": str(exc)})

        return {"created": created_count, "errors": errors}
