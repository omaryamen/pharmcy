"""Export views for apps.prescriptions."""

from apps.prescriptions.api.views.dispensation import PrescriptionDispenseViewSet
from apps.prescriptions.api.views.prescription import PrescriptionViewSet

__all__ = [
    "PrescriptionViewSet",
    "PrescriptionDispenseViewSet",
]
