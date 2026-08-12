"""Domain validators for Enterprise Prescription Management & Pharmacy Dispensing."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.prescriptions.exceptions import (
    ControlledSubstanceLicenseRequiredError,
    ExceedsPrescribedQuantityError,
    PrescriptionExpiredError,
)
from apps.prescriptions.models.enums import PrescriptionType


def validate_prescription_validity(expiry_date: Any) -> None:
    """Ensure prescription has not passed its expiration date."""
    today = timezone.now().date()
    if expiry_date < today:
        raise PrescriptionExpiredError(_("Prescription expired on %s.") % expiry_date)


def validate_controlled_substance_rules(rx_type: str, doctor_license_number: str) -> None:
    """Enforce controlled substance regulations (doctor license number required)."""
    controlled_types = [
        PrescriptionType.CONTROLLED_CLASS_A,
        PrescriptionType.CONTROLLED_CLASS_B,
        PrescriptionType.NARCOTIC,
    ]
    if rx_type in controlled_types and not doctor_license_number.strip():
        raise ControlledSubstanceLicenseRequiredError(
            _("Prescription of type '%s' requires a valid doctor license number.") % rx_type
        )


def validate_dispensing_quantity(
    requested_quantity: Decimal | float | int,
    prescribed_quantity: Decimal | float | int,
    previously_dispensed_quantity: Decimal | float | int,
) -> Decimal:
    """Ensure requested dispensing quantity does not exceed remaining prescribed quantity."""
    req = Decimal(str(requested_quantity))
    prescribed = Decimal(str(prescribed_quantity))
    prev = Decimal(str(previously_dispensed_quantity))
    remaining = prescribed - prev

    if req > remaining:
        raise ExceedsPrescribedQuantityError(
            _("Requested quantity (%s) exceeds remaining prescribed quantity (%s).") % (req, remaining)
        )
    return remaining
