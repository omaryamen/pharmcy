"""Supplier data validation rules."""

from __future__ import annotations

import re

from rest_framework.exceptions import ValidationError

IBAN_REGEX = re.compile(r"^[A-Za-z0-9]{15,34}$")
SWIFT_REGEX = re.compile(r"^[A-Za-z0-9]{8,11}$")


def validate_iban(value: str) -> str:
    cleaned = value.replace(" ", "").upper()
    if cleaned and not IBAN_REGEX.match(cleaned):
        raise ValidationError("IBAN format is invalid.")
    return cleaned


def validate_swift(value: str) -> str:
    cleaned = value.strip().upper()
    if cleaned and not SWIFT_REGEX.match(cleaned):
        raise ValidationError("SWIFT/BIC code format is invalid.")
    return cleaned
