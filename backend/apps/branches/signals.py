"""Django signals for Branch lifecycle events."""

from __future__ import annotations

from django.dispatch import Signal

branch_created = Signal()
branch_status_changed = Signal()
