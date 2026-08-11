"""Domain validators for Enterprise Goods Receipt & Receiving Management."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.goods_receipt.exceptions import ExpiryValidationError, OverReceivingPolicyError


def validate_batch_expiry(expiry_date: Any, manufacturing_date: Any | None = None) -> None:
    """Validate that expiry date is in the future and after manufacturing date."""
    if not expiry_date:
        raise ExpiryValidationError(_("Batch expiry date is required."))

    today = timezone.now().date()
    if expiry_date <= today:
        raise ExpiryValidationError(_("Cannot receive expired batch (Expiry date: %s).") % expiry_date)

    if manufacturing_date and expiry_date <= manufacturing_date:
        raise ExpiryValidationError(_("Expiry date (%s) must be after manufacturing date (%s).") % (expiry_date, manufacturing_date))


def validate_over_receiving_tolerance(
    ordered_quantity: Decimal,
    previously_received: Decimal,
    current_received: Decimal,
    tolerance_percentage: Decimal = Decimal("0.00"),
) -> None:
    """Verify that receiving quantity does not exceed PO ordered quantity beyond tolerance."""
    remaining = max(Decimal("0.0000"), ordered_quantity - previously_received)
    max_allowed = remaining * (Decimal("1.00") + (tolerance_percentage / Decimal("100.00")))

    if current_received > max_allowed:
        raise OverReceivingPolicyError(
            _("Receiving quantity %s exceeds remaining PO quantity %s (Max allowed with %s%% tolerance: %s).")
            % (current_received, remaining, tolerance_percentage, max_allowed)
        )


def validate_cold_chain_temperature(
    temp_at_receipt: Decimal | float | None,
    min_temp: Decimal | float | None,
    max_temp: Decimal | float | None,
) -> bool:
    """Return True if temperature excursion occurred."""
    if temp_at_receipt is None or min_temp is None or max_temp is None:
        return False

    temp = Decimal(str(temp_at_receipt))
    min_t = Decimal(str(min_temp))
    max_t = Decimal(str(max_temp))

    return temp < min_t or temp > max_t
