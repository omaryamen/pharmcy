"""Branch validation rules and helpers."""

from __future__ import annotations

import re

from rest_framework.exceptions import ValidationError

BRANCH_CODE_REGEX = re.compile(r"^[a-z0-9_]+$")


def validate_branch_code(value: str) -> str:
    cleaned = value.lower().strip()
    if not BRANCH_CODE_REGEX.match(cleaned):
        raise ValidationError("Branch code must contain only lowercase letters, numbers, and underscores.")
    return cleaned


def validate_coordinates(latitude: float | None, longitude: float | None) -> None:
    if latitude is not None and not (-90.0 <= float(latitude) <= 90.0):
        raise ValidationError("Latitude must be between -90.0 and 90.0.")
    if longitude is not None and not (-180.0 <= float(longitude) <= 180.0):
        raise ValidationError("Longitude must be between -180.0 and 180.0.")
