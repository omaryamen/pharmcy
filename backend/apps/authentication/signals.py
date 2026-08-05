"""Model signal wiring for identity lifecycle.

Services are the primary policy owner; these signals act as defense-in-depth
so that model-level changes made outside services (admin shell, migrations,
bulk updates) still produce audit events and immediately revoke live sessions.

Rules enforced here:
- status transitions log ``ACCOUNT_*`` events and, on lock / deactivation,
  revoke every active session (blacklisting the underlying refresh tokens);
- soft-deleting a user revokes every active session too.
"""

from __future__ import annotations

from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from apps.core.models import User, UserStatus

from .models import LoginSession, SecurityEvent, SecurityEventType, SessionRevokeReason

# Status -> audit event recorded for that transition (PENDING is set at
# registration time and is covered by the registration service).
_STATUS_TRANSITION_EVENTS = {
    UserStatus.LOCKED: SecurityEventType.ACCOUNT_LOCKED,
    UserStatus.INACTIVE: SecurityEventType.ACCOUNT_DEACTIVATED,
    UserStatus.ACTIVE: SecurityEventType.ACCOUNT_ACTIVATED,
}


def _revoke_active_sessions(user: User, reason: str = SessionRevokeReason.SECURITY) -> None:
    """Revoke and blacklist every live session for ``user``."""
    from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

    sessions = list(LoginSession.objects.filter(user=user, is_active=True))
    now = timezone.now()
    for session in sessions:
        session.is_active = False
        session.revoked_at = now
        session.revoked_reason = reason
        session.save(update_fields=["is_active", "revoked_at", "revoked_reason", "updated_at"])
        outstanding = OutstandingToken.objects.filter(jti=session.refresh_token_jti).first()
        if outstanding is not None:
            BlacklistedToken.objects.get_or_create(token=outstanding)


@receiver(pre_save, sender=User)
def record_status_transitions(sender, instance: User, **kwargs) -> None:
    if instance.pk is None:
        return
    try:
        previous = User.all_objects.get(pk=instance.pk)
    except User.DoesNotExist:
        return
    if previous.status == instance.status:
        return

    event_type = _STATUS_TRANSITION_EVENTS.get(instance.status)
    if event_type is not None:
        SecurityEvent.record(
            user=instance,
            event_type=event_type,
            details={"previous_status": previous.status},
        )

    if instance.status in (UserStatus.LOCKED, UserStatus.INACTIVE):
        _revoke_active_sessions(instance)


@receiver(post_save, sender=User)
def revoke_sessions_on_soft_delete(sender, instance: User, **kwargs) -> None:
    if getattr(instance, "is_deleted", False):
        _revoke_active_sessions(instance)


@receiver(post_delete, sender=User)
def revoke_sessions_on_hard_delete(sender, instance: User, **kwargs) -> None:
    # During hard delete the row is gone but FKs are still resolvable for the
    # in-memory instance; revoke any sessions that survived the cascade.
    LoginSession.objects.filter(user_id=instance.pk, is_active=True).update(
        is_active=False,
        revoked_at=timezone.now(),
        revoked_reason=SessionRevokeReason.SECURITY,
        updated_at=timezone.now(),
    )
