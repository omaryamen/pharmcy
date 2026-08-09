"""Batch service for managing pharmaceutical lot creation, compliance, and recall status."""

from __future__ import annotations

import logging
from typing import Any

from django.db import transaction

from apps.inventory.exceptions import DuplicateBatchNumberError, InvalidBatchDateError
from apps.inventory.models import Batch, BatchStatus
from apps.inventory.repositories import BatchRepository
from apps.inventory.validators import validate_batch_dates

logger = logging.getLogger(__name__)


class BatchService:
    def __init__(self) -> None:
        self.repository = BatchRepository()

    @transaction.atomic
    def create_batch(
        self,
        tenant,
        company,
        medicine,
        *,
        batch_number: str,
        expiry_date,
        supplier=None,
        lot_number: str = "",
        manufacturing_date=None,
        registration_number: str = "",
        country_of_origin: str = "",
        status: str = "active",
        unit_cost=0.0000,
        selling_price=0.0000,
        initial_quantity=0.00,
        storage_requirements: str = "",
        notes: str = "",
        **extra_fields,
    ) -> Batch:
        clean_batch_num = batch_number.strip()

        # Validate date rules
        validate_batch_dates(manufacturing_date, expiry_date)

        # Validate batch number uniqueness per tenant and medicine
        if self.repository.exists(tenant=tenant, medicine=medicine, batch_number=clean_batch_num):
            raise DuplicateBatchNumberError(
                f"A batch with number '{clean_batch_num}' already exists for medicine '{medicine.english_name}'."
            )

        batch = self.repository.create(
            tenant=tenant,
            company=company,
            medicine=medicine,
            supplier=supplier,
            batch_number=clean_batch_num,
            lot_number=lot_number,
            manufacturing_date=manufacturing_date,
            expiry_date=expiry_date,
            registration_number=registration_number,
            country_of_origin=country_of_origin,
            status=status,
            unit_cost=unit_cost,
            selling_price=selling_price,
            initial_quantity=initial_quantity,
            current_quantity=initial_quantity,
            storage_requirements=storage_requirements,
            notes=notes,
            **extra_fields,
        )

        logger.info("Created batch %s for medicine %s (Exp: %s)", batch.batch_number, medicine.english_name, batch.expiry_date)
        return batch

    @transaction.atomic
    def update_batch(self, batch: Batch, **fields) -> Batch:
        if "manufacturing_date" in fields or "expiry_date" in fields:
            mfg = fields.get("manufacturing_date", batch.manufacturing_date)
            exp = fields.get("expiry_date", batch.expiry_date)
            validate_batch_dates(mfg, exp)

        updated = self.repository.update(batch, **fields)
        logger.info("Updated batch %s for medicine %s", batch.batch_number, batch.medicine.english_name)
        return updated

    @transaction.atomic
    def block_batch(self, batch: Batch) -> Batch:
        batch.block()
        logger.info("Blocked batch %s", batch.batch_number)
        return batch

    @transaction.atomic
    def unblock_batch(self, batch: Batch) -> Batch:
        batch.unblock()
        logger.info("Unblocked batch %s", batch.batch_number)
        return batch

    @transaction.atomic
    def recall_batch(self, batch: Batch) -> Batch:
        batch.recall()
        logger.warning("RECALLED batch %s for medicine %s", batch.batch_number, batch.medicine.english_name)
        return batch

    @transaction.atomic
    def soft_delete_batch(self, batch: Batch) -> Batch:
        self.repository.delete(batch)
        logger.info("Soft deleted batch %s", batch.batch_number)
        return batch
