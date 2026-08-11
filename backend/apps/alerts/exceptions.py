"""Domain exceptions for Enterprise Expiry, Recall & Inventory Alert Management."""

from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import APIException


class AlertDomainError(APIException):
    """Base exception for Inventory Alerts domain."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "alert_domain_error"
    default_detail = "An inventory alert error occurred."


class InvalidAlertStateError(AlertDomainError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "invalid_alert_state"
    default_detail = "The alert is in an invalid state for this operation."


class AlertAlreadyResolvedError(AlertDomainError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "alert_already_resolved"
    default_detail = "The alert has already been resolved."


class InvalidRecallStateError(AlertDomainError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "invalid_recall_state"
    default_detail = "The recall is in an invalid state for this operation."


class RecallAlreadyInitiatedError(AlertDomainError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "recall_already_initiated"
    default_detail = "The recall has already been initiated."


class RecallAlreadyCompletedError(AlertDomainError):
    status_code = status.HTTP_409_CONFLICT
    default_code = "recall_already_completed"
    default_detail = "The recall has already been completed."
