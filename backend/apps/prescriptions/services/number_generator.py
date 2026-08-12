"""Sequence number generator for prescriptions and pharmacy dispensations."""

from __future__ import annotations

import logging
from typing import Any

from django.utils import timezone

from apps.prescriptions.models import Prescription, PrescriptionDispense

logger = logging.getLogger(__name__)


class PrescriptionNumberGenerator:
    """Generates unique RX-YYYY-XXXXXX and DISP-YYYY-XXXXXX sequence document numbers."""

    def generate_rx_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"RX-{year}-"
        last = (
            Prescription.objects.filter(tenant=tenant, rx_number__startswith=prefix)
            .order_by("-rx_number")
            .first()
        )
        if last and last.rx_number:
            try:
                seq_str = last.rx_number.rsplit("-", 1)[-1]
                seq = int(seq_str) + 1
            except ValueError:
                seq = 1
        else:
            seq = 1
        return f"{prefix}{seq:06d}"

    def generate_dispense_number(self, tenant: Any) -> str:
        year = timezone.now().year
        prefix = f"DISP-{year}-"
        last = (
            PrescriptionDispense.objects.filter(tenant=tenant, dispense_number__startswith=prefix)
            .order_by("-dispense_number")
            .first()
        )
        if last and last.dispense_number:
            try:
                seq_str = last.dispense_number.rsplit("-", 1)[-1]
                seq = int(seq_str) + 1
            except ValueError:
                seq = 1
        else:
            seq = 1
        return f"{prefix}{seq:06d}"
