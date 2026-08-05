"""Authentication-specific domain errors.

Subclass ``PharmaCloudError`` so the API exception handler and the response
envelope translate them consistently. Error codes are stable API contracts —
clients should branch on ``code``, never on the human-readable message.
"""

from __future__ import annotations

from apps.common.exceptions import PharmaCloudError


class AuthError(PharmaCloudError):
    """Base error for the authentication module."""

    status_code = 400
    code = "auth_error"
    message = "Authentication error."


class InvalidCredentialsError(AuthError):
    """Email/password mismatch or unknown account.

    Identical for existing and non-existing accounts so the response does not
    enumerate which emails are registered.
    """

    status_code = 401
    code = "invalid_credentials"
    message = "Invalid email or password."


class AccountLockedError(AuthError):
    status_code = 423
    code = "account_locked"
    message = "Account is locked due to repeated failed login attempts."


class AccountInactiveError(AuthError):
    status_code = 403
    code = "account_inactive"
    message = "This account is inactive."


class EmailNotVerifiedError(AuthError):
    status_code = 403
    code = "email_not_verified"
    message = "Email address has not been verified yet."


class EmailAlreadyVerifiedError(AuthError):
    status_code = 409
    code = "email_already_verified"
    message = "Email address is already verified."


class InvalidVerificationCodeError(AuthError):
    status_code = 400
    code = "invalid_verification_code"
    message = "The verification code is invalid or has expired."


class TooManyVerificationAttemptsError(AuthError):
    status_code = 429
    code = "too_many_verification_attempts"
    message = "Too many verification attempts. Request a new code."


class InvalidTokenError(AuthError):
    status_code = 401
    code = "invalid_token"
    message = "The token is invalid or has expired."


class TokenRevokedError(AuthError):
    status_code = 401
    code = "token_revoked"
    message = "The token has been revoked."


class IncorrectCurrentPasswordError(AuthError):
    status_code = 400
    code = "incorrect_current_password"
    message = "The current password is incorrect."
    field = "current_password"


class PasswordReuseError(AuthError):
    status_code = 422
    code = "password_reuse"
    message = "The new password matches a recently used password."
    field = "new_password"
