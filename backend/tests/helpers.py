"""Shared helpers for the authentication test suite."""

from __future__ import annotations

import re
from contextlib import contextmanager

from django.core import mail

OTP_RE = re.compile(r"\b\d{6}\b")


@contextmanager
def as_request(user=None, tenant=None):
    """Run a block with a synthetic request in the thread-local context.

    Lets service-layer tests exercise the permission guards the way real
    requests do (``get_current_user`` / ``get_current_tenant`` read from this
    context). The request is cleared on exit.
    """
    from apps.common.utils import context as context_utils

    class _FakeRequest:
        pass

    request = _FakeRequest()
    request.user = user
    request.tenant = tenant
    context_utils.set_request(request)
    try:
        yield request
    finally:
        context_utils.clear()


def get_email(to_email: str):
    """Return the most recent outbox message addressed to ``to_email``."""
    for message in reversed(mail.outbox):
        if to_email in message.to:
            return message
    raise AssertionError(f"No email was sent to {to_email}")


def extract_otp(email_message) -> str:
    """Extract the 6-digit verification code from an email body."""
    match = OTP_RE.search(email_message.body or "")
    if match is None:
        raise AssertionError(f"No 6-digit code found in email body: {email_message.body!r}")
    return match.group(0)


def register_and_extract_code(
    api_client,
    *,
    email: str = "register@pharmacloud.test",
    first_name: str = "Register",
    password: str = "StrongPass!123",
) -> str:
    """Register a user via the API and return the emailed verification code."""
    response = api_client.post(
        "/api/v1/auth/register/",
        {"email": email, "first_name": first_name, "password": password},
        format="json",
    )
    assert response.status_code == 201, response.json()
    return extract_otp(get_email(email))
