"""Celery tasks for identity notifications.

Each task wraps a ``notifications`` builder; the tasks exist so request
handlers can enqueue delivery and never block on SMTP/SMS.
"""

from __future__ import annotations

from celery import shared_task
from django.apps import apps

from . import notifications
from .utils import deliver_phone_code


@shared_task(name="authentication.send_verification_code_email")
def send_verification_code_email_task(user_id, code: str, *, purpose: str = "verify your email address") -> int:
    User = apps.get_model("core", "User")
    user = User.all_objects.get(pk=user_id)
    return notifications.send_verification_code_email(user, code, purpose=purpose)


@shared_task(name="authentication.send_password_reset_code_email")
def send_password_reset_code_email_task(user_id, code: str) -> int:
    User = apps.get_model("core", "User")
    user = User.all_objects.get(pk=user_id)
    return notifications.send_password_reset_code_email(user, code)


@shared_task(name="authentication.send_phone_verification_code")
def send_phone_verification_code_task(user_id, code: str) -> bool:
    """Deliver a phone code via the SMS backend, falling back to email."""
    User = apps.get_model("core", "User")
    user = User.all_objects.get(pk=user_id)
    if deliver_phone_code(user.phone, code):
        return True
    return bool(notifications.send_phone_verification_code(user, code))


@shared_task(name="authentication.send_account_locked_notice")
def send_account_locked_notice_task(user_id) -> int:
    User = apps.get_model("core", "User")
    user = User.all_objects.get(pk=user_id)
    return notifications.send_account_locked_notice_email(user)
