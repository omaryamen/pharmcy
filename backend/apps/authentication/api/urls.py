"""API routes for the authentication app (mounted under /api/v1/)."""

from __future__ import annotations

from django.urls import path

from .views import (
    ChangePasswordView,
    EmailVerificationConfirmView,
    EmailVerificationRequestView,
    LoginView,
    LogoutView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    PhoneVerificationConfirmView,
    PhoneVerificationRequestView,
    ProfileView,
    RefreshView,
    RegisterView,
    SecurityEventListView,
    SessionListView,
    SessionRevokeAllView,
    SessionRevokeView,
    VerifyTokenView,
)

app_name = "authentication"

urlpatterns = [
    # --- Session (JWT) ---
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/token/", LoginView.as_view(), name="auth-login"),
    path("auth/token/refresh/", RefreshView.as_view(), name="auth-refresh"),
    path("auth/token/verify/", VerifyTokenView.as_view(), name="auth-verify"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    # --- Profile ---
    path("auth/me/", ProfileView.as_view(), name="auth-me"),
    path("auth/profile/", ProfileView.as_view(), name="auth-profile"),
    # --- Email / phone verification ---
    path("auth/email/verify/request/", EmailVerificationRequestView.as_view(), name="auth-email-verify-request"),
    path("auth/email/verify/confirm/", EmailVerificationConfirmView.as_view(), name="auth-email-verify-confirm"),
    path("auth/phone/verify/request/", PhoneVerificationRequestView.as_view(), name="auth-phone-verify-request"),
    path("auth/phone/verify/confirm/", PhoneVerificationConfirmView.as_view(), name="auth-phone-verify-confirm"),
    # --- Password ---
    path("auth/password/reset/request/", PasswordResetRequestView.as_view(), name="auth-password-reset-request"),
    path("auth/password/reset/confirm/", PasswordResetConfirmView.as_view(), name="auth-password-reset-confirm"),
    path("auth/password/change/", ChangePasswordView.as_view(), name="auth-password-change"),
    # --- Session ledger & audit trail ---
    path("auth/sessions/", SessionListView.as_view(), name="auth-sessions"),
    path("auth/sessions/revoke-all/", SessionRevokeAllView.as_view(), name="auth-sessions-revoke-all"),
    path("auth/sessions/<uuid:pk>/revoke/", SessionRevokeView.as_view(), name="auth-session-revoke"),
    path("auth/security/events/", SecurityEventListView.as_view(), name="auth-security-events"),
]
