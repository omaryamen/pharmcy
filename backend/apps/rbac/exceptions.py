"""RBAC-specific domain errors.

Subclass ``PharmaCloudError`` so the shared API exception handler and the
envelope renderer translate them consistently. Error codes are stable API
contracts — clients branch on ``code``, never on the message.
"""

from __future__ import annotations

from typing import Iterable

from apps.common.exceptions import PharmaCloudError


class RbacError(PharmaCloudError):
    """Base error for the RBAC module."""

    status_code = 400
    code = "rbac_error"
    message = "Access control error."


class InvalidPermissionCodeError(RbacError):
    status_code = 422
    code = "permission_code_invalid"
    message = "Permission codes must match '<module>.<resource>.<action>'."


class ProtectedRoleError(RbacError):
    status_code = 409
    code = "protected_role"
    message = "Protected roles cannot be modified or removed."


class ProtectedPermissionError(RbacError):
    status_code = 409
    code = "protected_permission"
    message = "System permissions cannot be modified or removed."


class PermissionInUseError(RbacError):
    status_code = 409
    code = "permission_in_use"
    message = "The permission is still referenced by roles or user overrides."


class RoleInUseError(RbacError):
    status_code = 409
    code = "role_in_use"
    message = "The role still has active assignments and cannot be removed."


class CircularInheritanceError(RbacError):
    status_code = 409
    code = "circular_role_inheritance"
    message = "The role hierarchy would create a circular dependency."


class CrossTenantError(RbacError):
    status_code = 422
    code = "cross_tenant_reference"
    message = "Roles and users must belong to the same tenant."


class PrivilegeEscalationError(RbacError):
    status_code = 403
    code = "privilege_escalation"
    message = "You cannot grant permissions you do not possess."

    def __init__(self, missing: Iterable[str] | None = None) -> None:
        if missing:
            codes = ", ".join(sorted(missing))
            super().__init__(f"Missing required permissions: {codes}.", code="privilege_escalation")
        else:
            super().__init__()


class ProtectedAssignmentError(RbacError):
    status_code = 409
    code = "protected_assignment"
    message = "A tenant must always have at least one active administrator."


class RoleAssignmentConflictError(RbacError):
    status_code = 409
    code = "role_assignment_conflict"
    message = "The role assignment is not possible in the current state."


class InactiveRoleError(RbacError):
    status_code = 422
    code = "role_inactive"
    message = "The role is inactive and cannot be assigned."


class MissingRbacPermissionError(RbacError):
    status_code = 403
    code = "missing_permission"
    message = "You do not have the required permission to perform this action."
