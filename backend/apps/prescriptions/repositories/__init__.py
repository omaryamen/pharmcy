"""Export repositories for apps.prescriptions."""

from apps.prescriptions.repositories.prescription_repository import (
    PrescriptionDispenseRepository,
    PrescriptionRepository,
)

__all__ = [
    "PrescriptionRepository",
    "PrescriptionDispenseRepository",
]
