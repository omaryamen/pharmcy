"""Domain validators for Enterprise Expiry, Recall & Inventory Alert Management."""

from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.alerts.exceptions import InvalidAlertStateError, InvalidRecallStateError


def validate_alert_can_be_acknowledged(alert: Any) -> None:
    """Verify that an alert can be acknowledged."""
    if not alert:
        raise InvalidAlertStateError(_("Alert does not exist."))
    if alert.status in ["resolved", "dismissed"]:
        raise InvalidAlertStateError(_("Cannot acknowledge an alert that is already resolved or dismissed."))


def validate_alert_can_be_resolved(alert: Any) -> None:
    """Verify that an alert can be resolved."""
    if not alert:
        raise InvalidAlertStateError(_("Alert does not exist."))
    if alert.status == "resolved":
        raise InvalidAlertStateError(_("Alert is already resolved."))


def validate_recall_can_be_initiated(recall: Any) -> None:
    """Verify that a recall order can be initiated."""
    if not recall:
        raise InvalidRecallStateError(_("Batch recall order does not exist."))
    if recall.status not in ["draft"]:
        raise InvalidRecallStateError(_("Recall order is not in draft status."))
