"""Medicine data validation rules."""

from __future__ import annotations

from rest_framework.exceptions import ValidationError


def validate_price_non_negative(value: float | int) -> float | int:
    if value < 0:
        raise ValidationError("Price cannot be negative.")
    return value
