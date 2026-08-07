"""Django signals for Medicine Master lifecycle events."""

from __future__ import annotations

from django.dispatch import Signal

medicine_created = Signal()
medicine_updated = Signal()
