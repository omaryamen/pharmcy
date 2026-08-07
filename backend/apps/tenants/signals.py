"""Django signals for Tenant lifecycle events."""

from __future__ import annotations

from django.dispatch import Signal

tenant_provisioned = Signal()
tenant_status_changed = Signal()
tenant_subscription_updated = Signal()
