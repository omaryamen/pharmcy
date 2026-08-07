"""Company validation rules and helpers."""

from __future__ import annotations

import re

from rest_framework.exceptions import ValidationError

COMPANY_CODE_REGEX = re.compile(r"^[a-z0-9_]+$")


def validate_company_code(value: str) -> str:
    cleaned = value.lower().strip()
    if not COMPANY_CODE_REGEX.match(cleaned):
        raise ValidationError("Company code must contain only lowercase letters, numbers, and underscores.")
    return cleaned


def validate_tax_number(value: str) -> str:
    cleaned = value.strip()
    if cleaned and len(cleaned) < 5:
        raise ValidationError("Tax registration number must be at least 5 characters long.")
    return cleaned
