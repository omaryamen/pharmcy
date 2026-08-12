"""Domain exception hierarchy for Enterprise Prescription Management & Pharmacy Dispensing."""

from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import APIException


class PrescriptionDomainError(APIException):
    """Base domain exception for prescription operations."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "prescription_domain_error"
    default_detail = "A prescription domain error occurred."


class PrescriptionExpiredError(PrescriptionDomainError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "prescription_expired"
    default_detail = "Prescription has expired and cannot be dispensed."


class PrescriptionNotVerifiedError(PrescriptionDomainError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "prescription_not_verified"
    default_detail = "Prescription must be clinically verified before dispensing."


class ExceedsPrescribedQuantityError(PrescriptionDomainError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "exceeds_prescribed_quantity"
    default_detail = "Dispensed quantity exceeds remaining prescribed limit or refills allowed."


class ControlledSubstanceLicenseRequiredError(PrescriptionDomainError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "controlled_substance_license_required"
    default_detail = "Controlled substance prescription requires valid prescribing doctor license number."


class InvalidPrescriptionStateError(PrescriptionDomainError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "invalid_prescription_state"
    default_detail = "Prescription document is in an invalid status for this operation."
