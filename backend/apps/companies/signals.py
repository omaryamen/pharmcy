"""Django signals for Company lifecycle events."""

from __future__ import annotations

from django.dispatch import Signal

company_created = Signal()
company_status_changed = Signal()
