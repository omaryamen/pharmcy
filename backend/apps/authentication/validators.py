"""Authentication validators: password strength and code format."""

from __future__ import annotations

from django.contrib.auth.password_validation import validate_password as django_validate_password
from django.core.exceptions import ValidationError

from apps.common.exceptions import ValidationFailedError


def validate_password_strength(password: str, user=None) -> str:
    """Run Django's configured password validators against ``password``.

    Raises ``ValidationFailedError`` (422) with a human-readable message when
    the password fails any configured validator.
    """
    try:
        django_validate_password(password, user=user)
    except ValidationError as exc:
        messages = [str(error.message) for error in exc.error_list]
        raise ValidationFailedError(
            " ".join(messages),
            code="weak_password",
            field="password",
        ) from exc
    return password


def validate_verification_code(code: str, *, length: int) -> str:
    """Ensure ``code`` looks like a numeric verification code of ``length``."""
    if not code.isdigit() or len(code) != length:
        raise ValidationFailedError(
            f"The verification code must be {length} digits.",
            code="invalid_verification_code_format",
            field="code",
        )
    return code
