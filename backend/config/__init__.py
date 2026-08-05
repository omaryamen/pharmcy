"""PharmaCloud ERP configuration package."""

from __future__ import annotations

# Make sure the Celery app is loaded when Django starts.
from .celery import app as celery_app

__all__ = ("celery_app",)
