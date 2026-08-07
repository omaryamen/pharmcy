"""Django signals for Reference Data lifecycle events."""

from __future__ import annotations

from django.dispatch import Signal

reference_data_changed = Signal()
