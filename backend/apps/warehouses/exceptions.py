"""Exceptions specific to Enterprise Warehouse & Storage Location Management."""

from __future__ import annotations

from apps.common.exceptions import BusinessRuleViolation, ConflictError, NotFoundError, ValidationFailedError


class WarehouseNotFoundError(NotFoundError):
    code = "warehouse_not_found"
    message = "The requested warehouse record does not exist."


class WarehouseStatusError(BusinessRuleViolation):
    code = "warehouse_status_invalid"
    message = "The operation cannot be performed for the warehouse in its current status."


class DuplicateWarehouseCodeError(ConflictError):
    code = "duplicate_warehouse_code"
    message = "A warehouse with this code already exists in this tenant."


class DuplicateWarehouseNameError(ConflictError):
    code = "duplicate_warehouse_name"
    message = "A warehouse with this name already exists in this company."


class WarehouseDeleteForbiddenError(BusinessRuleViolation):
    code = "warehouse_delete_forbidden"
    message = "Cannot delete warehouse because active storage locations or stock dependencies exist."


class StorageLocationNotFoundError(NotFoundError):
    code = "storage_location_not_found"
    message = "The requested storage location record does not exist."


class DuplicateLocationCodeError(ConflictError):
    code = "duplicate_location_code"
    message = "A storage location with this code already exists in this warehouse."


class CircularLocationHierarchyError(BusinessRuleViolation):
    code = "circular_location_hierarchy"
    message = "A storage location cannot be its own parent or descendant."


class InvalidLocationWarehouseMismatchError(ValidationFailedError):
    code = "location_warehouse_mismatch"
    message = "Parent storage location must belong to the exact same warehouse."


class InvalidWarehouseManagerError(ValidationFailedError):
    code = "invalid_warehouse_manager"
    message = "Assigned manager must be an active user belonging to the same tenant and company."


class StorageLocationDeleteForbiddenError(BusinessRuleViolation):
    code = "storage_location_delete_forbidden"
    message = "Cannot delete storage location because child locations or stock dependencies exist."
