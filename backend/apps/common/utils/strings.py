"""String and code generation helpers."""

from __future__ import annotations

import random
import string
from secrets import token_hex

from django.utils.text import slugify as _django_slugify


def slugify(value: str, max_length: int = 80) -> str:
    return _django_slugify(value or "")[:max_length].rstrip("-")


def random_code(prefix: str = "", length: int = 8, alphabet: str = string.ascii_uppercase + string.digits) -> str:
    """Human-friendly, unambiguous code (no lookalike chars)."""
    unambiguous = alphabet.replace("O", "").replace("I", "").replace("0", "").replace("1", "")
    return f"{prefix}{''.join(random.choices(unambiguous, k=length))}"


def random_token(byte_length: int = 32) -> str:
    """Cryptographically secure token (API keys, OTPs)."""
    return token_hex(byte_length)
