"""User and Employee Profile validation rules."""

from __future__ import annotations

import re

from rest_framework.exceptions import ValidationError

NATIONAL_ID_REGEX = re.compile(r"^[A-Za-z0-9_-]+$")


def validate_national_id(value: str) -> str:
    cleaned = value.strip()
    if cleaned and not NATIONAL_ID_REGEX.match(cleaned):
        raise ValidationError("National ID must contain valid alphanumeric characters.")
    return cleaned
