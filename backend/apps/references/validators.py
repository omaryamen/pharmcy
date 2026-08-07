"""Reference validation rules."""

from __future__ import annotations

import re

from rest_framework.exceptions import ValidationError

CODE_REGEX = re.compile(r"^[A-Za-z0-9_-]+$")


def validate_reference_code(value: str) -> str:
    cleaned = value.strip()
    if not CODE_REGEX.match(cleaned):
        raise ValidationError("Code must contain valid alphanumeric characters, underscores, or hyphens.")
    return cleaned
