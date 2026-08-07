"""Django signals for User lifecycle and profile events."""

from __future__ import annotations

from django.dispatch import Signal

user_profile_updated = Signal()
user_status_changed = Signal()
