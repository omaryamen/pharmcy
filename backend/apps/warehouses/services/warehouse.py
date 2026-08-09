"""Warehouse service managing warehouse lifecycle, defaults, and manager assignments."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from django.db import transaction

from apps.warehouses.exceptions import (
    DuplicateWarehouseCodeError,
    DuplicateWarehouseNameError,
    WarehouseDeleteForbiddenError,
    WarehouseNotFoundError,
)
from apps.warehouses.models import Warehouse, WarehouseStatus
from apps.warehouses.repositories import WarehouseRepository
from apps.warehouses.validators import validate_warehouse_manager

logger = logging.getLogger(__name__)


class WarehouseService:
    def __init__(self) -> None:
        self.repository = WarehouseRepository()

    @transaction.atomic
    def create_warehouse(
        self,
        tenant,
        company,
        *,
        code: str | None = None,
        name: str,
        arabic_name: str = "",
        english_name: str = "",
        description: str = "",
        branch=None,
        warehouse_type: str = "main",
        manager=None,
        phone: str = "",
        email: str = "",
        address: str = "",
        country: str = "Yemen",
        city: str = "Sanaa",
        district: str = "",
        postal_code: str = "",
        latitude=None,
        longitude=None,
        working_hours: str = "",
        is_default_receiving: bool = False,
        is_default_returns: bool = False,
        is_default_quarantine: bool = False,
        is_default_damaged: bool = False,
        is_default_cold: bool = False,
        notes: str = "",
        **extra_fields,
    ) -> Warehouse:
        clean_code = code.lower().strip() if code else f"wh-{uuid.uuid4().hex[:8]}"
        clean_name = name.strip()

        # Validate code uniqueness within tenant
        if self.repository.exists(tenant=tenant, code=clean_code):
            raise DuplicateWarehouseCodeError(f"A warehouse with code '{clean_code}' already exists in this tenant.")

        # Validate name uniqueness within company
        if self.repository.exists(tenant=tenant, company=company, name=clean_name):
            raise DuplicateWarehouseNameError(f"A warehouse with name '{clean_name}' already exists in this company.")

        # Validate manager user account
        validate_warehouse_manager(manager, tenant, company)

        warehouse = self.repository.create(
            tenant=tenant,
            company=company,
            branch=branch,
            code=clean_code,
            name=clean_name,
            arabic_name=arabic_name,
            english_name=english_name,
            description=description,
            warehouse_type=warehouse_type,
            status=WarehouseStatus.ACTIVE,
            manager=manager,
            phone=phone,
            email=email,
            address=address,
            country=country,
            city=city,
            district=district,
            postal_code=postal_code,
            latitude=latitude,
            longitude=longitude,
            working_hours=working_hours,
            is_default_receiving=is_default_receiving,
            is_default_returns=is_default_returns,
            is_default_quarantine=is_default_quarantine,
            is_default_damaged=is_default_damaged,
            is_default_cold=is_default_cold,
            notes=notes,
            **extra_fields,
        )

        logger.info("Created warehouse %s (%s) for company %s", warehouse.display_name, warehouse.code, getattr(company, "legal_name", str(company)))
        return warehouse

    @transaction.atomic
    def update_warehouse(self, warehouse: Warehouse, **fields) -> Warehouse:
        if "manager" in fields:
            validate_warehouse_manager(fields["manager"], warehouse.tenant, warehouse.company)

        updated = self.repository.update(warehouse, **fields)
        logger.info("Updated warehouse %s", warehouse.code)
        return updated

    @transaction.atomic
    def activate_warehouse(self, warehouse: Warehouse) -> Warehouse:
        warehouse.activate()
        logger.info("Activated warehouse %s", warehouse.code)
        return warehouse

    @transaction.atomic
    def deactivate_warehouse(self, warehouse: Warehouse) -> Warehouse:
        warehouse.deactivate()
        logger.info("Deactivated warehouse %s", warehouse.code)
        return warehouse

    @transaction.atomic
    def suspend_warehouse(self, warehouse: Warehouse) -> Warehouse:
        warehouse.suspend()
        logger.info("Suspended warehouse %s", warehouse.code)
        return warehouse

    @transaction.atomic
    def close_temporarily_warehouse(self, warehouse: Warehouse) -> Warehouse:
        warehouse.close_temporarily()
        logger.info("Closed temporarily warehouse %s", warehouse.code)
        return warehouse

    @transaction.atomic
    def restore_warehouse(self, warehouse: Warehouse) -> Warehouse:
        warehouse.restore()
        logger.info("Restored warehouse %s", warehouse.code)
        return warehouse

    @transaction.atomic
    def soft_delete_warehouse(self, warehouse: Warehouse) -> Warehouse:
        # Check active locations
        has_locations = warehouse.locations.filter(is_deleted=False).exists()
        if has_locations:
            raise WarehouseDeleteForbiddenError("Cannot delete warehouse containing active storage locations.")

        self.repository.delete(warehouse)
        logger.info("Soft deleted warehouse %s", warehouse.code)
        return warehouse

    @transaction.atomic
    def assign_manager(self, warehouse: Warehouse, manager) -> Warehouse:
        validate_warehouse_manager(manager, warehouse.tenant, warehouse.company)
        warehouse.manager = manager
        warehouse.save(update_fields=["manager", "updated_at"])
        logger.info("Assigned manager %s to warehouse %s", getattr(manager, "username", "None"), warehouse.code)
        return warehouse
