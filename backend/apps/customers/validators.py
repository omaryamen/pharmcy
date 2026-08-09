"""Validators for Enterprise Customer Management Domain."""

from __future__ import annotations

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

PHONE_REGEX = re.compile(r"^\+?[0-9\s\-()]{7,25}$")


def validate_phone_number(value: str) -> None:
    if value and not PHONE_REGEX.match(value.strip()):
        raise ValidationError(_("Invalid phone number format."))


from apps.customers.exceptions import InvalidCreditLimitError


def validate_credit_limit(value) -> None:
    if value is not None and value < 0:
        raise InvalidCreditLimitError()


def validate_date_range(start_date, end_date, message: str = "Start date must be before end date.") -> None:
    if start_date and end_date and start_date > end_date:
        raise ValidationError(_(message))
