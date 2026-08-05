"""Transactional email notifications for identity flows.

Emails are plain-text by default with a minimal HTML alternative. Delivery is
delegated to Celery tasks (``tasks.py``) so request handlers never block on
SMTP; in tests Celery runs eager and the locmem backend captures messages.
"""

from __future__ import annotations

import html

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse

from apps.core.models import User


def _escape(value: str) -> str:
    return html.escape(str(value))


def _deliver(subject: str, to_email: str, text_body: str, html_body: str | None = None) -> int:
    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    if html_body:
        message.attach_alternative(html_body, "text/html")
    return message.send()


def _email_wrapper(title: str, body_html: str) -> str:
    return (
        "<div style='font-family:Arial,sans-serif;max-width:600px;margin:auto'>"
        f"<h2>{title}</h2>{body_html}"
        "<hr/><p style='color:#888;font-size:12px'>PharmaCloud ERP</p></div>"
    )


def send_verification_code_email(user: User, code: str, *, purpose: str = "verify your email address") -> int:
    """Send the email verification OTP."""
    subject = "Your PharmaCloud verification code"
    text = (
        f"Hi {_escape(user.full_name or user.email)},\n\n"
        f"Your code to {purpose} is: {code}\n"
        f"It expires in {settings.AUTH_VERIFICATION_CODE_LIFETIME_MINUTES} minutes.\n\n"
        "If you did not request this, you can safely ignore this message.\n"
        "PharmaCloud ERP"
    )
    html_body = _email_wrapper(
        "Email verification",
        f"<p>Hi {_escape(user.full_name or user.email)},</p>"
        f"<p>Your code to {_escape(purpose)} is:</p>"
        f"<p style='font-size:28px;font-weight:bold;letter-spacing:4px'>{_escape(code)}</p>"
        f"<p>It expires in {settings.AUTH_VERIFICATION_CODE_LIFETIME_MINUTES} minutes.</p>"
        "<p>If you did not request this, you can safely ignore this message.</p>",
    )
    return _deliver(subject, user.email, text, html_body)


def send_password_reset_code_email(user: User, code: str) -> int:
    """Send the password-reset OTP."""
    subject = "Your PharmaCloud password reset code"
    text = (
        f"Hi {_escape(user.full_name or user.email)},\n\n"
        f"Your password reset code is: {code}\n"
        f"It expires in {settings.AUTH_VERIFICATION_CODE_LIFETIME_MINUTES} minutes.\n\n"
        "If you did not request a password reset, you can safely ignore this "
        "message — your password has not been changed.\n"
        "PharmaCloud ERP"
    )
    html_body = _email_wrapper(
        "Password reset",
        f"<p>Hi {_escape(user.full_name or user.email)},</p>"
        f"<p>Your password reset code is:</p>"
        f"<p style='font-size:28px;font-weight:bold;letter-spacing:4px'>{_escape(code)}</p>"
        f"<p>It expires in {settings.AUTH_VERIFICATION_CODE_LIFETIME_MINUTES} minutes.</p>"
        "<p>If you did not request this, you can safely ignore this message.</p>",
    )
    return _deliver(subject, user.email, text, html_body)


def send_account_locked_notice_email(user: User) -> int:
    """Notify the user their account was locked after failed logins."""
    subject = "Your PharmaCloud account was locked"
    reset_url = ""
    try:
        reset_url = reverse("auth-password-reset-request")
    except Exception:  # noqa: BLE001 - route may not be mounted in admin contexts
        pass
    text = (
        f"Hi {_escape(user.full_name or user.email)},\n\n"
        "Your account was locked because of repeated failed login attempts.\n"
        "You can request a password reset"
        + (f" at {reset_url}" if reset_url else "")
        + " or contact your administrator to unlock it.\n\n"
        "PharmaCloud ERP"
    )
    html_body = _email_wrapper(
        "Account locked",
        f"<p>Hi {_escape(user.full_name or user.email)},</p>"
        "<p>Your account was locked because of repeated failed login attempts.</p>"
        "<p>You can request a password reset or contact your administrator to unlock it.</p>",
    )
    return _deliver(subject, user.email, text, html_body)


def send_phone_verification_code(user: User, code: str) -> int:
    """Fallback channel for phone codes when no SMS backend exists.

    Delivers the code to the user's email so the account can be verified even
    before an SMS provider is configured. Production setups should configure
    ``AUTH_SMS_BACKEND`` instead.
    """
    subject = "Your PharmaCloud phone verification code"
    text = (
        f"Hi {_escape(user.full_name or user.email)},\n\n"
        f"Your phone verification code is: {code}\n"
        f"It expires in {settings.AUTH_VERIFICATION_CODE_LIFETIME_MINUTES} minutes.\n\n"
        "PharmaCloud ERP"
    )
    return _deliver(subject, user.email, text)
