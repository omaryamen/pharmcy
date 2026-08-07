"""Tenant validation rules and helpers."""

from __future__ import annotations

import re

from rest_framework.exceptions import ValidationError

SLUG_REGEX = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DOMAIN_REGEX = re.compile(r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$")


def validate_slug(value: str) -> str:
    cleaned = value.lower().strip()
    if not SLUG_REGEX.match(cleaned):
        raise ValidationError("Slug must consist of lowercase alphanumeric characters and hyphens.")
    if len(cleaned) < 3 or len(cleaned) > 50:
        raise ValidationError("Slug length must be between 3 and 50 characters.")
    return cleaned


def validate_domain_name(value: str) -> str:
    cleaned = value.lower().strip()
    if not DOMAIN_REGEX.match(cleaned) and not cleaned.endswith(".pharmacloud.local"):
        raise ValidationError("Invalid domain name format.")
    return cleaned
