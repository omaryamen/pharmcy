"""PharmacyDispensingService orchestrating prescription creation, clinical verification, FEFO batch selection, and stock reduction strictly via StockMovementEngine."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.branches.models import Branch
from apps.companies.models import Company
from apps.customers.models import Customer
from apps.inventory.models import Batch
from apps.medicines.models import Medicine
from apps.prescriptions.exceptions import (
    InvalidPrescriptionStateError,
    PrescriptionNotVerifiedError,
)
from apps.prescriptions.models import (
    DispenseStatus,
    Prescription,
    PrescriptionDispense,
    PrescriptionDispenseLine,
    PrescriptionLine,
    PrescriptionLineStatus,
    PrescriptionStatus,
    PrescriptionType,
)
from apps.prescriptions.repositories import PrescriptionDispenseRepository, PrescriptionRepository
from apps.prescriptions.services.number_generator import PrescriptionNumberGenerator
from apps.prescriptions.validators import (
    validate_controlled_substance_rules,
    validate_dispensing_quantity,
    validate_prescription_validity,
)
from apps.sales.services import FEFOBatchSelector
from apps.stock_movement.models.enums import MovementType, ReferenceType
from apps.stock_movement.services import StockMovementEngine
from apps.warehouses.models import StorageLocation, Warehouse

logger = logging.getLogger(__name__)


class PharmacyDispensingService:
    """Service layer executing prescription verification, clinical safety rules, stock deduction via StockMovementEngine, and dispensing logs."""

    def __init__(
        self,
        prescription_repository: PrescriptionRepository | None = None,
        dispense_repository: PrescriptionDispenseRepository | None = None,
        number_generator: PrescriptionNumberGenerator | None = None,
        stock_movement_engine: StockMovementEngine | None = None,
        fefo_selector: FEFOBatchSelector | None = None,
    ) -> None:
        self.prescription_repository = prescription_repository or PrescriptionRepository()
        self.dispense_repository = dispense_repository or PrescriptionDispenseRepository()
        self.number_generator = number_generator or PrescriptionNumberGenerator()
        self.stock_movement_engine = stock_movement_engine or StockMovementEngine()
        self.fefo_selector = fefo_selector or FEFOBatchSelector()

    @transaction.atomic
    def create_prescription(
        self,
        tenant: Any,
        company: Company,
        branch: Branch,
        customer: Customer,
        rx_date: Any,
        expiry_date: Any,
        doctor_name: str,
        lines_data: list[dict[str, Any]],
        rx_type: str = PrescriptionType.REGULAR,
        doctor_license_number: str = "",
        clinic_hospital_name: str = "",
        diagnosis_code: str = "",
        diagnosis_description: str = "",
        notes: str = "",
        idempotency_key: str = "",
        user: Any | None = None,
    ) -> Prescription:
        """Create a new medical prescription document."""
        if idempotency_key:
            existing = self.prescription_repository.find_by_idempotency_key(tenant, idempotency_key)
            if existing:
                logger.info(f"Duplicate Prescription request suppressed for key: {idempotency_key}")
                return existing

        validate_prescription_validity(expiry_date)
        validate_controlled_substance_rules(rx_type, doctor_license_number)

        rx_num = self.number_generator.generate_rx_number(tenant)

        prescription = self.prescription_repository.create(
            tenant=tenant,
            company=company,
            branch=branch,
            customer=customer,
            rx_number=rx_num,
            rx_date=rx_date,
            expiry_date=expiry_date,
            status=PrescriptionStatus.PENDING_VERIFICATION,
            rx_type=rx_type,
            doctor_name=doctor_name,
            doctor_license_number=doctor_license_number,
            clinic_hospital_name=clinic_hospital_name,
            diagnosis_code=diagnosis_code,
            diagnosis_description=diagnosis_description,
            idempotency_key=idempotency_key,
            notes=notes,
            created_by=user,
        )

        for line_item in lines_data:
            med_id = line_item["medicine_id"]
            med = Medicine.objects.get(pk=med_id, tenant=tenant)

            qty = Decimal(str(line_item.get("prescribed_quantity", "1.0000")))
            refills = int(line_item.get("refills_allowed", 0))

            PrescriptionLine.objects.create(
                tenant=tenant,
                prescription=prescription,
                medicine=med,
                prescribed_quantity=qty,
                dispensed_quantity=Decimal("0.0000"),
                dosage=line_item.get("dosage", ""),
                frequency=line_item.get("frequency", ""),
                duration_days=int(line_item.get("duration_days", 1)),
                instructions=line_item.get("instructions", ""),
                refills_allowed=refills,
                refills_remaining=refills,
                status=PrescriptionLineStatus.PENDING,
                notes=line_item.get("notes", ""),
            )

        logger.info(f"Created Prescription {rx_num} for customer {customer.english_name}")
        return prescription

    @transaction.atomic
    def verify_prescription(self, tenant: Any, prescription: Prescription, pharmacist: Any) -> Prescription:
        """Clinically verify prescription safety and compliance by a licensed pharmacist."""
        rx = Prescription.objects.select_for_update().get(pk=prescription.pk, tenant=tenant)
        if rx.status not in [PrescriptionStatus.PENDING_VERIFICATION, PrescriptionStatus.DRAFT]:
            raise InvalidPrescriptionStateError(f"Cannot verify prescription in status '{rx.status}'.")

        validate_prescription_validity(rx.expiry_date)
        validate_controlled_substance_rules(rx.rx_type, rx.doctor_license_number)

        rx.is_verified = True
        rx.verified_by = pharmacist
        rx.verified_at = timezone.now()
        rx.status = PrescriptionStatus.VERIFIED
        rx.save(update_fields=["is_verified", "verified_by", "verified_at", "status", "updated_at"])

        logger.info(f"Verified Prescription {rx.rx_number} by pharmacist {pharmacist}")
        return rx

    @transaction.atomic
    def dispense_prescription(
        self,
        tenant: Any,
        prescription: Prescription,
        warehouse: Warehouse,
        dispensing_lines: list[dict[str, Any]],
        pharmacist: Any,
        pharmacist_notes: str = "",
    ) -> PrescriptionDispense:
        """Dispense prescription medicines, deducting physical stock strictly through StockMovementEngine."""
        rx = Prescription.objects.select_for_update().get(pk=prescription.pk, tenant=tenant)
        if not rx.is_verified:
            raise PrescriptionNotVerifiedError("Prescription must be clinically verified before dispensing.")
        if rx.status not in [PrescriptionStatus.VERIFIED, PrescriptionStatus.PARTIALLY_DISPENSED]:
            raise InvalidPrescriptionStateError(f"Cannot dispense prescription in status '{rx.status}'.")

        validate_prescription_validity(rx.expiry_date)

        disp_num = self.number_generator.generate_dispense_number(tenant)
        dispensation = self.dispense_repository.create(
            tenant=tenant,
            company=rx.company,
            branch=rx.branch,
            warehouse=warehouse,
            prescription=rx,
            dispense_number=disp_num,
            dispensed_at=timezone.now(),
            status=DispenseStatus.COMPLETED,
            dispensed_by=pharmacist,
            pharmacist_notes=pharmacist_notes,
        )

        all_lines_fully_dispensed = True

        for disp_item in dispensing_lines:
            rx_line_id = disp_item["prescription_line_id"]
            rx_line = PrescriptionLine.objects.select_for_update().get(pk=rx_line_id, prescription=rx, tenant=tenant)

            disp_qty = Decimal(str(disp_item["dispensed_quantity"]))
            validate_dispensing_quantity(disp_qty, rx_line.prescribed_quantity, rx_line.dispensed_quantity)

            storage_location_id = disp_item.get("storage_location_id")
            batch_id = disp_item.get("batch_id")

            if storage_location_id:
                location = StorageLocation.objects.get(pk=storage_location_id, warehouse=warehouse, tenant=tenant)
            else:
                location = warehouse.storage_locations.first()

            if batch_id:
                batch = Batch.objects.get(pk=batch_id, tenant=tenant)
            else:
                selected_batch, _ = self.fefo_selector.select_fefo_batch_for_sale(
                    tenant=tenant, warehouse=warehouse, storage_location=location, medicine=rx_line.medicine, required_quantity=disp_qty
                )
                batch = selected_batch

            unit_price = disp_item.get("unit_price", batch.selling_price)
            unit_price_dec = Decimal(str(unit_price))

            # DEDUCT PHYSICAL STOCK STRICTLY VIA STOCK MOVEMENT ENGINE
            self.stock_movement_engine.create_movement(
                tenant=tenant,
                company=rx.company,
                branch=rx.branch,
                warehouse=warehouse,
                source_warehouse=warehouse,
                source_location=location,
                movement_type=MovementType.SALE,
                medicine=rx_line.medicine,
                batch=batch,
                quantity=disp_qty,
                unit_cost=batch.unit_cost,
                reference_type=ReferenceType.PRESCRIPTION,
                reference_id=str(rx.pk),
                reference_number=rx.rx_number,
                reason=f"Prescription Dispense: {disp_num} (RX: {rx.rx_number})",
                idempotency_key=f"RX-DISP-{rx.pk}-{rx_line.pk}-{dispensation.pk}",
                performed_by=pharmacist,
                auto_process=True,
            )

            PrescriptionDispenseLine.objects.create(
                tenant=tenant,
                dispense=dispensation,
                prescription_line=rx_line,
                medicine=rx_line.medicine,
                batch=batch,
                warehouse=warehouse,
                storage_location=location,
                dispensed_quantity=disp_qty,
                unit_price=unit_price_dec,
                total_price=unit_price_dec * disp_qty,
            )

            rx_line.dispensed_quantity += disp_qty
            if rx_line.dispensed_quantity >= rx_line.prescribed_quantity:
                rx_line.status = PrescriptionLineStatus.DISPENSED
            else:
                rx_line.status = PrescriptionLineStatus.PARTIALLY_DISPENSED
                all_lines_fully_dispensed = False

            rx_line.save(update_fields=["dispensed_quantity", "status", "updated_at"])

        if all_lines_fully_dispensed:
            rx.status = PrescriptionStatus.FULLY_DISPENSED
            rx.dispensed_at = timezone.now()
            rx.dispensed_by = pharmacist
        else:
            rx.status = PrescriptionStatus.PARTIALLY_DISPENSED

        rx.save(update_fields=["status", "dispensed_at", "dispensed_by", "updated_at"])

        logger.info(f"Successfully dispensed Prescription {rx.rx_number} (Dispense: {disp_num})")
        return dispensation

    @transaction.atomic
    def reverse_dispensation(self, tenant: Any, dispense: PrescriptionDispense, pharmacist: Any, reason: str = "") -> PrescriptionDispense:
        """Reverse a prescription dispensing event, restoring physical stock via StockMovementEngine."""
        disp = PrescriptionDispense.objects.select_for_update().get(pk=dispense.pk, tenant=tenant)
        if disp.status != DispenseStatus.COMPLETED:
            raise InvalidPrescriptionStateError(f"Cannot reverse dispense in status '{disp.status}'.")

        rx = disp.prescription

        for line in disp.lines.select_related("medicine", "batch", "warehouse", "storage_location", "prescription_line"):
            # RESTORE STOCK VIA COMPENSATING STOCK MOVEMENT
            self.stock_movement_engine.create_movement(
                tenant=tenant,
                company=disp.company,
                branch=disp.branch,
                warehouse=line.warehouse,
                destination_warehouse=line.warehouse,
                destination_location=line.storage_location,
                movement_type=MovementType.SALE_RETURN,
                medicine=line.medicine,
                batch=line.batch,
                quantity=line.dispensed_quantity,
                unit_cost=line.batch.unit_cost,
                reference_type=ReferenceType.PRESCRIPTION,
                reference_id=str(rx.pk),
                reference_number=disp.dispense_number,
                reason=f"Dispensation Reversal: {reason}",
                idempotency_key=f"RX-REV-{disp.pk}-{line.pk}",
                performed_by=pharmacist,
                auto_process=True,
            )

            rx_line = line.prescription_line
            rx_line.dispensed_quantity -= line.dispensed_quantity
            if rx_line.dispensed_quantity <= Decimal("0.0000"):
                rx_line.status = PrescriptionLineStatus.PENDING
            else:
                rx_line.status = PrescriptionLineStatus.PARTIALLY_DISPENSED
            rx_line.save(update_fields=["dispensed_quantity", "status", "updated_at"])

        disp.status = DispenseStatus.REVERSED
        disp.save(update_fields=["status", "updated_at"])

        rx.status = PrescriptionStatus.VERIFIED
        rx.save(update_fields=["status", "updated_at"])

        logger.info(f"Reversed PrescriptionDispense {disp.dispense_number} by {pharmacist}")
        return disp
