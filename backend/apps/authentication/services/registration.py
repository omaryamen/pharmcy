"""Registration service: self-service account creation."""

from __future__ import annotations

from django.conf import settings
from django.db import transaction

from apps.common.exceptions import ConflictError
from apps.core.models import User, UserStatus

from ..models import SecurityEventType
from ..repositories import PasswordHistoryRepository, SecurityEventRepository
from ..validators import validate_password_strength
from .events import record_event
from .verification import issue_verification_code


class RegistrationService:
    """Create a new account and, when email verification is enforced, issue
    the initial verification code."""

    def __init__(
        self,
        password_repository: PasswordHistoryRepository | None = None,
        event_repository: SecurityEventRepository | None = None,
    ) -> None:
        self.passwords = password_repository or PasswordHistoryRepository()
        self.events = event_repository or SecurityEventRepository()

    @transaction.atomic
    def register(
        self,
        *,
        email: str,
        first_name: str,
        last_name: str = "",
        phone: str = "",
        password: str,
        request=None,
    ) -> dict:
        email = (email or "").strip().lower()
        if not email:
            from apps.common.exceptions import ValidationFailedError

            raise ValidationFailedError("An email address is required.", code="email_required", field="email")

        # Include soft-deleted rows: the email unique constraint covers them.
        if User.all_objects.filter(email__iexact=email).exists():
            raise ConflictError("An account with this email already exists.", code="email_taken", field="email")

        validate_password_strength(password)

        user = User.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            password=password,
            status=(UserStatus.PENDING_VERIFICATION if settings.AUTH_VERIFY_EMAIL_REQUIRED else UserStatus.ACTIVE),
            email_verified=not settings.AUTH_VERIFY_EMAIL_REQUIRED,
        )

        # Seed the history window so an initial password cannot be reused.
        self.passwords.record(user, password)
        record_event(self.events, user=user, event_type=SecurityEventType.REGISTERED, request=request)

        verification = None
        if settings.AUTH_VERIFY_EMAIL_REQUIRED:
            from ..models import VerificationTokenKind
            from ..repositories import VerificationTokenRepository

            verification = issue_verification_code(
                VerificationTokenRepository(),
                user,
                VerificationTokenKind.EMAIL_VERIFICATION,
                request=request,
            )

        return {
            "user": user,
            "verification_sent": verification is not None,
        }
