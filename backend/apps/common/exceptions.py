"""Domain exceptions for PharmaCloud.

Raise these from services / business logic. DRF translates the framework
subclasses automatically; plain ``PharmaCloudError`` is caught and mapped by
the API exception handler.
"""

from __future__ import annotations

from typing import Any


class PharmaCloudError(Exception):
    """Base domain error."""

    status_code: int = 400
    code: str = "error"
    message: str = "An error occurred."
    field: str | None = None

    def __init__(self, message: str | None = None, *, code: str | None = None, field: str | None = None) -> None:
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code
        if field is not None:
            self.field = field
        super().__init__(self.message)

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.field is not None:
            payload["field"] = self.field
        return payload


class BusinessRuleViolation(PharmaCloudError):
    """A business rule was violated (e.g. negative stock, invalid expiry)."""

    status_code = 409
    code = "business_rule_violation"
    message = "Operation violates a business rule."


class ConflictError(PharmaCloudError):
    status_code = 409
    code = "conflict"
    message = "The request conflicts with the current state of the resource."


class NotFoundError(PharmaCloudError):
    status_code = 404
    code = "not_found"
    message = "The requested resource does not exist."


class PermissionDeniedError(PharmaCloudError):
    status_code = 403
    code = "permission_denied"
    message = "You do not have permission to perform this action."


class UnauthorizedError(PharmaCloudError):
    status_code = 401
    code = "unauthorized"
    message = "Authentication credentials are invalid or missing."


class ValidationFailedError(PharmaCloudError):
    status_code = 422
    code = "validation_error"
    message = "The provided data is invalid."


class ExternalServiceError(PharmaCloudError):
    status_code = 502
    code = "external_service_error"
    message = "An upstream dependency failed."


class ServiceUnavailableError(PharmaCloudError):
    status_code = 503
    code = "service_unavailable"
    message = "The service is temporarily unavailable."


class TenantResolutionError(PharmaCloudError):
    status_code = 400
    code = "tenant_resolution_error"
    message = "A valid X-Tenant-ID or X-Tenant-Slug header is required."
