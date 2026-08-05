"""Authentication API views."""

from .auth import LoginView, LogoutView, RefreshView, VerifyTokenView
from .password import ChangePasswordView
from .profile import ProfileView
from .registration import RegisterView
from .security import SecurityEventListView
from .sessions import SessionListView, SessionRevokeAllView, SessionRevokeView
from .verification import (
    EmailVerificationConfirmView,
    EmailVerificationRequestView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    PhoneVerificationConfirmView,
    PhoneVerificationRequestView,
)

__all__ = [
    "ChangePasswordView",
    "EmailVerificationConfirmView",
    "EmailVerificationRequestView",
    "LoginView",
    "LogoutView",
    "PasswordResetConfirmView",
    "PasswordResetRequestView",
    "PhoneVerificationConfirmView",
    "PhoneVerificationRequestView",
    "ProfileView",
    "RefreshView",
    "RegisterView",
    "SecurityEventListView",
    "SessionListView",
    "SessionRevokeAllView",
    "SessionRevokeView",
    "VerifyTokenView",
]
